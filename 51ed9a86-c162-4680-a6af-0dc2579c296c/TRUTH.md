# TRUTH: 51ed9a86-c162-4680-a6af-0dc2579c296c

## Problem

Implement a single executable named `aws` on `$PATH` that emulates the subset of the real `aws cognito-idp` CLI covering eight subcommands: `admin-create-user`, `admin-get-user`, `create-user-pool`, `create-user-pool-client`, `delete-user-pool`, `describe-user-pool`, `list-user-pools`, `list-users`. The program dispatches on `argv[1] == "cognito-idp"` and `argv[2] == <subcommand>`, parses AWS-CLI-style `--flag value` arguments, talks to a Cognito Identity Provider-compatible backend endpoint (reachable via environment-provided credentials/endpoint, e.g. a local emulator such as LocalStack/moto), and returns JSON on stdout for success or a classed error message on stderr with an appropriate exit code. State (pools, clients, users) must be durable across separate invocations of the program because each command is a fresh subprocess — the backing service, not the CLI process, is the source of truth.

## Behavioral contract

- Invocation shape: `aws cognito-idp <command> [--flag value ...]`.
- Every flag listed per-command in the instruction must be accepted; any flag not listed for that command is an unknown-flag usage error. Flags may be no-ops as long as they are accepted and, where semantically required (e.g. affecting output), applied.
- Required flags per command (as enumerated in the task) must be enforced; missing → usage error, exit 252.
- Unknown flags, repeated flags, empty flag values → usage error, exit 252.
- Field length/range constraints must be enforced by the CLI *or* legitimately delegated to the backend service returning a validation error — but per "Implementation constraints," client-side value validation beyond documented length/range limits explicitly listed under "Argument validation" should not invent additional rules. The listed length/range checks (pool-id ≤55, username ≤128, filter ≤256, temp-password ≤255, max-results/limit 1–60, generic 512-char oversized value cap) are required checks that must yield exit 252 somewhere in the pipeline (client or service-forwarded).
- A well-formed reference to a nonexistent resource (unknown pool id, unknown username, etc.) is a service error: exit 254 (or 1/255 acceptable per contract, but 254 is the documented modeled-error code).
- stdout carries only the JSON success payload (parseable via `json.loads`), nothing else. stderr carries only the one-line error message on failure. Never both populated in the same invocation.
- No raw stack traces ever, regardless of error origin (network failure, backend exception, bad JSON, etc.).
- Exit code must be one of {0,1,252,254,255}, matching the class: 0 success, 252 usage, 254 modeled service error, 1/255 other.
- Cross-command consistency: created pools/users/clients must be visible to subsequent list/describe/get commands in later, independent process invocations; deleted pools must disappear from listings and cause service errors on describe/use.

## Solution decomposition

1. **Argument parser**: generic `--flag value...` tokenizer per subcommand-specific flag spec; supports list-valued flags (space or comma separated tokens after a flag), required-flag enforcement, unknown-flag rejection, missing-value rejection, JSON-valued flags (parse or pass through raw), oversized-value rejection.
2. **Command dispatch table**: one branch/handler per of the 8 subcommands, each: parse args → validate required/lengths → build a request payload → call backend operation → map response/error to stdout/stderr+exit code.
3. **Backend transport**: an HTTP(S) client hitting the Cognito Identity Provider JSON-1.1 protocol (`X-Amz-Target: AWSCognitoIdentityProviderService.<Op>`) at whatever endpoint the environment specifies (env var driven — must not hardcode a real AWS region/endpoint override in violation of "do not override... endpoint... in code"; reading from env is fine, hardcoding a fallback default is a judgment call but should not force a specific non-default endpoint when one is supplied by env). Alternative: use boto3 if present in the image (not "awscli", so allowed) since it already implements auth signing, error mapping and pagination — this is likely simpler and more robust than hand-rolled HTTP+SigV4.
4. **Response formatting**: convert backend JSON response into AWS-CLI-shaped JSON (top-level operation output, e.g. `{"UserPool": {...}}`, `{"User": {...}}` etc., matching typical aws-cli field naming), serialize with `json.dumps` to stdout, exit 0.
5. **Error mapping**: catch HTTP/service error responses (or boto3 `ClientError`), extract error code/type and message, emit one of the accepted stderr shapes, choose exit code (254 for modeled service exceptions such as `ResourceNotFoundException`, `UserNotFoundException`; 252 for parameter validation raised by the parser before any network call; 255/1 for transport/unexpected failures).
6. **Persistence**: rely entirely on the external service/emulator for state; the CLI itself is stateless across invocations. No local file-based state should be needed if a real backend is reachable per test harness setup.

