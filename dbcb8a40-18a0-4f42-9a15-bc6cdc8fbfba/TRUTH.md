# TRUTH: dbcb8a40-18a0-4f42-9a15-bc6cdc8fbfba

## Problem

Implement a single executable `aws` on `$PATH` that emulates the `aws kms` CLI surface for ten subcommands (`create-alias`, `create-key`, `decrypt`, `describe-key`, `disable-key`, `encrypt`, `generate-data-key`, `list-aliases`, `list-keys`, `schedule-key-deletion`), by dispatching to a real KMS-compatible backend service reachable via environment-provided endpoint/credentials (e.g. a LocalStack-style KMS emulator already running). The program is a thin, faithful proxy: it must translate CLI flags into service API calls, forward responses as JSON to stdout, and surface service/usage errors on stderr with an appropriate exit code — without reimplementing cryptography, without validating business rules client-side, and without shelling out to the real `awscli`.

## Behavioral contract

- Invocation form: `aws kms <subcommand> [--flag value ...]`. Any other service name or unknown subcommand is a usage error.
- Only the flags listed per-subcommand in the instruction are accepted; unlisted/unknown flags are a client usage error (exit 252), not silently ignored.
- Required flags per operation (e.g. `--key-id` for `describe-key`/`disable-key`/`generate-data-key`/`schedule-key-deletion`, `--alias-name`+`--target-key-id` for `create-alias`, `--key-id`+`--plaintext` for `encrypt`, `--ciphertext-blob` for `decrypt`) must be enforced; missing ones are a usage error, not passed through blank.
- All other input validation (value legality, e.g. bad `--key-usage`, out-of-range `--pending-window-in-days`, malformed key ids) is NOT done client-side — it must be delegated to the backing service, which returns a modeled validation exception that the program forwards as a service error (exit 254 or 1, not 252).
- Success: JSON response body written to stdout only, nothing on stderr, exit 0.
- Failure: stdout empty, one error line on stderr naming the failure class (service error envelope, bare `<ErrorCode>: message`, or a `usage:`/`Parameter validation failed:`/`Unknown options:` style line for client-detected problems), exit code in `{1,252,254,255}`, no raw traceback ever.
- State is server-side and persists across process invocations (each CLI invocation is a fresh subprocess hitting the same backend), so:
  - keys created via `create-key` show up in `list-keys`/`describe-key`.
  - aliases created via `create-alias` show up in `list-aliases` and resolve to their target key.
  - `disable-key` / `schedule-key-deletion` change key state observable via `describe-key`, and block subsequent crypto operations on that key with the correct error class.
  - `encrypt`→`decrypt` and `generate-data-key` ciphertext→`decrypt` round-trip to original plaintext; this round-trip is provided by the backend service, not reimplemented locally.
- Binary/blob input (`--plaintext`, `--ciphertext-blob`) must accept plain base64 strings as well as `fileb://`/`file://` file references, consistent with aws-cli v2 `cli_binary_format=base64` conventions, and must be forwarded to the service in the encoding it expects.
- Timestamp fields in service responses, if the backend returns them as epoch numbers, should be rendered in a stable JSON-parseable form (ISO8601 is one valid choice) — the actual requirement is just that `json.loads` succeeds and semantic values are correct; exact timestamp formatting is not strictly graded beyond parseability.
- Must not set/override `AWS_ENDPOINT_URL`, region, or credentials env vars — read what's already in the environment (with a documented sensible default endpoint only as fallback, not an override).

## Solution decomposition

1. **Argument parsing / dispatch**: read `argv`, expect `kms <subcommand>`, route to a per-command handler; reject unknown service/subcommand/flags with usage errors.
2. **Flag → API parameter mapping**: for each subcommand, map only its allowed CLI flags to the corresponding KMS API request field names (e.g. `--key-id`→`KeyId`, `--customer-master-key-spec`/`--key-spec`→`KeySpec`, `--pending-window-in-days`→int `PendingWindowInDays`), preserving optionality (only include a param if the flag was given, except required ones).
3. **Blob handling**: implement `file://`/`fileb://`/bare-value resolution to base64 for blob-typed flags (`--plaintext`, `--ciphertext-blob`).
4. **Transport to backend**: issue an HTTP request to the KMS-compatible endpoint (JSON-1.1 protocol, `X-Amz-Target: TrentService.<Operation>` header) using endpoint/credentials from the environment; do not hardcode/override region or endpoint beyond a fallback default.
5. **Response handling**: on success, print the JSON body (optionally normalizing timestamps) to stdout, exit 0. On HTTP error, parse the JSON error envelope (`__type`/`message` or similar) and print an error line to stderr identifying the error code/class, exit 254 (or 1/255, any non-zero in the allowed set).
6. **Client-side usage errors**: for missing required flags, unknown flags, or malformed integer args, print a `usage:`/`Missing required parameter:`/`Unknown options:`-style line to stderr, exit 252, without ever calling the backend.
7. **No local crypto/state**: all cryptographic operations, key state, alias resolution, and cross-command consistency are the backend's responsibility; the CLI is a stateless proxy per invocation.

## Solution space

Multiple valid architectures satisfy the contract:

