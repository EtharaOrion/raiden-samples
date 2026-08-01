# TRUTH: 366d3cf5-0a51-44ea-b43a-3c0d7276c963

## Problem

Implement a single executable `aws` on `$PATH` that emulates the subset of the real `aws dynamodb` CLI needed for `create-table`, `delete-item`, `delete-table`, and `put-item`, dispatching on `argv[1]=="dynamodb"` and `argv[2]` as the subcommand. The program must talk to a real DynamoDB-compatible endpoint (already configured via environment variables — endpoint URL, region, credentials) using whatever AWS SDK or raw HTTP signing mechanism is available in the image, must preserve state consistency across a sequence of commands (create → put → get → query → delete, etc.), and must produce AWS-CLI-shaped JSON output on success and AWS-CLI-shaped error lines on failure, using only the documented exit-code set.

## Behavioral contract

- Invocation form: `aws dynamodb <subcommand> [--flag value ...]`.
- Success: DynamoDB JSON response written to stdout only (valid JSON, parseable by `json.loads`); stderr empty; exit `0`.
- Failure: nothing on stdout; a single human-readable line on stderr identifying the error class (either the AWS envelope form `An error occurred (<ErrorCode>) ...`, a bare `<ErrorCode>: <message>` form, or a client-side usage line like `usage:`/`Parameter validation failed:`/`Unknown options:`); no raw stack trace ever; exit code from `{0,1,252,254,255}` with the general convention:
  - `252` = usage/parsing error (missing required flag, unknown flag, duplicate flag, malformed/empty value, oversized value beyond what the service would accept as a parameter, invalid JSON in a flag that is validated client-side before the request is sent)
  - `254` = service returned a modeled exception (`ResourceNotFoundException`, `ResourceInUseException`, `ConditionalCheckFailedException`, `ValidationException`, etc.) — this is what happens for most "table doesn't exist" / "table already exists" / condition-failure scenarios, and notably for the *first* successful-looking `create-table` in a two-command sequence where the harness expects 254 because the table already exists from prior test setup (see error case table — a bare valid `create-table --table-name X` case is listed as exit 254, implying pre-existing/duplicate table state).
  - `1`/`255` also acceptable general/application-error codes per spec but tests only assert `returncode != 0` for failures.
- Must NOT: shell out to real `aws` CLI or import `awscli`, override endpoint/region/credentials in code (must read from env as already set), fabricate non-upstream flags, client-side validate table names (leave that to the service → `ValidationException`).
- Numbers in Item/Key AttributeValue maps are DynamoDB's `{"N": "5"}` string-encoded form — this is a pass-through property of the JSON given by the caller, not something the program computes, but the program must not mangle it (e.g., no premature JSON→native→JSON round-trip that turns numeric strings into floats).

## Solution decomposition

