# TRUTH: 51ba95bc-50d4-43b5-9b0e-2953eeed5776

## Problem

Build a single executable named `aws` on `$PATH` that implements three `dynamodb` subcommands (`create-table`, `get-item`, `put-item`) by talking to a real DynamoDB-compatible endpoint configured via the environment (credentials/endpoint already set, must not be overridden in code). The program must behave like a minimal, faithful slice of the real `aws` CLI: parse documented flags only, translate them into the DynamoDB JSON protocol request, forward to the service, and translate the response/error back into CLI-shaped stdout/stderr with a constrained exit-code vocabulary. State (tables/items) lives in the backing service, not in the submission, so correctness across a sequence of commands depends on correctly relaying requests, not on any local persistence.

## Behavioral contract

- Single dispatcher executable `aws` reads `argv[1] == "dynamodb"`, `argv[2]` = subcommand, remaining tokens = flags.
- Only the documented flags per subcommand are accepted; anything else (unknown flag, duplicate flag, missing required value, malformed value) is a **client-side usage error** → exit `252`, message on stderr, nothing on stdout.
- Required flags: `create-table` needs `--table-name`; `get-item` needs `--table-name` + `--key`; `put-item` needs `--table-name` + `--item`. Missing → exit `252`.
- Empty-string value for `--table-name` (`--table-name ` with nothing following, i.e. flag immediately followed by another flag or end) → exit `252`.
- Oversized `--table-name` (512 chars) is NOT rejected client-side (per instructions: don't validate table names locally) — it must be sent to the service and the resulting `ValidationException`/error surfaced, which is exit `252` per the declared error case (so implementations must map that particular oversized-name case to 252 — see note below on how the reference achieves this incidentally). Malformed `--attribute-definitions {not valid json` → JSON parse failure → 252.
- Repeating the same flag twice (`--table-name x --table-name y`) → exit `252` (duplicate flag detection).
- On success: perform the operation against the endpoint; print the DynamoDB JSON response (or the relevant subset — see below) to stdout as parseable JSON, nothing on stderr, exit `0`.
- On a service-modeled failure (`ResourceNotFoundException`, `ResourceInUseException`, `ConditionalCheckFailedException`, `ValidationException`, etc.): nothing on stdout, an error line on stderr naming the error code/class, exit `254`.
- `get-item`: response has `Item` key only if found; if not found, no `Item` member is present (still exit 0, valid empty/near-empty JSON on stdout).
- `get-item` reads must be strongly consistent (`ConsistentRead: true` should be passed, or otherwise guarantee read-after-write visibility for the very next read against the sandboxed backend).
- `put-item` correctly forwards `--condition-expression` etc.; a failed condition check must not create/alter the item and must surface `ConditionalCheckFailedException`.
- `create-table` re-creation of an existing table name must surface `ResourceInUseException`; key-schema/attribute-definition mismatch surfaces `ValidationException`. These are service-side; the client just needs to forward and relay the error untouched.
- No raw tracebacks on any path. No fabricated flags. No stdout/stderr mixing.

## Solution decomposition

1. **Argv parsing / dispatch**: strip `dynamodb`, dispatch on subcommand token; unknown subcommand → usage error exit 252 (or 255, both in allowed set, but 252 is most consistent with "usage error").
2. **Per-subcommand flag table**: map each documented `--flag` to a request field name and a value-parsing strategy (plain string, JSON blob, JSON-or-shorthand list for attribute-definitions/key-schema, JSON-or-shorthand map for provisioned-throughput, boolean flag with no value).
3. **Value parsing correctness**:
   - `--attribute-definitions` / `--key-schema` accept either a JSON array or AWS CLI shorthand (`AttributeName=id,AttributeType=S ...` — space-separated repeated groups). Must produce a list of dicts either way.
   - `--provisioned-throughput` accepts JSON object or shorthand `ReadCapacityUnits=5,WriteCapacityUnits=5` with numeric coercion.
   - All other `json`-typed flags (`--key`, `--item`, `--expression-attribute-values`, etc.) are JSON-only; invalid JSON → usage error 252.
   - Booleans (`--consistent-read`, `--deletion-protection-enabled`) take no following value.
4. **Duplicate-flag / stray-token detection** to satisfy the `--table-name x --table-name y` and trailing-garbage error cases.
5. **HTTP transport**: build a DynamoDB JSON-1.0 request (`Content-Type: application/x-amz-json-1.0`, `X-Amz-Target: DynamoDB_20120810.<Op>`) against the endpoint from environment variables (never hardcode/override endpoint, region, or creds), POST the JSON body, parse response.
6. **Error translation**: on non-2xx HTTP, parse the DynamoDB error envelope (`__type` / `message`), extract the short error code, print `<Code>: <message>` (or full AWS envelope form) to stderr, exit `254`.
7. **Success output shaping**: print the relevant response JSON to stdout; for `get-item`, omit `Item` key entirely when absent rather than printing `null`/empty item.
8. **Exit code discipline**: usage failures → 252; service-modeled failures → 254; success → 0; never emit a traceback (catch-all exception handler prints a brief message and exits with an allowed non-zero code, e.g. 255, instead of propagating Python's default traceback).

## Solution space

Any implementation reaching this behavior is acceptable, including:
- **Boto3-based implementation** (rather than hand-rolled HTTP+SigV4-stub) — arguably simpler and more robust, since boto3 already knows DynamoDB's shorthand/JSON parsing, signs requests properly using the ambient credentials/endpoint env vars, and raises typed `ClientError` exceptions with `.response["Error"]["Code"]`. This is a fully valid, likely more robust, alternative to the reference's raw-HTTP-with-dummy-auth approach.
- Implementation in any language (Go, Node, shell wrapping curl + jq, etc.) as long as the executable is named `aws`, is on `$PATH`, and satisfies the I/O contract.
- Using `argparse`-style strict parsing vs. manual token-walking, as long as unknown flags/missing values reliably yield 252.
- Printing full raw service JSON response vs. a filtered subset — either is fine as long as required members (`Item` for get-item) follow the presence/absence rule and the output is valid JSON.
- Choosing exit code 255 vs 252 for "unknown subcommand" — both are in the allowed non-zero set; tests only assert `returncode != 0` for generic error cases, and specific codes only where explicitly declared (252/254).
- Any strategy for shorthand parsing of `--attribute-definitions`/`--key-schema`/`--provisioned-throughput` — accepting JSON-only and rejecting shorthand would fail the declared shorthand test cases, so shorthand support is effectively required, but the exact parser (regex, split, csv) is unconstrained.
- Determining "oversized table name" (512 chars) → 252: this is not a documented client validation but is required by the declared error case. A compliant solution may either (a) truly avoid client-side length validation and rely on the service to reject an oversized name and then map that particular service error to 252 instead of the usual 254, or (b) impose a generous length cap client-side. Since the instructions explicitly forbid client-side table-name validation ("Do not validate table names client-side"), the intended route is (a): the service's `ValidationException` for the malformed/oversized name is mapped to exit `252` rather than `254`. Any solution that achieves the correct exit code for this specific declared case without breaking the "don't validate names" rule for other cases is acceptable — e.g., special-casing `ValidationException` arising from parameter-shape issues (too long) to exit 252, while runtime/business ValidationExceptions (key-schema mismatch) still exit at whatever code they map to (accepted set includes 252/254/1, since the instruction's own error-case table lists `--table-name <oversized-value:512-chars>` → 252 while key-schema mismatch is only described narratively, not in the strict exit-code table, giving implementers latitude).

## Known pitfalls

- Mixing stdout/stderr: any diagnostic print must go to stderr only; accidentally using `print()` for errors instead of `sys.stderr.write` breaks the contract.
- Printing `{"Item": null}` or an empty `Item` key when the item is absent instead of omitting the key entirely — violates the "NO `Item` member" requirement.
- Letting Python/other runtime exceptions propagate as tracebacks (e.g., unguarded `json.loads`, `KeyError` on missing dict fields) — must be caught and converted to a clean error line + allowed exit code.
- Treating `--table-name` with an empty value (immediately followed by another `--flag` or end of argv) as valid — must be flagged as a usage error, not silently accepted as `TableName=""`.
- Failing to support both JSON and AWS-CLI shorthand syntax for `--attribute-definitions`/`--key-schema`/`--provisioned-throughput` — many observed argv patterns use shorthand.
- Overriding `AWS_ENDPOINT_URL`/region/credentials in code instead of reading what's already set in the environment — breaks routing to the sandbox's DynamoDB endpoint.
- Not detecting duplicate flags (`--table-name` given twice) leads to silently accepting the last value instead of erroring at 252.
- Not making reads strongly consistent — could cause read-after-write flakiness against an eventually-consistent backing store if `ConsistentRead` isn't forced/passed through.
- Validating table name format/length client-side in general (explicitly disallowed) beyond what's needed for the one declared oversized-name error case.
- Forgetting numbers must remain JSON strings inside AttributeValue maps (`{"N": "5"}`) — since these are just passed through JSON parsing of `--item`/`--key`, this is naturally satisfied as long as the parser doesn't attempt numeric coercion on JSON values (only on shorthand provisioned-throughput fields).
- Swallowing the distinction between a usage error and a service error — e.g., catching all exceptions generically and always exiting 254, which would break the 252-vs-254 split test cases.

## Cheat surface

- Hardcoding responses (e.g., always returning a canned `{"Item": ...}` or always succeeding) instead of actually calling the configured endpoint — would fail cross-command consistency tests (create→put→get) and the ResourceInUseException/ResourceNotFoundException/ConditionalCheckFailedException cases which require genuine service-side state.
- Faking exit codes based on argv pattern-matching rather than actual parse/service outcomes (e.g., special-casing exact strings from the observed-argv list) — would fail on the many `<string_v1..v7>`/`<json_v1..v7>` variants which differ only in opaque substituted values.
- Persisting state locally (a fake in-process/on-disk table store) instead of using the real endpoint — would violate "state must remain consistent across commands" in ways that diverge from actual DynamoDB semantics (e.g., condition expressions, key-schema validation) and could pass some tests while failing others that rely on genuine service validation (e.g., attribute-definitions/key-schema mismatch → ValidationException).
- Shelling out to the real `awscli`/`aws` binary or importing `boto3`'s CLI package as literally `awscli` — explicitly disallowed; using `boto3` (the SDK) directly is fine, but wrapping/calling the actual `aws` executable is not.
- Suppressing all errors and always exiting `0` with empty/garbage JSON to dodge failure-case tests — would fail the declared `-> exit 254` / `-> exit 252` cases and the "stdout empty on failure" check.
- Printing the full Python exception message to stderr disguised as a "brief error string" — technically avoids a traceback but may leak implementation details; better to map to a proper error class name.

## Success criteria

- All three subcommands, invoked as `aws dynamodb <cmd> ...`, produce stdout-only JSON on success (`json.loads`-parseable) and stderr-only class-identifying error text on failure, with empty stdout on failure and empty stderr on success.
- Exit codes are drawn from `{0,1,252,254,255}` and match the declared cases: usage/parse errors → 252, service-modeled errors (missing table, resource-in-use, conditional-check-failed, validation) → 254 (or 1, per the general contract, but the declared cases specifically expect 254 for the shown "success-argv-but-table-doesn't-exist-yet" scenarios), no crashes/tracebacks ever.
- Cross-command state is real and consistent: `create-table` then `list-tables`-equivalent behavior, `put-item` then `get-item` returns the exact written item, conditional put failures leave state unchanged, strongly-consistent reads observe the immediately preceding write.
- No fabricated flags accepted beyond the documented set per subcommand; all documented flags are at least parsed and forwarded (even if some, like provisioned-throughput under PAY_PER_REQUEST, are functionally ignored by the sandbox).
- Environment-provided endpoint/region/credentials are used as-is, never overridden.
- Numbers in AttributeValue JSON remain strings (`{"N": "5"}"`) end-to-end.