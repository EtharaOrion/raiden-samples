# TRUTH: 7f578226-b8d2-4976-b7ee-60f4ac980008

## Problem

Build a single executable named `aws` on `$PATH` that implements four `aws dynamodb` subcommands (`create-table`, `describe-table`, `put-item`, `scan`) by translating CLI argv into calls against a DynamoDB-compatible endpoint reachable via environment-configured credentials/endpoint (a local sandbox service speaking the real DynamoDB JSON protocol). The program must behave like a thin, faithful CLI shim: parse flags per the documented flag set for each subcommand, convert values into DynamoDB JSON request shapes, issue the operation, and print/report results or errors according to a strict output/exit-code contract. State (tables, items) must persist across separate invocations of the process because each command is a separate subprocess call and correctness is verified by sequences like create-table → put-item → get-item → scan.

## Behavioral contract

- Invocation: `aws dynamodb <subcommand> [--flag value ...]`. Unknown top-level tokens, unknown subcommands, unknown flags, duplicate flags, missing required flags, missing flag values, and malformed JSON values for JSON-bearing flags are all **client-side usage errors** → exit `252`, stderr only, stdout empty.
- Oversized values (e.g. table name 512 chars) → usage error → exit `252` (this is AWS SDK-side parameter validation, not client-side name validation — do NOT implement custom table-name format validation; only enforce documented length/parameter constraints).
- Successful calls: JSON response document to stdout only, stderr empty, exit `0`.
- Service-modeled errors (`ResourceNotFoundException`, `ResourceInUseException`, `ConditionalCheckFailedException`, `ValidationException`, etc., returned by the backing DynamoDB-compatible service) → exit `254`, message to stderr identifying the error class, stdout empty.
- Never print a raw stack trace under any circumstance.
- Numbers in item/key AttributeValues are represented as `{"N": "<string>"}` — never as native JSON numbers.
- Do not shell out to `awscli` or the real `aws` binary; do not override endpoint/region/credentials — read them from environment (already configured by the harness).
- No client-side validation of table names beyond what's documented (length is service-enforced too, but many implementations may pre-check trivially — either way the exit code contract must hold).
- State must persist across process invocations: since each command is a new subprocess, all state must live in the backing service reached over network/socket (there is no in-process state to keep) — i.e., every command must actually talk to the configured DynamoDB endpoint rather than emulate state locally in files, UNLESS a local state file is used consistently across invocations (see Solution space).

## Solution decomposition

