# TRUTH: 2ff5cecf-2386-4be3-8f1c-d471e32150f8

## Problem

Implement a single executable `aws` on `$PATH` that dispatches on `argv[1]=="dynamodb"` and `argv[2]` to emulate four `aws dynamodb` subcommands (`delete-table`, `get-item`, `list-tables`, `update-item`) against a live DynamoDB-compatible endpoint reachable via credentials/endpoint already present in the environment. The program is a thin, faithful client: it must marshal CLI flags into DynamoDB JSON-protocol requests, send them to the configured endpoint, and translate the response/error back into the documented stdout/stderr/exit-code contract. No local business logic re-implements DynamoDB semantics (item storage, expression evaluation, conditional checks) — that all lives in the real service behind the endpoint; correctness is judged by round-tripping state through it correctly.

## Behavioral contract

- Invocation: `aws dynamodb <subcommand> [--flag value ...]`.
- Success: operation response JSON (parseable, DynamoDB-shaped) on stdout only, exit 0, stderr empty.
- Failure: stdout empty, one-line human-readable error on stderr identifying error class (service error envelope, bare `<ErrorCode>: msg`, or client usage-error prefix), no traceback, exit code in `{1,252,254,255}` (0 reserved for success).
  - `252`: usage errors — unknown/missing/duplicate/malformed flags, empty flag value, invalid JSON in a flag, oversized values (>~512 chars) that the SDK/service itself would reject as a parameter validation error before or via the call.
  - `254`: modeled service exceptions (`ResourceNotFoundException`, `ConditionalCheckFailedException`, `ValidationException`, `ResourceInUseException`, etc.) returned by the backing service.
  - `1`/`255`: other application/general errors.
- Only the four listed subcommands need to work; each supports exactly its documented flag set — no extra invented flags, no client-side table-name validation (let the service reject via `ValidationException`).
- State (tables/items) persists across separate process invocations because it lives in the real backing DynamoDB-compatible service — the CLI itself must be stateless and must not use the real `aws` binary or `awscli` package.
- Numbers in AttributeValue JSON are strings (`{"N":"5"}`) — this is just passed through, not implemented by the CLI.
- Tables are on-demand (`PAY_PER_REQUEST`) — irrelevant to these four commands directly (no create-table here) but implies no local capacity logic.

## Solution decomposition

