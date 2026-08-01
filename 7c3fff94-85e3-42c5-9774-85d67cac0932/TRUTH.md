# TRUTH: 7c3fff94-85e3-42c5-9774-85d67cac0932

## Problem

Implement a single executable `aws` on `$PATH` that dispatches `aws kms <subcommand> [flags...]` to a stateful, in-process-or-remote KMS-like service, covering 30 named subcommands. The program must behave like `aws-cli` talking to a real KMS backend: it parses documented flags, forwards a request, and prints a JSON response to stdout on success or a classifiable error line to stderr on failure, with an exit code from a fixed small set. State (keys, aliases, tags, rotation, policies, key material) must persist and be mutually consistent across separate invocations of the CLI within a test run, since each command is a separate subprocess.

## Behavioral contract

- Invocation: `aws kms <command> [--flag value ...]`. Unknown top-level command or malformed args → usage error (exit 252), never a stack trace.
- stdout carries *only* the JSON response body on success (parseable via `json.loads`); stderr is empty on success.
- stdout is empty on failure; stderr carries exactly one of: AWS envelope `An error occurred (<ErrorCode>) when calling the <Operation> operation: <message>`, bare `<ErrorCode>: <message>`, or a client usage-error line (`usage: ...`, `Parameter validation failed: ...`, `Unknown options: ...`).
- Exit code ∈ {0,1,252,254,255}; test harness only checks zero/nonzero except where it inspects code semantics implicitly through error class matching.
- No fabricated flags beyond what's listed per-command; no client-side semantic validation of input values beyond what's needed to route/serialize (the *service* — real or emulated — is the source of truth for validation errors), though basic usage errors (missing required flag, unknown flag, wrong arg count) are legitimately client-side.
- Cross-command state consistency is mandatory: created keys/aliases/tags/rotation-state/policy/key-state changes made by one invocation must be observable by subsequent invocations (i.e., persisted across process boundaries, not just in-memory of one run).
- Cryptographic round-trips must be real: encrypt→decrypt, generate-data-key ciphertext→decrypt, re-encrypt→decrypt, sign→verify, generate-mac→verify-mac must all actually work with matching plaintext/signature/MAC — not stubbed/random values that happen to satisfy schema.
- Key lifecycle semantics: disabled or pending-deletion keys must reject crypto operations distinguishably (as a modeled service error, i.e. class `DisabledException`/`KMSInvalidStateException`-ish, exit 254 typically); cancel-key-deletion returns key to disabled (not enabled); enable-key required afterward.

## Solution decomposition

1. **Executable entrypoint**: `/workspace/submission/aws` (or elsewhere on PATH) that recognizes `kms` as the service token and dispatches on `argv[2]`.
2. **Backend connectivity**: Read AWS endpoint/credentials/region from environment (must NOT hardcode/override), and communicate with whatever KMS-compatible service the environment provides (e.g., a local emulator such as LocalStack/moto-server listening per env vars) using the JSON protocol (`X-Amz-Target: TrentService.<Op>`) or an SDK/boto3 client configured from env. This is the mechanism the reference uses; equally valid is using `boto3` directly with a client constructed with no explicit endpoint/region/credential overrides (letting env vars flow through), since boto3 is presumably available in the image.
3. **Per-subcommand flag parsing**: map each CLI flag to its API JSON field name and type (string, int, blob/base64, JSON list/tags), supporting `file://`/`fileb://` blob/string loading conventions used by aws-cli.
4. **Required-flag / arg-count validation**: enforce the "Flags:" list per command; missing required args, unrecognized flags, or missing values → usage error class, exit 252.
5. **Request dispatch and response passthrough**: forward the assembled parameters to the corresponding KMS API operation (e.g. CreateKey, DescribeKey, Encrypt, Decrypt, GenerateDataKey, Sign, Verify, GenerateMac, VerifyMac, TagResource, etc.), and relay the JSON response (possibly reformatting timestamp fields to ISO8601 strings to match aws-cli conventions — though tests only check semantic JSON content, not formatting, so this is optional polish, not required).
6. **Error translation**: on backend HTTP error, emit an error line matching one of the three acceptable shapes and map to exit 254 (modeled service error) or other codes as appropriate; on network/unexpected exception, catch and print a brief message (never a traceback), exit 255 or 1.
7. **Pagination handling for list-keys / list-aliases / list-resource-tags** (optional convenience — auto-paginate when no `--limit`/`--marker` given, as aws-cli does) — not strictly required by the contract, since tests are about content not truncation behavior explicitly, but must not break when `--limit`/`--marker` are given.
8. **Statefulness**: whatever backend is used must retain keys/aliases/tags/policies/rotation state/key material across separate process invocations — this effectively requires a persistent backend (server process, or file/db-backed local store) rather than in-memory state reset each run, since each `aws kms ...` call is a fresh subprocess.

## Solution space