## Solution space

Multiple implementation strategies are equally valid:

- **boto3-based**: construct a `boto3.client("cognito-idp", ...)` using ambient env credentials/endpoint (via `AWS_ENDPOINT_URL` / service-specific endpoint override env vars already set in the environment — do not pass a hardcoded `endpoint_url` unless reading it from env), call the corresponding `client.<operation>(**kwargs)` method with kwargs built from parsed flags, catch `botocore.exceptions.ClientError`/`ParamValidationError` and map to output. This avoids hand-rolling SigV4 signing and JSON protocol framing.
- **Raw HTTP + manual signing/JSON-1.1 protocol** (as in the reference): construct request bodies manually per operation, sign or stub-sign requests, parse JSON error envelopes (`__type`/`message`) directly. Valid but more error-prone (must get header/target names exactly right per operation).
- **Local in-memory/file-backed state** (only valid if the test harness does not spin up a real backend and only checks single-process sequences via a shared file/DB) — risky given the spec says commands run as independent subprocesses; a durable local JSON-file-based store keyed by env-provided identifiers (e.g., an endpoint or workspace-scoped path) would also satisfy cross-command consistency as long as it survives across separate `aws` invocations. This is a legitimate alternative if no live backend is available in the test environment, but the safer, more likely-correct route mirrors the real service via the network endpoint provided by env vars.
- Any language may be used (Python, Go, Node, etc.) as long as `/workspace/submission/aws` (or another `$PATH` entry) is invoked correctly with subprocess semantics matching argv passing.
- Flags marked "ignore" (complex JSON configs with no visible behavioral effect in the tests) may be accepted and dropped, or accepted and forwarded verbatim to the backend — both are fine since tests assert on JSON semantic content, not full echoing of every input field, unless the instruction implies otherwise (e.g., generated `UserPoolId`, `ClientId`, timestamps).

## Known pitfalls