1. **Entry point & dispatch**: `/workspace/submission/aws` (or any `$PATH` location) parses `argv[1]` as service (`dynamodb`), `argv[2]` as the subcommand, dispatches to one of four handlers.
2. **Argument parsing**: For each subcommand, only the documented flag list is accepted. Parsing must detect: missing required flags (`--table-name`, `--item` for put-item), duplicate flags, flags with empty/missing values, unknown flags, and malformed inline JSON — all mapped to exit `252` before any network call is attempted.
3. **Shorthand/JSON value conversion**: Flags like `--attribute-definitions`, `--key-schema`, `--provisioned-throughput`, `--item`, `--expression-attribute-values`, etc. accept either AWS CLI shorthand syntax (`Key=Val,Key2=Val2`) or raw JSON, and must be converted into the corresponding DynamoDB request field (PascalCase) with correct nesting (e.g., `AttributeDefinitions` is a list of `{AttributeName, AttributeType}` objects, `KeySchema` is a list of `{AttributeName, KeyType}`).
4. **Network call to backing service**: Build and send the DynamoDB JSON-protocol request (`X-Amz-Target: DynamoDB_20120810.<Operation>`, JSON body) to the endpoint configured via environment variables, using whatever credentials are already present in the environment (do not hardcode/override).
5. **Response handling**: On HTTP 2xx, emit the JSON response body to stdout verbatim (or reformatted, order-independent) and exit `0`. On error response, extract the DynamoDB error type/message, write a class-identifying line to stderr, exit `254` (or `1`/`255` for non-modeled errors — but per the task's declared error cases, all listed application failures are `254`).
6. **Cross-command consistency**: Because each invocation is a fresh process, this is naturally satisfied by always hitting the same real backing service; no separate consistency logic is needed as long as no local caching diverges from server state.

## Solution space

Valid alternative approaches (should NOT be penalized):

- **Language choice**: Python, Node.js, Go, Ruby, shell+curl+jq, etc. — anything in the base image, no external package installs.
- **HTTP client**: raw `urllib`, `requests` (if preinstalled), `curl` subprocess, `http.client`, Node `https` module, etc.
- **Signing**: Since the sandbox endpoint typically doesn't enforce real SigV4 validation, a dummy/placeholder Authorization header (as in the reference) is acceptable; a fully correct SigV4 signer is also acceptable and arguably more robust — both are valid.
- **State persistence architecture**: The reference always calls out to a live network endpoint per invocation. An alternative valid architecture is a local JSON-file-backed store at a fixed path (e.g. `/workspace/submission/.dynamodb_state.json`) that persists table/item state across process invocations, IF the task's actual test harness runs against a mock/local endpoint anyway — but given the instructions explicitly say "AWS credentials and endpoint are set in the environment; do not override," the safest and clearly-correct route is talking to the configured endpoint. A local-file simulation is only valid if it independently satisfies every documented AWS error-code/exit-code/JSON-shape behavior identically (harder to get right, riskier, but not automatically wrong).
- **Shorthand parsing**: Full argparse-style shorthand grammar (with escaping, nested structures) vs. the reference's simpler comma/equals splitter — both fine as long as the observed argv patterns in the spec parse correctly.
- **Error message format**: Any of the three documented shapes (service envelope, bare `Code: message`, or `usage:`/`Parameter validation failed:`/`Unknown options:` prefixed usage lines) is acceptable — implementers are free to choose either format per error class.
- **Exit code granularity**: Using `1` or `255` instead of `254` for non-listed application failures is fine; only the specific exit codes enumerated in the "Error cases" per command are strictly checked.
- **Output formatting**: pretty-printed vs. compact JSON, any key ordering — tests parse JSON, not text-match.

## Known pitfalls

- **Validating flags/JSON before checking required fields**: order matters little as long as any usage problem yields `252`, but a common bug is calling the network before validating (e.g. missing `--item` should never reach the server).
- **Numbers as native JSON**: converting shorthand `N=5` into `{"N": 5}` (a number) instead of `{"N": "5"}` (a string) breaks the DynamoDB AttributeValue contract explicitly called out in the spec.
- **Duplicate flags not rejected**: `--table-name X --table-name Y` must be a `252` usage error, not silently taking the last value (a subtle but explicitly tested case).
- **Table-name oversized (512 chars) treated as `252` even though it superficially resembles domain data** — must not be forwarded to the server as a runaway request causing a different exit code (e.g., `254` from server-side validation would be wrong per spec).
- **Mixing stdout/stderr**: printing partial JSON to stdout before detecting a later error, or writing error text to stdout, violates the strict separation requirement.
- **Swallowing exceptions into stack traces**: any unhandled Python/Node exception dumping a traceback to stderr must be caught and converted into a clean one-line message.
- **Ignoring `--billing-mode PAY_PER_REQUEST` special-casing**: provisioned-throughput values should not cause failures when billing mode is `PAY_PER_REQUEST` — don't require `--provisioned-throughput` when `PAY_PER_REQUEST` is set, and don't error out due to it being absent.
- **Key-schema/attribute-definitions mismatch validation**: this should be *server-driven* (`ValidationException` from the endpoint), not client-invented; over-eager client-side validation risks wrong exit code or message class if implemented incorrectly.
- **Recreating an existing table**: must surface `ResourceInUseException` (from server) rather than being silently swallowed or crashing.
- **`get-item`/`query` mentioned in cross-command flow**: even though not in the four required subcommands' explicit flag tables, the overall program must maintain consistent backing state such that separately-tested `get-item`/`query` behavior (if tested elsewhere in the suite) still reflects `put-item` writes — reinforcing that all commands must hit the same durable backend.
- **Not exiting immediately with correct code after usage error** — remember exit code call must actually happen (`sys.exit`/`process.exit`), not just print and fall through to code that still tries the network call.

## Cheat surface

- **Hardcoding fixed JSON responses** for `create-table`/`describe-table`/`put-item`/`scan` without actually persisting/reading real state would pass a naively shallow test but fail cross-command state checks (create→list, put→get) and is explicitly guarded against by the "state must remain consistent" requirement.
- **Ignoring `--condition-expression`** and always succeeding `put-item` would fail the `ConditionalCheckFailedException` test on re-put with `attribute_not_exists`.
- **Skipping duplicate-key/malformed-JSON detection and always returning 252 for everything** would fail success-path tests requiring exit `0` and real JSON output.
- **Fabricating flags/behavior not in the documented flag list** (e.g., inventing a `--force` flag) is explicitly disallowed by the instructions and likely tested by the `--not-a-real-flag` cases expecting `252`.
- **Client-side table-name format validation** (e.g. regex-checking allowed characters) is explicitly disallowed — the spec says not to validate table names client-side; doing so could produce wrong exit codes for legitimate-but-unusual names the service would accept.
- **Printing to both stdout and stderr on the same invocation** (e.g., logging progress info) would break the strict separation checks even if functionally correct otherwise.

## Success criteria

- All four subcommands parse only their documented flags; any unknown flag, duplicate flag, missing required flag, empty flag value, or malformed inline JSON yields exit `252` with stderr-only output and no network call.
- Oversized table-name values yield exit `252`.
- Valid `create-table` calls succeed (`0`), appear in subsequent `list-tables`-equivalent state, and recreating the same name fails with `ResourceInUseException`-class message at exit `254`.
- `key-schema`/`attribute-definitions` mismatches surface as `ValidationException`-class errors at exit `254`.
- `put-item` writes are durably visible to a later `get-item` call (same key) in a separate process invocation; conditional-expression failures on existing keys leave stored data unchanged and report `ConditionalCheckFailedException` at exit `254`; writes to nonexistent tables report `ResourceNotFoundException` at exit `254`.
- Numbers in items/keys always serialize/round-trip as `{"N": "<string>"}`.
- `scan` and `describe-table` against an as-yet-uncreated/nonexistent table report a modeled error at exit `254`.
- On every success path, stdout contains valid, `json.loads`-parseable DynamoDB response JSON and stderr is empty; on every failure path, stdout is empty and stderr contains a one-line, class-identifiable error message with no stack trace.
- Exit codes used are strictly within `{0, 1, 252, 254, 255}`, matching the specific code required for each enumerated error case in the spec.