Valid alternative approaches (any of these, not just the reference's shape):

- **Thin client over a provided emulator**: If the test environment supplies a running local KMS-compatible HTTP service (e.g., LocalStack) with endpoint/creds already in env vars, the submission can be a thin protocol client (raw HTTP via `urllib`, or via `boto3.client("kms")` with default env-derived config) — this is what the reference does. Using `boto3` instead of hand-rolled SigV4-lite headers is equally valid and likely simpler/more robust.
- **Self-contained local implementation**: If no backend service is available/expected, a fully self-contained CLI that implements KMS semantics itself (key generation via `cryptography`/`hashlib`/`hmac`/stdlib crypto, persisting state to a JSON/sqlite file under a fixed path) is equally valid, as long as: state persists across process invocations, crypto round-trips are real, and error/response shapes match the contract. This is likely necessary if the task environment does not provide a live KMS-compatible endpoint — the instruction's emphasis on "AWS credentials and endpoint are set in the environment" suggests a backend is provided, but a hybrid/fallback implementation is also acceptable.
- **Language choice**: any language available in the image (Python, Go, Node, etc.) is acceptable, provided the resulting executable `aws` handles the `kms` service correctly; the reference happens to be Python.
- **JSON pretty-printing / timestamp formatting**: optional; tests parse JSON semantically, so raw `json.dumps` without ISO8601 conversion of timestamp fields is equally acceptable as long as fields are self-consistent (e.g. if `CreationDate` is a number instead of string, that's fine since no format is contractually mandated — only that it's valid JSON and semantically correct where compared).
- **Auto-pagination**: implementing or not implementing multi-page merging for `list-keys`/`list-aliases` is a matter of choice; a single-page response is acceptable as long as it doesn't break when explicit `--limit`/`--marker` are passed, since the contract doesn't mandate exhaustive pagination.

## Known pitfalls

- **Mixing stdout/stderr**: printing a partial JSON to stdout before hitting an error, or printing diagnostic/debug info to stdout, breaks the "stdout is JSON-only on success / empty on failure" contract.
- **Leaking tracebacks**: any unhandled Python/Go/Node exception producing a stack trace on stderr fails the "no raw traceback" requirement even if exit code is nonzero.
- **Client-side over-validation**: rejecting values that only the service is supposed to validate (e.g. validating KeyUsage/KeySpec enums locally) risks diverging from real service semantics; the instruction explicitly says not to validate input client-side beyond basic usage-error class (missing/unknown/malformed CLI args are fine to check).
- **State not persisting across process boundaries**: since every command is a fresh subprocess invocation, an implementation holding state only in memory (e.g., a Python dict reset each run) will fail every cross-command test; state must be durable (backend server or on-disk store).
- **Fake/non-functional crypto**: returning random bytes for ciphertext/signature/MAC without an actual invertible relationship to plaintext/key breaks all round-trip tests (encrypt→decrypt, sign→verify, generate-mac→verify-mac, generate-data-key ciphertext→decrypt, re-encrypt→decrypt).
- **Wrong state transition for cancel-key-deletion**: per spec it returns to **disabled**, not enabled — a common mistake is re-enabling directly.
- **Not blocking crypto ops on disabled/pending-deletion keys**: must surface a modeled error (not silently succeed).
- **Hardcoding/overriding endpoint, region, or credentials** in code instead of reading from environment — violates explicit constraint and likely breaks against the test harness's actual configured endpoint.
- **Fabricating flags** not in the documented per-command flag list, or silently accepting typoed/extra flags instead of raising a usage error.
- **Blob/file handling**: forgetting `file://`/`fileb://` prefix handling for blob-typed arguments (`--plaintext`, `--ciphertext-blob`, `--message`, `--signature`, `--mac`, `--policy` via file, tags via file) could break tests that pass literal values vs. file references — though only support what's plausible for the given flags.
- **Exit code selection**: using an exit code outside {0,1,252,254,255}, or conflating usage errors (252) with service errors (254) in a way that a test's error-class matching fails against the chosen error message shape.
- **Alias name handling**: forgetting to require/prefix `alias/` correctly, or not making `delete-alias`/`update-alias`/`create-alias` consistently visible in `list-aliases`.

## Cheat surface

- Returning syntactically valid but semantically empty/fake JSON (e.g., static canned responses with fixed fake key IDs/ARNs) would pass naive shape checks but fail cross-command consistency and round-trip tests (list-keys must show created key, decrypt must recover exact plaintext, verify must validate the exact signature produced by sign) — this is not a viable shortcut given the test suite described (268 tests) which explicitly checks end-to-end behavior, not just per-call schema.
- Hardcoding "always valid"/"always success" for `verify`/`verify-mac` regardless of actual signature/MAC correctness would be caught by negative tests presumably included (verifying wrong signature should fail) — must implement genuine crypto verification.
- Ignoring `--dry-run` semantics is likely acceptable if the harness doesn't test them deeply, but claiming success while performing the real mutating operation when `--dry-run` is set would be incorrect if tested (moderate risk area, not central to the contract as stated).
- Skipping real HSM-grade crypto (using simple reversible encoding, e.g., XOR/base64, in place of real AES/RSA) is acceptable *functionally* as long as round-trip correctness holds and no test inspects the ciphertext's cryptographic properties directly — the contract only requires round-trip semantic correctness, not cryptographic strength, per the observable-behavior framing.

## Success criteria

- All 268 shipped tests pass: JSON responses parse and contain expected semantic fields (key ids, ARNs, states, plaintext/ciphertext, signatures, MACs, tags, aliases, policy documents, rotation flags) matching the cross-command state machine described.
- Round-trip operations (encrypt/decrypt, sign/verify, generate-mac/verify-mac, generate-data-key/decrypt, re-encrypt/decrypt) are cryptographically and semantically correct, not merely schema-valid.
- Key lifecycle state transitions (`disable-key`, `enable-key`, `schedule-key-deletion`, `cancel-key-deletion`) are correctly reflected in `describe-key` and correctly gate cryptographic operations with a modeled error.
- Alias/tag/rotation/policy mutations are correctly reflected in their corresponding read commands.
- All success output goes only to stdout as valid JSON; all failure output goes only to stderr as one of the three acceptable error-class shapes; exit codes are drawn from the permitted set and are nonzero exactly on failure.
- No raw tracebacks ever appear; no unauthorized flags accepted; no hardcoded endpoint/region/credential overrides in code.