# TRUTH: f31f67cf-f1e4-46f8-b9b4-152255ec8ad6

## Problem

Implement a single executable `aws` on `$PATH` that emulates the subset of the real `aws cognito-idp` CLI needed to manage user pools, app clients, users, and groups, entirely through a stateful backend service (reachable via the standard AWS SDK/HTTP endpoint environment variables) — without shelling out to the real `aws` binary or `awscli` package. The program dispatches on `sys.argv[2]` (the subcommand token) after the literal `cognito-idp` service name, translates CLI flags into a JSON request body, sends it to the cognito-idp-compatible endpoint, and renders the JSON response (or a clean error) according to a strict stdout/stderr/exit-code contract.

## Behavioral contract

- Invocation: `aws cognito-idp <command> [--flag value ...]`.
- Success: prints exactly one JSON document to stdout (parseable by `json.loads`); stderr is empty; exit code `0`.
- Failure: stdout is empty; stderr has one human-readable line naming the error class (service error envelope, bare `<Code>: <msg>`, or a client usage-error prefix like `usage:`, `Parameter validation failed:`, `Unknown options:`); exit code is one of `{1,252,254,255}` (never 0, never a raw traceback).
- All 28 listed commands must be dispatchable; each accepts (at minimum) the flags enumerated in the task for that command, translated to the correct request field names/shapes.
- Cross-command state consistency must hold for a single running instance of the backing service across the whole test session: creates/updates/deletes performed by one command must be visible to every other command that reads related state (see Cross-command behavior in the instructions). This means the CLI itself should be effectively stateless per-invocation — all persistent state lives in the backend service, not in local files — so that any sequence of separate subprocess invocations behaves consistently.
- Deleting a user pool cascades: subsequent operations against its id, or its clients/users/groups, must fail with a resource-not-found error class.
- Duplicate resource creation (e.g., same username, same pool) must fail with the correct modeled exception class (e.g. UsernameExistsException, ResourceNotFoundException) rather than silently succeeding or crashing.
- No client-side semantic validation should reject input the service would accept (e.g., don't hand-roll password-strength or attribute-name checks) — let the backend enforce modeled validation and surface its error. Basic argument-shape checks (unknown flag, missing required flag, malformed JSON/int) are appropriate client-side usage errors (exit 252).
- Never emit an interpreter stack trace under any failure condition — catch and convert to the required stderr line format.

## Solution decomposition

1. **CLI argument parsing**: recognize `cognito-idp` as the service, dispatch on subcommand name, map each `--kebab-case-flag` to the correct JSON field name and value type (string, int, JSON blob, comma/JSON list, shorthand attribute list `Name=..,Value=..`, boolean flags like `--permanent`/`--no-permanent`). Reject truly unknown flags and missing required flags with a usage error (exit 252) without contacting the backend.
2. **Request construction**: build the JSON request body matching the real Cognito Identity Provider API shapes (e.g. `UserAttributes` as list of `{Name, Value}`, `CustomAttributes` as schema-attribute objects, group/user/pool identifiers as top-level string fields).
3. **Transport to backend**: send an HTTP POST to the endpoint configured via environment (do not hardcode/override endpoint, region, or credentials — read them from env as already set up), using the `X-Amz-Target: AWSCognitoIdentityProviderService.<OperationName>` convention (JSON RPC-style protocol used by Cognito). Any authentication header is cosmetic/dummy since credentials/endpoint are pre-provisioned by the harness.
4. **Response handling**: on 2xx, parse and print the JSON body to stdout (some operations return an empty/void body — print `{}` or omit body per shape, but never print nothing when JSON is expected and never mix stdout with error text). On HTTP error, extract the service error code/message and print it to stderr in one of the accepted shapes, mapping the HTTP status/exception to an appropriate exit code (254 for modeled service errors is the natural mapping; 255 for transport-level failures).
5. **Timestamp/number formatting**: convert epoch-time numeric fields (creation/modification dates, etc.) to a consistent JSON-serializable representation (ISO8601 string or numeric) so the output is valid, parseable JSON — exact representation is not graded beyond being valid JSON with correct semantic values.
6. **Per-command mapping table**: a declarative table mapping subcommand → (operation name, required params, whether the response body is typically empty) covering all 28 commands, used to drive required-arg checking and dispatch.
7. **Error class fidelity**: ensure that operations which the spec calls out for specific error classes (admin-create-user duplicate → UsernameExistsException-class, missing pool/user/group → ResourceNotFoundException-class / UserNotFoundException-class) surface the backend's real error rather than a generic message, since state and validation logic lives server-side.

## Solution space

Multiple structurally different implementations are equally valid:

- **Any language** (Python, Node, Go, Bash+jq, etc.) as long as the final executable is named `aws` and lives on `$PATH` (the `/workspace/submission/` convenience directory or elsewhere).
- **Any HTTP client / SDK** to talk to the backend: raw sockets, `curl` invoked from a script, a language's built-in HTTP library, or a bundled (pre-existing, not newly-fetched) AWS SDK for that language, as long as it does not shell out to the real `aws` CLI/awscli package and does not override endpoint/region/credential env vars.
- **Argument parsing** may use a hand-rolled parser, `argparse`, a generic getopt library, or manual token scanning — as long as unknown/missing/malformed flags produce exit 252 with a usage-shaped message and valid input passes through.
- **Attribute/list shorthand parsing** could support only JSON syntax, only comma/`Name=Value` shorthand, or both — either is fine as long as the documented `--user-attributes`/`--custom-attributes`/`--user-attribute-names` inputs used by the tests are accepted and translated correctly into the request.
- **Op-name derivation** could use a static per-command lookup table (as in the reference) or a generic transform of the kebab-case subcommand to PascalCase (e.g., `admin-create-user` → `AdminCreateUser`) — either is acceptable as long as it matches the real API's operation names.
- **Response rendering**: pretty-printed or compact JSON, any key ordering, any timestamp encoding (numeric epoch, ISO string, RFC3339) — since tests assert on parsed JSON semantics only.
- **Error message formatting**: any of the three documented shapes (full AWS envelope, bare `Code: message`, or usage-error prefix) — a solution need not replicate the exact reference wording.
- **State storage**: the CLI process itself is stateless (all mutable state lives in the external backend service); a solution that instead implements its own local mock backend (e.g. writing to a local file/DB) would only be valid if the harness's "AWS endpoint" env vars actually point at that local mock — but per the task, credentials/endpoint are pre-set by the harness to point at a real backing service, so implementations should talk to that endpoint rather than inventing local persistence. (If the harness is self-contained with its own mock server already listening on the configured endpoint, then the CLI's only job is a thin protocol-translating client, not a full mock implementation.)

