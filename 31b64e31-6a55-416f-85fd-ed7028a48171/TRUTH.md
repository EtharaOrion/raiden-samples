# TRUTH: 31b64e31-6a55-416f-85fd-ed7028a48171

## Problem

Implement a single executable named `aws` on `$PATH` that emulates the subset of the real AWS CLI needed for `aws dynamodb create-table|get-item|list-tables|put-item`. The program must talk to a DynamoDB-compatible endpoint (already configured via environment variables such as `AWS_ENDPOINT_URL`/`AWS_ENDPOINT_URL_DYNAMODB` and credentials), translate CLI flags into the corresponding DynamoDB JSON API request, and translate the response/error back into stdout/stderr with a specific exit code contract. State (tables and items) is held by the backing service, not by the CLI process, so correctness is judged across sequences of invocations (create → put → get → list).

## Behavioral contract

- Single binary `aws`, dispatches on `argv[1] == "dynamodb"` and `argv[2]` as the subcommand.
- Each subcommand accepts only its documented flags; unknown flags, missing required flags, empty required values, duplicated flags, and malformed JSON in flag values are usage errors → exit `252`, nothing on stdout.
- On success: prints one JSON document to stdout parseable by `json.loads`; stderr is empty; exit `0`.
- On a modeled service error (endpoint reachable, service rejects the request): stderr contains a line identifying the error class (either full AWS envelope, bare `Code: message`, or a usage-style prefix) and exit is `254` for these tasks' declared error-cases (note: the spec's general exit-code table also allows `1`, but the enumerated error cases in this task all specify `254`, so a correct implementation returns `254` for ResourceNotFoundException/ResourceInUseException/ConditionalCheckFailedException/ValidationException-type failures reached via valid syntax but rejected by the service or absent resources).
- No raw tracebacks ever, regardless of failure type.
- Numbers in Item/Key AttributeValue maps are represented as JSON strings under `"N"`.
- State consistency: create-table → visible in list-tables; put-item → immediately visible via get-item (strongly consistent reads); duplicate create-table on an existing name fails; conditional put failures leave stored data unchanged.

## Solution decomposition