- Treating `--flag -123` (a negative-looking value) as a new flag token because it starts with `-`: the value-collection loop must not confuse valid non-flag values (including JSON blobs starting with `{`/`[`, or numeric strings) with flags. The reference's heuristic (`--foo` only counts as a new flag if char after `--` is non-digit) illustrates the risk of naive `--` detection.
- Mixing stdout/stderr — printing partial JSON before hitting an error, or writing library warnings to stdout.
- Leaking tracebacks from any unhandled exception (JSON decode error, network error, KeyError from missing response field) — must be wrapped in a catch-all that degrades to a class-labeled stderr line and exit 255/1.
- Serializing datetime/epoch timestamp fields incorrectly — AWS CLI emits ISO8601, and boto3 returns Python `datetime` objects by default requiring a custom JSON encoder (or converting epoch floats to ISO8601 if using raw HTTP JSON responses). Getting this wrong can break `json.loads`-parseable assertions if datetimes leak through unhandled (e.g., raise `TypeError: Object of type datetime is not JSON serializable`, crashing partway through printing = mixed/broken stdout).
- Forgetting to enforce a required flag before making a network call (must validate offline where possible to get exit 252, not 254, since server-side "missing required field" is still a service-level ValidationException in real Cognito’s protocol, but the instruction explicitly wants missing-required-flag as CLI usage error 252, not delegated to the service).
- Over-validating: task explicitly says "Do not validate input client-side; the service rejects malformed input with a validation error" — except for the specific enumerated length/range checks. Adding extra client-side business validation (e.ks. username format regex) beyond the documented list is unnecessary and could produce wrong exit-code classification if it diverges from real service behavior on edge cases actually tested.
- Case sensitivity / exact flag spelling, e.g. `--callback-ur-ls`, `--logout-ur-ls`, `--allowed-o-auth-flows` — these unusual AWS CLI flag names (camel-case abbreviations split oddly) must be matched exactly as specified, not "corrected" to more natural spellings.
- Repeated flags should error (252), not silently take last-value — a naive dict-based accumulation would silently allow repeats.
- Empty flag value (flag present but immediately followed by another flag or end of argv) must be a usage error, not treated as flag absent or empty string accepted.
- `--max-results`/`--limit` bounds (1–60) must be enforced exactly at the boundaries (0 and 61 must fail; 1 and 60 must pass).
- Length boundaries are "N or more is an error," i.e., strictly-greater-than-limit-minus-one — off-by-one errors here (using `<=` vs `<`) are an easy mistake (e.g. 512 chars is invalid, 511 is valid; 55-char pool id valid, 56 invalid).
- Deleted-pool residual state: after `delete-user-pool`, `describe-user-pool`/`list-users`/`admin-get-user` for that pool must yield service errors, not stale cached success — this requires the backend to actually be mutated, so a fully faked/local success-only implementation that doesn't track deletions would fail here.

## Cheat surface

- Hardcoding fixed/sample JSON responses without actually calling a backend would fail cross-command consistency tests (pool created in one process must be visible in the next), unless a real backend is used, so a "fake it" static-response approach cannot pass more than isolated single-command shape checks.
- Silently swallowing and always exiting 0 regardless of backend errors — must be caught by tests requiring exit 254 on nonexistent resources and 252 on bad params.
- Broadly catching all exceptions and mapping every failure to the same exit code/message, losing the required class distinction between usage (252) vs modeled service (254) vs other (255/1) errors.
- Passing all flags straight through to boto3/the backend and letting botocore raise its own `ParamValidationError` for *every* validation family, then reporting exit 252 for e.g. "resource not found" caught as a generic client error — must distinguish `ParamValidationError`/client-side arg errors (252) from `ClientError` with a modeled AWS exception name (254).
- Reproducing an "always succeeds" `create-user-pool`/`admin-create-user` that never persists (in-memory dict reset per process) — breaks the required cross-invocation state persistence since tests invoke the CLI as separate subprocess calls.
- Shelling out to real `awscli`/`aws` binary or importing `awscli` package — explicitly forbidden.
- Overriding region/endpoint/credentials in code instead of reading from the environment — explicitly forbidden and likely breaks the test harness's ability to point the CLI at its mock backend.

## Success criteria

- All 8 subcommands are dispatched correctly from a single `aws` executable on `$PATH`.
- For every documented flag combination, correct required-flag/length/range validation triggers exit 252 with a class-identifying stderr message, and stdout is empty.
- For well-formed requests referencing missing resources (unknown pool/user/client), exit 254 (or another accepted non-zero code) with a class-identifying stderr message naming the service error, and stdout is empty.
- For successful invocations, stdout is exactly one JSON document parseable by `json.loads`, containing the operation's expected top-level result object with correctly-typed fields (including generated IDs and ISO8601-ish timestamps if present), and stderr is empty.
- Cross-command sequences behave consistently: a pool created via `create-user-pool` shows up in `list-user-pools`/`describe-user-pool`; a client created via `create-user-pool-client` requires a real prior pool; a user created via `admin-create-user` shows up in `list-users`/`admin-get-user`; a deleted pool disappears from listings and produces service errors on subsequent access — all verified across separate subprocess invocations of the CLI.
- No stack traces ever appear in stderr/stdout; exit code is always drawn from `{0,1,252,254,255}`.