1. **Command routing**: parse `argv[1]` == `"dynamodb"`, `argv[2]` = subcommand in `{create-table, delete-item, delete-table, put-item}`; anything else → usage error exit 252.
2. **Flag table per subcommand**: an explicit allow-list of documented flags mapped to the DynamoDB API field name and expected value kind (plain string, JSON blob, shorthand list e.g. `AttributeName=id,AttributeType=S`). Unknown flags, duplicate flags, flags with a value starting with another `--` (empty/missing value), and missing required flags (`--table-name`, and `--key`/`--item` where applicable) must all be caught before any network call and exit 252.
3. **Value marshalling**:
   - JSON-typed flags (`--key`, `--item`, `--expected`, `--expression-attribute-names`, `--expression-attribute-values`, etc.) must be `json.loads`'d; invalid JSON → 252.
   - `--attribute-definitions` and `--key-schema` accept either JSON or AWS CLI shorthand (`AttributeName=x,AttributeType=S`); both forms must be supported since the observed argv patterns include both.
   - `--provisioned-throughput`, `--on-demand-throughput`, `--tags`, `--warm-throughput`, `--sse-specification`, `--stream-specification`, `--global-secondary-indexes`, `--local-secondary-indexes`, `--table-class`, `--deletion-protection-enabled`, `--resource-policy`, `--global-table-*` are pass-through/optional; billing-mode PAY_PER_REQUEST path is the one actually exercised meaningfully by tests — provisioned-throughput behavior can be a no-op/ignored per spec note.
   - Oversized values (512-char table name, 65-char attribute-definitions string that isn't valid shorthand/JSON) must be rejected as usage errors (252) — i.e., any value that fails to parse as valid shorthand or JSON, or is structurally nonsensical for the flag, is a client-side parse failure, not forwarded to the service.
4. **Required-field enforcement**: `create-table` needs `--table-name`; `delete-table` needs `--table-name`; `put-item` needs `--table-name` + `--item`; `delete-item` needs `--table-name` + `--key`. Missing any → 252.
5. **Dispatch to DynamoDB API**: call `CreateTable`, `DeleteTable`, `PutItem`, `DeleteItem` respectively against the configured endpoint (via `boto3` if available, or raw signed HTTP requests, or any other in-image HTTP/SDK mechanism). Do not hardcode/override endpoint, region, or credentials — read them from environment (`AWS_ENDPOINT_URL`/`AWS_ENDPOINT_URL_DYNAMODB`, `AWS_ACCESS_KEY_ID`, etc.) exactly as provided.
6. **Response handling**: on HTTP/service success, print the JSON response body to stdout, exit 0. On service error response, extract the DynamoDB `__type`/error code and message, print in one of the accepted stderr shapes, exit 254 (or 1/255, but 254 is the natural mapping for "service-modeled error").
7. **Error translation**: never let a raw exception/traceback reach stderr — catch broadly around the network call and any JSON parsing that happens after argument validation, converting to the appropriate exit code and message shape.
8. **create-table defaults**: when `--attribute-definitions`/`--key-schema` are omitted but `--table-name` alone is given, a correct implementation either forwards the omitted-field request as-is (service will reject with `ValidationException` → 254, matching the "exit 254" bare-table-name error case) or supplies sensible defaults consistent with the observed error-code expectations. Given the error table lists `create-table --table-name <string>` alone as **254** (not 252), the required-fields check for `create-table` must NOT require `--attribute-definitions`/`--key-schema` client-side — omission is a *service*-level rejection, not a usage error. (This differs from `put-item`/`delete-item` where `--item`/`--key` omission IS a 252 client-side usage error.)

## Solution space

- **HTTP client choice**: any of `boto3`, `botocore`, hand-rolled SigV4-signed `urllib`/`requests` calls, or another language's AWS SDK (Go, Node, Java, etc.) are all valid, as long as no extra packages are fetched beyond what the image ships and the real `aws` binary/awscli is not shelled out to.
- **Language choice**: Python, Go, Node, shell+curl, etc. — any executable named `aws` on `$PATH` works, single-file or multi-file.
- **Shorthand parsing**: could reuse a bundled botocore shorthand parser (if `boto3` is available, letting botocore's own client construct the request and raise botocore exceptions, which are then caught and reformatted) instead of writing a custom shorthand/JSON dual-mode parser — this is a fully valid alternate route and arguably more robust for the "documented flags" match, since botocore knows DynamoDB's real parameter shapes and raises `ParamValidationError` naturally for malformed input.
- **Argument parsing approach**: manual token loop vs. `argparse`-based parsing with `nargs` tricks — both acceptable as long as unknown flags/duplicates/missing values map to exit 252 and value semantics are preserved.
- **create-table field defaulting**: a solution may choose to never inject default AttributeDefinitions/KeySchema and simply forward whatever the user passed (letting the service produce `ValidationException` for the bare `--table-name` case), or it may inject defaults only when-safe — both satisfy the exit-254 requirement as long as the bare-name case does NOT succeed silently (that would violate the observed exit-254 expectation).
- **Error extraction**: parsing botocore's `ClientError.response['Error']` vs. parsing a raw JSON error body's `__type`/`message` fields — both fine, as long as the code+message end up in an accepted stderr shape.

## Known pitfalls

- Treating `create-table --table-name <string>` (no attribute-definitions/key-schema) as a 252 usage error instead of forwarding to the service and getting 254 — the spec explicitly lists this as exit 254, not 252. A common mistake is to require attribute-definitions/key-schema client-side.
- Client-side validating table names (length, charset) — spec explicitly forbids this except for the truly oversized (512-char) case which is documented as producing 252; over-eager validation of ordinary names would incorrectly reject valid names.
- Mixing stdout/stderr, e.g., printing a preamble or trailing debug info to stdout on success, or writing partial JSON to stdout before an error is discovered mid-command.
- Letting exceptions (JSON decode errors on the *response*, network errors, SDK internal errors) leak as Python/Go tracebacks to stderr instead of being caught and reduced to a clean one-line message.
- Not treating duplicate flags (`--table-name X --table-name Y`) as an error — the spec requires 252 for this in every command.
- Not rejecting unknown flags (`--not-a-real-flag`) — must be 252, not silently ignored (silently ignoring would produce success/254 depending on service response instead of 252).
- Not rejecting empty flag values (`--table-name ` with nothing after) — must be 252.
- Turning oversized/invalid `--attribute-definitions` shorthand (`{not valid json` or a bogus 65-char string) into a crash instead of a clean 252.
- Mutating numeric AttributeValue strings (`{"N":"5"}`) during any parse→re-serialize round trip in a way that changes their string representation (e.g., `json.loads` → Python int/float → re-`json.dumps` could still preserve `"5"` as a JSON string value inside `N`, but care needed if any code path treats `N` values as numbers rather than passing the dict through untouched).
- Signing/endpoint mistakes: overriding region/endpoint/credentials in code instead of relying on env — breaks connectivity to the sandboxed DynamoDB-compatible backend.
- Not making `delete-item` on a non-existent key succeed (some naive implementations might add a client-side existence-check condition-expression by default, which would break idempotent delete semantics).
- Forgetting the `ConditionalCheckFailedException` pass-through path for `--condition-expression` failures on both `put-item` and `delete-item`.
- Exiting 0 on a service error response by forgetting to check the HTTP status/error envelope before printing.

## Cheat surface

- A submission could try to hardcode canned JSON responses for `create-table`/`put-item`/etc. without actually talking to the backend — this would fail cross-command consistency checks (`list-tables`, `get-item`, `query` reflecting real state) since state must persist across process invocations via the real backend, not in-memory/local fake state. Any local-only mock state that doesn't survive across separate subprocess invocations (each CLI call is a fresh process) is not viable, since there is no shared state mechanism other than the actual DynamoDB endpoint.
- Could try to always exit 0 and print `{}`-ish stub to pass loosely-checked cases — fails on exit-code assertions for the many explicit error cases (252/254) and fails cross-command state checks that read real data back with `get-item`/`list-tables`/`query`.
- Could try to guess exit codes from argv text patterns without truly parsing (e.g., regex sniffing for "not-a-real-flag" substring) — fragile and likely to fail on the numerous non-enumerated but implied validations (empty values, duplicates, oversized values); a real flag-table-driven parser is needed for robustness.
- Shelling out to `awscli`/real `aws` binary is explicitly disallowed and would be a detectable cheat/violation even if functionally it might work.

## Success criteria

- For every documented error case, the correct exit code (252 for usage/parse errors, 254 for service-modeled errors) is produced, with stdout empty and a class-identifying line on stderr, no traceback.
- For every success case, stdout contains a JSON document parseable by `json.loads`, stderr is empty, exit code 0.
- Cross-command state is honored via the real backend: `create-table` → table visible in `list-tables`; `put-item` → item visible via `get-item`; `delete-item` → item absent via `get-item`; `delete-table` → table absent from `list-tables`; conditional-expression failures leave prior state unchanged.
- Numeric AttributeValues remain JSON-string-encoded (`{"N": "5"}`) end-to-end, unaltered by the CLI's parsing/serialization.
- Re-creating an existing table → `ResourceInUseException`-class failure; key-schema/attribute-definitions mismatch → `ValidationException`-class failure; operating on a missing table → `ResourceNotFoundException`-class failure; failed condition expressions → `ConditionalCheckFailedException`-class failure.
- No stray output, no mixed stdout/stderr, no stack traces, under any tested input including malformed/oversized/duplicate-flag/unknown-flag argv.