## Known pitfalls

- **Mixing stdout/stderr**: printing a warning or debug line to stdout before/after the JSON breaks `json.loads` parsing of stdout on success; printing JSON error bodies to stdout instead of stderr on failure is a correctness bug.
- **Leaking tracebacks**: unhandled exceptions (e.g. `KeyError`, `JSONDecodeError`, connection errors) must be caught and converted to a one-line stderr message with a non-zero exit, never a Python/Node stack dump.
- **Wrong exit code for success**: any exit code other than 0 on a successful call is a failure regardless of stdout content.
- **Client-side over-validation**: rejecting values the service would actually accept (e.g. custom regex checks on username/password) can incorrectly turn a should-succeed case into a usage error, or vice versa turn a should-fail case into a false success.
- **Not treating `--permanent`/`--no-permanent`-style boolean flags correctly** (requiring a value argument for boolean-only flags, or vice versa).
- **Required-arg checking mismatches**: e.g. `list-user-pools --max-results` is actually mandatory per the real CLI model even though instinctively it looks optional — required-arg tables must match the true API model, not just the instruction's flag list, to avoid both false-usage-errors and false-passes.
- **Losing cross-command state** by keeping any pool/user/group data in local process memory or a local file instead of relying on the shared backend — since each CLI invocation is a fresh subprocess, any local-only state vanishes between commands and breaks the cross-command consistency requirements.
- **Not cascading deletes**: forgetting that `delete-user-pool` must also make its clients/users/groups unreachable (resource-not-found), if the CLI (rather than backend) were responsible for such bookkeeping.
- **Timestamp field type mismatches**: emitting raw epoch floats without conversion can still be valid JSON, so this isn't strictly required, but inconsistent typing (e.g. sometimes string, sometimes number) across responses could confuse tests that inspect specific timestamp fields — safest bet is a single consistent convention.
- **Attribute shorthand ambiguity**: not accepting both JSON-array-of-objects and CLI shorthand (`Name=x,Value=y`) forms for `--user-attributes` could break tests that use whichever form is common in `aws` CLI conventions.
- **Overly strict unknown-flag detection**: rejecting a flag documented in the instruction's flag list for a command as "unknown" because it's missing from an internal table would produce false usage errors on otherwise-valid invocations.
- **Fabricating flags not in the real API** (explicitly disallowed) — adding invented parameters could cause validation mismatches server-side.

## Cheat surface

- Hardcoding fixed/canned JSON responses per command without actually calling a stateful backend would fail any cross-command consistency test (e.g., create then get, create then list, delete then verify absence) since state wouldn't actually persist or change.
- Faking success unconditionally (always exit 0, always print `{}`) would fail negative-path tests expecting `UsernameExistsException`/`ResourceNotFoundException`/`UserNotFoundException`-class errors and specific exit codes.
- Swallowing all errors and turning them into generic exit 1 without correct classification wording would fail failure-class-matching tests that check for a recognizable error-code-shaped stderr line.
- Implementing local file-based fake persistence that isn't shared/visible to the actual test harness's checks (if the harness inspects state via separate `aws` invocations rather than trusting only your own commands) risks losing state between subprocess calls if not properly durable — must genuinely delegate to the configured backend endpoint rather than simulate.
- Printing both a preamble/log line and the JSON body to stdout on success (e.g., "Calling AWS..." followed by JSON) would break `json.loads` parsing.
- Shelling out to the real `aws` CLI or importing `awscli` package is explicitly forbidden and would be a spec violation even if it "worked."
- Overriding `AWS_ENDPOINT_URL`/region/credentials in code to point somewhere else than the harness-provided environment values is explicitly forbidden.

## Success criteria

- For every one of the 28 commands, valid invocations return exit 0, empty stderr, and a stdout JSON document containing the semantically correct fields (ids, names, attributes, statuses, membership lists) reflecting actual accumulated state from prior commands in the same test sequence.
- Cross-command sequences (create pool → create client/user/group → mutate → read back → delete → verify absence/cascade) behave consistently exactly as described in "Cross-command behavior," independent of key order or list order.
- Documented negative-path commands (duplicate username, missing pool/user/group/client) fail with the correct error class in stderr, empty stdout, and a non-zero exit code drawn from `{1,254,255}` as appropriate (typically 254 for modeled service exceptions).
- Malformed/unknown CLI usage (bad flag, missing required flag, invalid JSON/int argument) is rejected client-side with a usage-error-shaped stderr line and exit code 252, without contacting the backend.
- No test observes a stack trace, mixed stdout/stderr content, or an exit code outside `{0,1,252,254,255}`.
- The executable is discoverable as `aws` on `$PATH` and correctly dispatches only when invoked as `aws cognito-idp <command> ...`.