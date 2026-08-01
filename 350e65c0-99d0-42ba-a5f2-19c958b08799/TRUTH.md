# TRUTH: 350e65c0-99d0-42ba-a5f2-19c958b08799

## Problem

Implement a single executable `aws` on `$PATH` that emulates `aws kms <subcommand>` for twelve commands: `cancel-key-deletion`, `create-alias`, `create-key`, `decrypt`, `delete-alias`, `describe-key`, `disable-key`, `enable-key`, `encrypt`, `list-aliases`, `list-keys`, `schedule-key-deletion`. The program must dispatch on the subcommand token, talk to a KMS-compatible backend service reachable via environment-provided credentials/endpoint, and maintain state consistency across an entire test session (keys, aliases, and key states created/modified by one invocation must be visible to later invocations, since each subcommand is a separate subprocess and state lives server-side, not in the CLI process).

## Behavioral contract

- Invocation: `aws kms <command> [--flag value ...]`. Unknown commands/flags/missing required args → usage error, exit 252, message on stderr (no traceback).
- Success: JSON response object written to stdout only (parseable via `json.loads`), stderr empty, exit 0.
- Failure at the service layer: stdout empty; stderr contains a human-readable line naming the error class (one of: full AWS envelope `An error occurred (<Code>) ...`, bare `<Code>: <message>`, or a client usage-error prefix); exit code in `{1, 252, 254, 255}` as appropriate (254 for modeled service exceptions is the natural choice, but any non-zero in the declared set passes since tests only check `returncode != 0` plus stderr content matching the class).
- No raw stack traces ever, on any path.
- No hard-coded region/credentials/endpoint override in code — must be picked up from environment.
- Must not shell out to real `aws`/awscli, must not fetch extra packages.
- Cross-command state consistency:
  - `create-key` → key visible in `list-keys`/`describe-key`, usable by crypto ops.
  - `encrypt`→`decrypt` round-trips to original plaintext; key id returned matches the key that encrypted.
  - `disable-key` blocks crypto ops (disabled-key error) until `enable-key`.
  - `schedule-key-deletion` puts key into pending-deletion (visible in `describe-key`), blocks crypto use; `cancel-key-deletion` returns it to disabled state (needs subsequent `enable-key` to use again).
  - `create-alias`/`delete-alias` reflected in `list-aliases`; duplicate alias → already-exists error; alias targeting a missing key → not-found error.
  - Missing-key operations (`describe-key`, `encrypt`, `decrypt`, `create-alias` target, delete/cancel/enable/disable/schedule on nonexistent key) → `NotFoundException`-class error.

## Solution decomposition