1. **Argv dispatch**: recognize `dynamodb` as argv[1], subcommand as argv[2]; unknown subcommand → usage error (252).
2. **Flag parser per subcommand**: whitelist of `--flag value` (and boolean flags like `--consistent-read` needing no value) matching each command's documented flag set exactly; reject unknown flags, duplicate flags, missing values, empty values, oversized values, and invalid inline JSON for JSON-typed flags — all as 252.
3. **Required-parameter check**: `--table-name` required for all four; `--key` required for `get-item`/`update-item`. Missing → 252.
4. **Payload marshaling**: map CLI flags to the DynamoDB JSON protocol request field names (TableName, Key, UpdateExpression, ExpressionAttributeNames/Values, ConditionExpression, Limit, ExclusiveStartTableName, ConsistentRead, etc.), with correct types (string/int/bool/JSON-decoded object).
5. **Transport**: send an `X-Amz-Target: DynamoDB_20120810.<Op>` JSON request to the endpoint from env (e.g. `AWS_ENDPOINT_URL`/`AWS_ENDPOINT_URL_DYNAMODB` or SDK default resolution), using credentials already in the environment (do not hardcode/override endpoint or creds; do not fabricate a real SigV4 signature requirement if the endpoint doesn't enforce it — but must not override configured endpoint/region/creds).
6. **Response handling**: on 2xx, print returned JSON body to stdout (empty body → maybe `{}`/nothing, but must still be valid per contract — empty-Item GetItem case should omit `Item` key rather than emit `null` or error).
7. **Error handling**: on HTTP error / modeled exception, parse the `__type`/`message` envelope, print a class-identifying line to stderr, exit 254. Catch transport/config problems distinctly (should still not leak tracebacks) — exit non-zero within the allowed set.
8. **No stdout/stderr mixing**: ensure exactly one of stdout/stderr is written per invocation.

## Solution space

Multiple implementation strategies are valid and must not be penalized:

- **Raw HTTP JSON-protocol client** (as in the reference) hitting the DynamoDB JSON API directly with `X-Amz-Target` headers, hand-rolled or dummy auth headers — valid if the test endpoint doesn't require real SigV4 validation.
- **Using boto3** (if present in the image) configured to pick up endpoint/region/credentials purely from environment variables, calling `delete_table`, `get_item`, `list_tables`, `update_item`, and catching `botocore.exceptions.ClientError` to extract `Error.Code`/`Error.Message` for the stderr envelope. This is arguably simpler and equally correct as long as it doesn't override env-configured endpoint/region/creds in code.
- Any other language (Node.js AWS SDK v2/v3, Go SDK, raw curl-equivalent in Bash) provided it's already available in the image and no packages are fetched.
- Flag parsing can be done via a manual whitelist dict (as shown) or via any argument-parsing library already available, as long as unknown/duplicate/malformed/oversized flags are rejected with exit 252 and valid ones are correctly typed/passed through.
- Boolean flags (`--consistent-read`) can be implemented as no-value flags or flags accepting an optional value, as long as documented behavior holds.
- Error-class stderr line can take any of the three documented shapes (service envelope, bare `Code: message`, or usage-error prefix) — wording is not checked verbatim.
- Exit code choice within `{1,254,255}` for a modeled service failure is flexible as long as it's non-zero and semantically reasonable relative to the documented mapping (though matching the documented 254/252 split is the cleanest way to satisfy explicit error-case tests that assert specific codes).

## Known pitfalls

- **Client-side table-name validation**: task explicitly forbids validating table names locally; must let the service return `ValidationException`. A solution that pre-validates name format and rejects locally deviates from spec (though functionally may still produce a similar-looking error — risk is over/under-restricting valid inputs).
- **Oversized flag values (512 chars) must yield 252**, not be silently sent to the service (which might return a different code or hang) — parser needs an explicit length guard or rely on the SDK's own parameter validation producing a usage-class error before the network call.
- **Duplicate flags** (e.g., `--table-name x --table-name y`) must be usage errors (252), not "last wins".
- **Empty value for `--table-name`** (`--table-name ` with nothing after) must be 252 — easy to mishandle if argv parsing treats a following `--flag` token as the value or silently accepts empty string.
- **Malformed JSON for any JSON-typed flag** (even ones not central to the command, like `--attribute-definitions` which isn't in the flag whitelist at all for these four commands) must cause 252 — note: `--attribute-definitions` appears in error cases as a bogus/unknown flag for these commands, so it should be rejected as "unknown option" (252) regardless of JSON validity, exercising the "unknown flag" path rather than "bad JSON" path.
- **`get-item` on absent key**: must return exit 0 with a JSON body lacking the `Item` key (not `{"Item": null}`, not an error). Easy to mess up if code defaults to writing an empty object incorrectly or errors on missing key.
- **Reserved words in update expressions**: must surface as `ValidationException` from the real service (not swallowed/misclassified) — this only works correctly if the update-expression/attribute-names/values are passed through verbatim to the service, unmangled.
- **Conditional check failures must not mutate state** — this is guaranteed automatically by delegating to the real service's atomic conditional update; a bug would only arise from doing writes client-side outside the single atomic call.
- **stdout/stderr mixing**: must never write partial JSON to stdout before discovering an error downstream; buffer/build full response before printing, and only print on the success path.
- **Not overriding endpoint/region/credentials**: hardcoding a region or endpoint in code instead of reading env vars breaks the "respect environment configuration" constraint, potentially causing all calls to target the wrong service.
- **No tracebacks**: unhandled exceptions (e.g. `KeyError`, `json.JSONDecodeError`, network errors) must be caught and converted to a one-line stderr message.
- **Numbers as strings**: passing AttributeValue JSON through must not coerce `{"N":"5"}` into a native number or otherwise transform the JSON structure.

## Cheat surface

- Faking success/error responses locally (e.g., maintaining an in-memory or on-disk fake DynamoDB) without actually calling the configured endpoint would break state-consistency and cross-invocation tests (separate subprocess calls sharing state) unless persisted very carefully — and would violate "do not shell out/fabricate"-style spirit even if not literally forbidden; the safest and intended path is to always hit the real configured endpoint.
- Hardcoding exit code 254 for all `ServiceError`s without inspecting whether it's really a modeled exception vs. a connectivity error could mask real bugs, but tests only check exit code membership and message-class matching so this is within tolerance as long as messages are accurate.
- Printing an error code without querying the service at all (e.g., stub that always returns `ResourceNotFoundException`) would fail success-path tests and cross-command consistency tests (e.g. create→get sequences), so blind stubbing is not viable given 126 shipped tests presumably covering happy paths.
- Silently swallowing unknown flags instead of erroring (252) would pass some tests accidentally but fail the explicit `--not-a-real-flag` error-case tests.
- Emitting `{"Item": null}` for missing get-item key would likely fail strict "no Item member" assertions if tests check `"Item" not in response`.

## Success criteria

- All documented error-case argv patterns exit with the specified code (252 for usage errors, 254 for modeled service errors) and write a single class-identifying line to stderr with empty stdout.
- All documented success argv patterns exit 0, write valid parseable JSON to stdout matching DynamoDB response shape, with empty stderr.
- `list-tables` returns `TableNames` as a set-comparable list (empty when no tables exist).
- `delete-table` removes the table from subsequent `list-tables` output; deleting a nonexistent table gives `ResourceNotFoundException`/254.
- `get-item` returns `{"Item": ...}` for existing keys and omits `Item` for absent keys; reads are consistent with prior writes (via `--consistent-read` where needed, or service default strong consistency for this local backend); missing table → `ResourceNotFoundException`/254.
- `update-item` correctly applies `UpdateExpression` with attribute name/value aliasing, visible afterward via `get-item`; unescaped reserved words → `ValidationException`; failed `--condition-expression` → `ConditionalCheckFailedException` with no state mutation.
- No test observes a raw stack trace, mixed stdout/stderr content, or an exit code outside `{0,1,252,254,255}`.
- Cross-command sequences (create→put→get→query-style flows spanning other commands in the broader suite, and specifically delete→list, update→get here) reflect consistent, cumulative state.