1. **Argument parsing / dispatch**: read `argv[1]` (`dynamodb`) and `argv[2]` (subcommand); route to one of four handlers. Missing command or unrecognized subcommand → usage error, exit 252.
2. **Flag parser**: generic `--flag value...` scanner restricted to each command's allowed flag set; reject unknown flags, duplicate flags, flags with empty/missing values, and stray positional tokens — all exit 252. This must run to completion (not fail the whole process) before any network call, so invalid-value tests never reach the service.
3. **Payload construction**: map kebab-case CLI flags to CamelCase DynamoDB request fields (`--table-name`→`TableName`, `--key`→`Key`, `--item`→`Item`, `--attribute-definitions`→`AttributeDefinitions`, `--key-schema`→`KeySchema`, `--billing-mode`→`BillingMode`, `--condition-expression`→`ConditionExpression`, boolean flags like `--consistent-read`/`--deletion-protection-enabled` become `true`, etc.). JSON-valued flags (`--key`, `--item`, `--expected`, `--expression-attribute-values`, etc.) must be parsed via `json.loads`; malformed JSON → exit 252 before any network call.
4. **Shorthand support for create-table**: `--attribute-definitions AttributeName=id,AttributeType=S` and `--key-schema AttributeName=id,KeyType=HASH` (comma-separated `Key=Value` shorthand) must be converted into the JSON list-of-objects the DynamoDB API expects, since these are the observed argv patterns and no JSON form is guaranteed to be given. Similarly for `--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5`.
5. **Request dispatch**: send the constructed payload as a DynamoDB `X-Amz-Target: DynamoDB_20120810.<Operation>` JSON-1.0 POST to the endpoint URL taken from the environment (must NOT hardcode/override endpoint, region, or credentials — read what's already provided). SigV4-style auth headers may be dummy/pass-through since the sandbox endpoint doesn't enforce real signing (as in the reference), or real signing may be used if credentials are available — either is acceptable as long as no external service or extra packages are used.
6. **Response handling**: on HTTP success, print the JSON body verbatim (or reformatted) to stdout, exit 0. Note `PutItem` may return an empty body (`{}`) — this still counts as success with a printed JSON document (e.g., `{}`), not literally empty stdout, to satisfy "stdout parseable by json.loads" — printing a blank line here is a latent inconsistency in the reference (it prints `""` not valid JSON) and a stricter implementation should print `{}` instead.
7. **Error handling**: on HTTP error, extract `__type`/error code and `message` from the JSON error body, write a stderr line naming the error class in one of the accepted shapes, and exit with a code in `{1,254,255}` (this task's error cases all expect 254). Connection failures should also produce a clean stderr message and non-zero exit, not a traceback.
8. **No client-side table-name validation** — let the service reject malformed names; only structural/flag-parsing issues are checked client-side.

## Solution space

Valid alternative implementations include:
- **Any language** (Python, Go, Node, shell+curl, etc.) since only "no extra packages fetched" is required — using the image's stdlib HTTP client, or even boto3 if already installed in the image (not fetched) is acceptable, as long as it isn't shelling out to the real `aws` CLI binary or hitting the real AWS service.
- Using **boto3** (if pre-installed) as the DynamoDB client instead of hand-rolled HTTP + JSON-1.0 protocol calls — this simplifies error mapping since boto3 raises typed `ClientError`s with `.response['Error']['Code']`.
- Real SigV4 request signing vs. dummy/placeholder auth headers — both fine since the sandbox endpoint likely does not enforce signature validation (matches reference's dummy signature approach), but real signing is not wrong either.
- Accepting flag values either as strict JSON only, or supporting both JSON and AWS CLI shorthand syntax for `--attribute-definitions`/`--key-schema`/`--provisioned-throughput` (shorthand support is necessary given the observed argv patterns use shorthand for create-table).
- Exit code for modeled service errors could be `1` or `254` per the general contract table, though this task's specific error-case list uses `254`; a solution using `1` would fail this task's tests, but `254` or `255` for exceptions not explicitly enumerated is safe.
- Using `sys.argv` positional scanning vs. a proper argparse-based parser — any approach that correctly rejects unknown/duplicate/missing flags before network I/O is fine.
- Printing response JSON with or without indentation/pretty-printing — only semantic JSON content is checked.

## Known pitfalls

- **Order of validation vs. network call**: usage errors (252) must be detected before contacting the service; if a malformed request slips through to the backend and the backend's own validation triggers a 4xx that's slapped with exit 254, tests expecting 252 will fail. E.g., duplicate `--table-name`, oversized table-name (512 chars vs allowed flag length), empty `--table-name`, and unknown flags must all be caught client-side.
- **Distinguishing 252 vs 254**: "missing/extra argument, malformed value, unknown flag" = 252 (client-side, no network call); "service rejects a syntactically valid request" (ResourceNotFoundException, ResourceInUseException, ConditionalCheckFailedException, ValidationException from mismatched key-schema/attribute-definitions) = 254. Conflating these is a common bug.
- **Oversized table-name (512 chars) → 252**: this must be caught as a usage/length validation issue, NOT sent to the service as a ValidationException (which would exit 254). This contradicts "do not validate table names client-side" for basic malformed names, but the oversized-value case is explicitly listed under error cases with exit 252 — read the spec's error-case list carefully; length limits are apparently enforced by the CLI's own argument parser layer (or happen to be rejected pre-flight) rather than by "table name legality" rules.
- **`--attribute-definitions {not valid json` → 252**: this literal broken-JSON test appears across all four commands even where `--attribute-definitions` isn't a documented flag for that command (get-item/put-item) — meaning it must be treated as an *unknown flag* there, still exit 252 either way. Ensure the "unknown flag" path is hit rather than crashing.
- **Empty stdout on failure, empty stderr on success**: mixing streams (e.g., printing partial JSON before an error occurs, or writing a warning to stderr on a successful call) breaks tests that assert exact stream separation.
- **PutItem success body**: DynamoDB's PutItem response is often `{}` (empty object) unless `ReturnValues` is requested. Printing truly empty stdout (no JSON at all, e.g., a blank string) would fail "stdout parseable by json.loads" — must print at least `{}`.
- **Strong consistency for get-item**: if using a real DynamoDB or DynamoDB Local backend, ensure `ConsistentRead: true` behavior/defaults don't introduce staleness in a way that breaks the immediate-read-after-write expectation the tests rely on (usually a non-issue with DynamoDB Local, but explicit `--consistent-read` must be forwarded correctly, not silently dropped).
- **Traceback leakage**: any unhandled exception (bad JSON parse inside a `try` that isn't caught, KeyError from malformed payload) must be caught and converted to a clean stderr message — never let Python's default traceback print.
- **Not fabricating flags / not hardcoding endpoint/region/credentials**: overriding `AWS_ENDPOINT_URL`, region, or credentials in code instead of reading env vars breaks connectivity in the test harness.
- **Key-schema/attribute-definitions mismatch validation**: this is a service-side check (ValidationException, 254), not something the CLI should attempt to reimplement client-side — just forward and relay the service's error.

## Cheat surface

- A submission could try to keep its own **in-process fake state** (e.g., a JSON file or in-memory dict of tables/items) instead of actually calling the configured endpoint, faking all responses locally. This would violate "do not override the service address... in code" implicitly, and would likely fail cross-process state consistency if tests invoke the CLI as separate subprocesses expecting shared backend state (a local file-based fake could actually pass many tests if made subprocess-persistent and put in a shared location — this is a real cheat risk graders should watch for: verify actual HTTP calls happen to the env-configured endpoint, not a local shim).
- Hardcoding exit code `254` for literally all failures without distinguishing usage errors (252) from service errors would pass some but not all error-case tests — a shallow "catch everything, exit 254" implementation is a partial cheat that TRUTH must catch via explicit 252 vs 254 differentiation checks.
- Printing the input verbatim / echoing constructed payload instead of the real service response would superficially resemble correct JSON shape but fail cross-command consistency checks (e.g., get-item must reflect real prior writes, not just echo the key back).
- Swallowing all exceptions and printing a generic success `{}` to stdout regardless of actual outcome (never truly exiting non-zero) would defeat failure-path tests; must be checked that failure scenarios (missing table, duplicate create, conditional check failure) genuinely surface non-zero exits and empty stdout.
- Using the real `aws` CLI binary or `awscli`/`boto3` pointed at real AWS (ignoring the sandbox endpoint env vars) is explicitly disallowed and should be flagged if endpoint envs are overridden.

## Success criteria

- All four subcommands parse only their documented flags; any unknown flag, duplicate flag, missing required flag, or empty required value yields exit `252` with empty stdout and a class-identifying stderr line, with no network call made.
- Malformed JSON in any JSON-valued flag yields exit `252` (checked client-side pre-network) across all commands, including the shared `--attribute-definitions {not valid json` probe on commands where that flag isn't even documented (unknown-flag path also yields 252).
- Oversized table-name (512 chars) yields exit `252` for create-table/get-item/put-item.
- A syntactically valid create-table request against a fresh table name succeeds (exit 0, JSON on stdout), and the table subsequently appears in `list-tables` output (checked via set membership, not order).
- Re-issuing `create-table` for the same name fails with a `ResourceInUseException`-class stderr message and exit `254`.
- create-table with key-schema referencing an attribute absent from attribute-definitions fails with `ValidationException`-class error and exit `254`.
- `get-item`/`put-item` against a nonexistent table fail with `ResourceNotFoundException`-class error, exit `254`.
- `put-item` followed by `get-item` on the same key returns the written item under `{"Item": ...}`; absent keys return success with no `Item` member.
- `put-item` with `--condition-expression attribute_not_exists(pk)` against an existing key fails with `ConditionalCheckFailedException`-class error, exit `254`, and does not mutate the stored item (verified by a subsequent get-item).
- Number attribute values round-trip as `{"N": "<string>"}`, never as JSON numeric literals.
- `list-tables` with no tables returns `{"TableNames": []}` (or equivalent empty list) with exit 0; membership-based assertions only.
- On every success path, stdout is valid JSON and stderr is empty; on every failure path, stdout is empty and stderr contains a message identifying the error class, with no raw tracebacks anywhere.
- Exit codes used are confined to `{0, 1, 252, 254, 255}` and match the specific codes enumerated per error case in this task (252 for usage/client errors, 254 for modeled service errors on syntactically-valid-but-rejected or missing-table cases).