1. **Argument parsing per subcommand**: each command has its own flag set (see instruction's per-command Flags list). Must accept `--flag value` and reasonably `--flag=value`; reject unknown flags/missing required values with a usage-class error and exit 252. Must NOT client-side-validate semantic content (e.g. enum values, key-id format) — that validation must come from the service ("do not validate input client-side").
2. **Backend transport**: the CLI needs to actually store/mutate key state somewhere durable across process invocations. The reference does this by calling a KMS-compatible HTTP service (e.g., a local emulator like LocalStack) already configured via environment endpoint/credentials env vars, using AWS JSON-1.1 protocol (`X-Amz-Target: TrentService.<Op>`). This is the only way state persists correctly across many separate subprocess invocations without the CLI itself running a daemon.
3. **Dispatch table**: map each of the 12 subcommand names (and by implication the sibling operations mentioned in cross-command behavior, e.g. `generate-data-key`, `re-encrypt`, `sign`, `verify`, `generate-mac`, `verify-mac`, `list-resource-tags`, `get-key-rotation-status`, `get-key-policy` — only if those are separately tested; note the declared command list for THIS task is the 12 listed, so those extra ones are cross-command narrative context but not necessarily graded subcommands here) to its handler function, each building the correct request payload field names (PascalCase API names) from parsed CLI flags.
4. **Response shaping**: translate the service's JSON response into the shape `aws kms <cmd>` normally emits (i.e., pass through the service's own response body as JSON to stdout) — this naturally satisfies "parseable JSON, semantic content only" since assertions don't care about key order/whitespace.
5. **Error translation**: on HTTP error / service exception, print an error line to stderr identifying the error code/class (from the service's error envelope, e.g. `__type`/`message` fields) and exit non-zero, never leaking a raw traceback.
6. **Blob/text argument handling**: `--plaintext`, `--ciphertext-blob` are base64 KMS blob values; must support raw base64 strings (and optionally `fileb://`/`file://` prefixes as AWS CLI conventionally does) without altering semantics — service handles actual validation.
7. **Special-case business flows**:
   - `cancel-key-deletion` → key ends in **disabled** state (not enabled) per spec — a deliberate nuance to encode/pass through correctly (whatever the backing service does; CLI must not reinterpret/override it).
   - `create-key` defaults: no `--key-usage` → symmetric ENCRYPT_DECRYPT; `SIGN_VERIFY` → asymmetric spec; `GENERATE_VERIFY_MAC` → HMAC spec. This is typically handled correctly automatically if the CLI passes through whatever `--key-usage`/`--key-spec`/`--customer-master-key-spec` flags the user gave to the service unmodified — the service enforces the default itself. If a chosen backend does NOT default correctly, the CLI would need to supply a default itself, but per "do not validate/fabricate client-side," the preferred path is trusting the backend.
   - Pagination flags `--limit`/`--marker` for `list-keys`/`list-aliases`: when omitted, some implementations auto-paginate through all pages and aggregate; when supplied, pass through as single-page semantics. Either behavior is acceptable as long as output shape matches AWS's (`Keys`/`Truncated`/`NextMarker` or `Aliases`/...).

## Solution space

Multiple valid architectures satisfy this contract:

- **Thin proxy to a real KMS-protocol backend** (reference approach): CLI is essentially a translator from `aws kms` CLI syntax to raw AWS JSON-1.1 HTTP calls against an already-running KMS-compatible endpoint (e.g. LocalStack) configured via env vars, passing responses/errors straight through. This requires zero cryptographic logic in the CLI itself.
- **Self-contained stateful server + client**: CLI could itself implement the KMS semantics (create/store keys, encrypt/decrypt with real crypto, aliases, state machine) using a local persistent store (file/sqlite in a fixed shared location) so that repeated `aws` invocations share state. This is valid as long as: state persists across process invocations, crypto round-trips work, and errors/format match the contract. This avoids reliance on an external service but is far more implementation work and must independently implement all the state-machine edge cases (disabled/pending-deletion blocking crypto, not-found, already-exists, etc.).
- **Language choice**: Python, Go, Node, shell+jq, etc. — anything available in the base image, provided no extra packages are fetched. The reference uses Python's stdlib `urllib`; using `boto3`-like hand-rolled signing or a vendored SDK already present in the image would also be acceptable as long as it isn't literally calling the `awscli`/`aws` binary.
- **Error/exit-code mapping**: any exit code in `{1,252,254,255}` for failures is acceptable; a solution that always uses 1 for all service errors and 252 only for usage errors is equally valid to one that uses 254 for modeled exceptions.
- **Pagination**: auto-aggregating all pages by default vs. requiring `--marker`-based paging are both acceptable, as long as `--limit`/`--marker` supplied explicitly behave sensibly and unpaginated calls return the full/expected key set that later assertions rely on (since tests check "reflects the cumulative effect" and "every key created so far").

## Known pitfalls

- Mixing stdout/stderr: writing partial JSON to stdout before an error occurs, or writing error JSON to stdout instead of stderr, breaks the "stdout empty on failure" / "stderr empty on success" contract.
- Emitting Python/Go tracebacks on unexpected exceptions (e.g., file-not-found for blob args, JSON decode errors) — must be caught and turned into a clean one-line message with non-zero exit.
- Client-side validating enum/format values (e.g. rejecting an unrecognized `--encryption-algorithm` before calling the service) — spec explicitly says not to do this; the service should be the source of truth for validation errors.
- Fabricating flags not in the documented flag list per command (e.g., adding a made-up `--force` flag) — instruction explicitly forbids inventing flags.
- Treating `cancel-key-deletion` as fully re-enabling the key (returning to `Enabled`) instead of `Disabled` — subtle state-machine bug that breaks the documented sequence (`cancel-key-deletion` → still need explicit `enable-key`).
- Overriding region/endpoint/credentials in code instead of reading them from the environment — breaks test harness assumptions about routing to its backend.
- Not persisting state across process invocations (e.g., keeping an in-memory dict inside the CLI process) — since each `aws kms ...` call is a fresh subprocess, any state kept only in-process is lost; keys/aliases must be durable somewhere the next invocation can see (backend service or a shared file/db).
- Hard-failing on the global boilerplate AWS CLI flags (`--region`, `--output`, `--no-paginate`, etc.) that the harness may or may not pass — a correct parser should tolerate/ignore recognized global flags rather than erroring as "unknown flag."
- Silently swallowing `--dry-run` incorrectly — this flag should be forwarded so the backend can respond with its own DryRunOperation semantics rather than the CLI faking success/failure itself.
- Confusing which state blocks crypto: both `Disabled` and `PendingDeletion` must block encrypt/decrypt/sign/etc. with distinct-but-appropriate error classes (`DisabledException` vs invalid-state style errors) — not conflating them into one generic error.

## Cheat surface

- Always exiting 0 and printing plausible-looking canned JSON without ever actually calling a backend or performing crypto — would fail round-trip (`encrypt`→`decrypt` must recover original plaintext) and cross-command visibility tests (`list-keys` after `create-key`).
- Hardcoding a single fake key id / alias and ignoring `--key-id`/`--alias-name` inputs — fails multi-key/multi-alias sequential test scenarios and not-found error paths.
- Skipping error-class differentiation and just printing `Error: failed` for every failure — fails tests asserting the specific error-class shape (e.g., `NotFoundException`) is present in stderr.
- Storing state only in a local file scoped to a single test's tmp dir path in a way that isn't actually shared across the specific invocations the grader makes (e.g., using `/tmp/pid-specific` paths) — silently breaks cross-command consistency while appearing to pass simple single-command smoke tests.
- Ignoring `--plaintext`/`--ciphertext-blob` content and returning a fixed ciphertext/plaintext — passes shape checks but fails identity/round-trip semantic checks.
- Not implementing the pending-deletion/disabled blocking logic, letting `encrypt`/`decrypt` succeed on disabled/pending keys — passes state-transition commands individually but fails the cross-command "blocks cryptographic use" assertions.

## Success criteria

- All 12 commands parse their documented flags correctly, reject unrecognized flags/missing required args with usage-class stderr output and exit 252.
- Successful invocations print only valid JSON to stdout, with stderr empty, exit 0.
- Failed invocations print only an error line naming the error class to stderr, with stdout empty, exit code in `{1,252,254,255}`.
- No raw stack trace ever appears on stderr.
- `create-key` → key appears in subsequent `list-keys` and `describe-key` calls (same process invocation boundary — state persists via external/shared store).
- `create-alias`/`delete-alias` correctly change `list-aliases` output; duplicate-alias and missing-target-key produce appropriate error classes.
- `encrypt` then `decrypt` on the resulting ciphertext returns the original plaintext (base64-equal) and correct key id.
- `disable-key` → subsequent `encrypt`/`decrypt` on that key fail with a disabled-key error class; `enable-key` restores crypto capability.
- `schedule-key-deletion` → `describe-key` shows pending-deletion state and crypto ops fail; `cancel-key-deletion` moves it to disabled (not enabled); a further `enable-key` restores crypto capability.
- `describe-key`/other commands on a nonexistent key id return a not-found error class with non-zero exit.
- No network/service address, region, or credential values are hardcoded/overridden in the submitted code — environment values are used as-is.
- No shelling out to `awscli`/`aws`, and no additional packages fetched beyond what the base image provides.