- **Direct HTTP/JSON-1.1 protocol client** (as in the reference) — hand-rolled request/response against the KMS emulator's HTTP API, no SDK dependency.
- **boto3-based implementation** — if boto3 (or the AWS SDK for another language) is preinstalled in the image, using it to call `kms` operations is equally valid, as long as it reads endpoint/region/credentials from the environment rather than hardcoding them, and error/response shaping still meets the output contract. (Not importing `awscli` is required, but boto3 is a different library and is allowed.)
- **Any language** (Go, Node, Rust, shell+curl, etc.) is acceptable as long as the resulting entry point is an executable `aws` on `$PATH` and only uses packages already present in the image.
- Flag-to-parameter mapping tables can be structured many ways (dict-driven generic dispatcher vs. one function per subcommand) — both are fine as long as only the declared flags per subcommand are accepted.
- Timestamp normalization is optional cosmetic behavior; leaving epoch numbers as-is is also acceptable since grading is on JSON semantic content, not formatting, provided the value is still parseable/comparable as intended.
- Error message wording is free-form as long as it fits one of the three documented shapes (service envelope / bare code:message / client usage-prefix).
- Extra commands beyond the ten listed (e.g. `enable-key`, `cancel-key-deletion`, `sign`, `verify`, etc., referenced only in "cross-command behavior") may optionally be implemented for a richer round-trip story, but are not required deliverables — the graded command set is exactly the ten listed under "Commands". (The reference includes `enable-key` as a bonus/internal helper; this is not mandatory.)

## Known pitfalls

- **Client-side over-validation**: rejecting values like an unrecognized `--key-usage` or out-of-range `--pending-window-in-days` locally instead of letting the service produce the modeled validation error — violates "do not validate input client-side."
- **Fabricating flags**: adding flags not in the instruction's allow-list per command (e.g. accepting `--tags` on commands that don't list it) or silently accepting unknown flags instead of erroring.
- **Mixing stdout/stderr**: printing partial JSON before an error, or writing diagnostic/debug output to stdout.
- **Leaking tracebacks**: letting an unhandled exception (network error, JSON decode error, KeyError on missing field) print a Python/Go stack trace instead of a clean one-line error.
- **Hardcoding/overriding environment**: setting `AWS_ENDPOINT_URL`, `AWS_DEFAULT_REGION`, or credential env vars in code instead of reading what's already configured — breaks portability to the test harness's actual backend.
- **Blob mishandling**: not supporting `fileb://`/`file://` prefixes, or double-base64-encoding/decoding values, breaking round-trip encrypt/decrypt tests.
- **Required-flag omission**: forwarding a request without a required field to the service and treating the resulting error as fine — acceptable behaviorally (still an error) but exit code should reflect a service error appropriately, not crash; better to catch missing required flags early with clean usage errors matching exit 252.
- **Blocking cross-command state**: implementing any command with local/in-memory fake state instead of delegating to the real backend — breaks consistency since each invocation is a separate process invocation (no shared memory), so state MUST live in the backend, not in the CLI process.
- **Wrong exit code family**: using exit codes outside `{0,1,252,254,255}`.
- **Response reshaping errors**: mutating/renaming JSON fields returned by the service so that expected keys (e.g. `KeyId`, `CiphertextBlob`, `Plaintext`) are missing or renamed, breaking `json.loads`-based assertions on semantic content.

## Cheat surface

- Returning canned/static JSON without actually calling a backend (works only if tests don't verify cross-command state persistence or actual crypto round-trips — but the spec explicitly requires round-trip and cross-command consistency, so this would fail).
- Implementing crypto locally (e.g. real AES encrypt/decrypt in the CLI itself) instead of delegating to the service — could pass round-trip tests but would fail cross-process/cross-command state consistency (e.g. `describe-key` after `disable-key` from a separate process invocation) unless a shared persistent store is also implemented, which is unnecessarily risky and diverges from "state must remain consistent" as delegated to a real service.
- Swallowing all errors into exit 1 uniformly and printing an unhelpful string — technically satisfies "exit code in the set" but risks failing tests that check for specific error-class name patterns in stderr.
- Accepting arbitrary extra flags silently (ignoring instead of rejecting) to dodge usage-error tests — violates "unknown flags are a usage error" expectation implied by the flag allow-lists.
- Shelling out to real `aws`/`awscli` — explicitly forbidden.

## Success criteria

- For each of the ten subcommands, all documented flag combinations produce valid JSON on stdout with exit 0 when given well-formed input against a working backend.
- Unknown/missing/malformed flags produce stderr-only usage errors with exit 252 before ever contacting the backend.
- Service-rejected requests (bad key ids, disabled keys, invalid values) produce stderr-only error lines naming the error class, with exit code in `{1,254,255}`, and empty stdout.
- No stdout/stderr mixing on either path; no raw tracebacks under any input, including garbage/edge-case args.
- Cross-command state is correctly observable: keys from `create-key` appear in `list-keys`/`describe-key`; aliases from `create-alias` appear in `list-aliases`; `disable-key`/`schedule-key-deletion` state changes are visible in `describe-key` and block `encrypt`/`decrypt`/`generate-data-key` with the correct error class.
- `encrypt`→`decrypt` round-trips to identical plaintext; `generate-data-key`'s returned ciphertext decrypts to its returned plaintext.
- Blob flags accept bare base64, `file://`, and `fileb://` forms correctly.
- The executable is discoverable as `aws` on `$PATH` (with `/workspace/submission/` acceptable) and requires no network access beyond the configured KMS endpoint, and fetches no additional packages at runtime.