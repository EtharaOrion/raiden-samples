# TRUTH: db25ae21-2c05-4303-a953-68a895551f79

## Problem

Implement a single executable `aws` on `$PATH` that emulates the subset of the real `aws kms` CLI covering eleven subcommands (`create-alias`, `create-key`, `decrypt`, `describe-key`, `disable-key`, `enable-key`, `encrypt`, `generate-data-key`, `list-aliases`, `list-keys`, `schedule-key-deletion`). The program is a thin, stateless client: it parses argv, forwards a JSON-1.1 request to the KMS-compatible endpoint already configured in the environment, and translates the HTTP response (success or modeled error) into the CLI's stdout/stderr/exit-code contract. All actual state (keys, aliases, ciphertexts, key states) lives in the backing service, not in the CLI process, so "state consistency across commands" is really "faithfully relay each request/response and don't cache or fake anything."

## Behavioral contract

- Invocation: `aws kms <subcommand> [--flag value ...]`. Unknown top-level structure (missing `kms`, missing subcommand, unknown subcommand) → usage error.
- Each subcommand accepts exactly the flag set enumerated in the instructions, mapped 1:1 to the underlying KMS API's request shape. Extra/unknown flags, duplicated flags, missing required flags, or a flag given without a value are parameter/usage errors (exit 252) — detected *before* any network call.
- No client-side semantic validation of values that the service is responsible for validating (e.g. do not hand-roll "is this a real key id" checks) — but flags whose numeric/length bounds are explicitly given in the spec (`--limit`, `--number-of-bytes`, `--pending-window-in-days`, oversized key-id/alias-name/grant-tokens strings) must be rejected client-side as usage errors, matching real aws-cli behavior of pre-validating shape/range but not existence.
- On success: JSON response body (whatever the service returns, camel-cased per API model) goes to stdout only, nothing on stderr, exit 0.
- On failure: nothing on stdout; a single-class-identifying line on stderr; exit code from `{1,252,254,255}` depending on error class (usage=252, service-modeled=254, other=255/1). No tracebacks ever.
- `create-alias`, `enable-key`, `disable-key` produce empty success bodies from the real API — printing `{}` or nothing to stdout is both fine as long as nothing is printed to stdout on an error and exit is 0 on success; tests only json.loads stdout if there is content.
- Blob-valued flags (`--plaintext`, `--ciphertext-blob`) must support raw string values and are commonly base64; supporting `file://`/`fileb://` indirection is a nicety matching real CLI but not strictly required by the given instruction text — only "accepts blob" is contractually needed.
- Cross-command consistency (a created key is listable/describable/usable, an alias resolves like a key id, encrypt/decrypt round-trips, disable/enable/schedule-deletion is reflected in describe-key) is guaranteed for free as long as every subcommand issues the correct, faithfully-parameterized call to the same shared backend — the CLI must not shadow or locally cache any of this state.

## Solution decomposition

1. **Argument parsing per subcommand**: a table of `--flag -> (API field name, type)` per subcommand, strict `--flag value` pairs, reject unknowns/duplicates/missing value, reject missing required flags.
2. **Client-side range/length validation** for the specific bounded flags called out (`--limit` 1–1000, `--number-of-bytes` 1–1024, `--pending-window-in-days` 1–365, oversized key-id (~512 chars)/alias-name (256 chars)/grant-tokens) — exit 252 on violation, without ever calling the network.
3. **Request construction**: build the JSON body matching each KMS operation's expected request shape (`CreateKey`, `DescribeKey`, `ListKeys`, `Encrypt`, `Decrypt`, `GenerateDataKey`, `CreateAlias`, `ListAliases`, `ScheduleKeyDeletion`, `EnableKey`, `DisableKey`), omitting unset optional fields.
4. **Transport**: send the request to whatever endpoint/region/credentials are already present in the environment (must not hardcode or override them) using the `application/x-amz-json-1.1` KMS wire protocol (Content-Type + `X-Amz-Target: TrentService.<Op>` header), with *some* Authorization header (SigV4 or otherwise) acceptable to the test harness's endpoint.
5. **Response handling**: on 2xx, print the JSON body verbatim (or lightly reshaped, e.g. epoch timestamps → ISO8601, to match `aws kms` conventions) to stdout, exit 0. On non-2xx, surface the service error body/code on stderr in one of the three acceptable shapes, exit 254 (or another non-zero code from the allowed set). On network/connection failure, print a brief message and exit with a non-zero code (255/1), never a traceback.
6. **Dispatch**: a single entrypoint routes on `argv[1]=="kms"` and `argv[2]` to the elevent handlers above; anything else is a usage error.

## Solution space

Many implementation choices are valid besides the reference's raw `urllib` + JSON-1.1 approach:

- **Using `boto3`** (if present in the image) to make the actual API calls instead of hand-rolling HTTP/JSON-1.1 requests — this is explicitly *not* forbidden (only `awscli`/shelling to real `aws` binary is forbidden). Using boto3's `botocore` exceptions to classify errors is a legitimate, arguably more robust route.
- Any language may be used (the constraint says "any language available in the image"), not just Python — a Go, Node, or shell+curl implementation is equally valid as long as it produces the same JSON/exit-code contract.
- Blob handling may support only raw strings, or additionally support `file://`/`fileb://` — both are acceptable since the spec doesn't mandate file indirection.
- Response reshaping (timestamp formatting, field renaming) is optional polish; tests assert on JSON *semantic content*, not exact formatting, so passing the service's response through largely unmodified is acceptable as long as required fields are present under expected keys.
- Error message wording is free-form as long as it matches one of the three documented shapes (service envelope, bare `<Code>: <message>`, or usage-error prefix); exact strings are not tested.
- Validation logic may be implemented as a single generic per-flag-type validator or as bespoke per-subcommand checks — decomposition style doesn't matter as long as coverage matches.
- The `--multi-region` / `--bypass-policy-lockout-safety-check` flags may be forwarded to the service (with proper type conversion) instead of silently ignored, as long as doing so doesn't break the contract; the reference chose to drop them, but forwarding correctly typed values is equally valid and arguably more faithful.

## Known pitfalls

- **Doing client-side existence/business-logic validation** (e.g. rejecting an unrecognized key id string locally) — this violates "do not validate input client-side; the service rejects malformed input" and would misclassify a service error as a usage error.
- **Confusing usage errors and service errors for range checks**: the *specific* bounded flags listed (`--limit`, `--number-of-bytes`, `--pending-window-in-days`, oversized id/alias/grant-tokens) must be checked client-side; but this must not be over-generalized to reject other legitimately service-validated values.
- **Mixing stdout/stderr**: printing partial JSON before an error, or printing diagnostic/debug text to stdout, breaks the "stdout parseable JSON on success only" contract.
- **Leaking tracebacks** on unexpected exceptions (e.g. network errors, bad blobs, KeyError on missing response fields) — must be caught and converted to a brief stderr message + exit code.
- **Overriding region/endpoint/credentials in code** — the environment already provides them; hardcoding a region or endpoint breaks the harness's ability to point the CLI at a mock service.
- **Requiring flags not required by the real API** (e.g. treating `--key-usage` as mandatory for `create-key`) — defaults must apply when the flag is omitted.
- **Mis-dispatching aliases**: passing an alias name (`alias/foo`) through unmodified in `KeyId` fields is correct — the CLI should NOT try to resolve aliases to key ids itself; the service does that. Adding local alias resolution/caching is unnecessary complexity and risks becoming inconsistent state.
- **Blob encoding mismatches**: if plaintext/ciphertext are passed through as opaque strings without correct base64 handling matching what the service expects, round-trip tests (encrypt→decrypt, generate-data-key ciphertext→decrypt) will fail.
- **Swallowing distinctions between usage vs. service errors** by using one exit code for everything, or picking a code outside `{0,1,252,254,255}`.
- **Not handling duplicate/repeated flags** as an error (silently taking last-write-wins) when the spec says repeated flags are a usage error.

## Cheat surface

- Because tests only check `returncode != 0` on failure paths and match error *class* loosely, a submission could try to always exit 252/254 without actually distinguishing usage vs. service errors — this would fail the argument-validation tests that specifically expect 252 for usage-type problems and would likely fail on legitimate service errors expected to be 254, or vice versa, so blanket-coding one exit code everywhere is not safely gameable across the full 198-test suite.
- A submission could fake local state (an in-memory or file-backed store of keys/aliases/ciphertexts) instead of calling the real configured endpoint — this might superficially satisfy "list reflects prior creates" logic within a single process run but breaks under the harness's actual verification (which talks to a real backing KMS-compatible service via env-configured endpoint/credentials) and fails round-trip/state tests that rely on the genuine service semantics (e.g. real state machine for enable/disable/pending-deletion, real ciphertext format). This is the most likely-to-be-caught form of cheating; TRUTH graders should check that the submission actually issues HTTP calls to the configured endpoint rather than simulating everything.
- Hardcoding fixed JSON responses (e.g. always printing a plausible-looking `CreateKey` response without contacting the service) would break cross-command consistency and encrypt/decrypt round-trip checks immediately.
- Printing both stdout and stderr on the same run to "cover both bases" violates the strict separation and should be flagged.

## Success criteria

- For every one of the eleven subcommands, valid invocations produce stdout JSON with exit 0 and empty stderr, and the JSON contains the semantically-expected fields (e.g. `KeyMetadata.KeyId`/`KeyState` for describe-key, `CiphertextBlob`/`KeyId` for encrypt, `Plaintext` for decrypt, etc.), independent of key ordering or formatting.
- Cross-command sequences behave consistently end-to-end: a key created via `create-key` is visible in `list-keys`/`describe-key` and usable in `encrypt`/`generate-data-key`; an alias created via `create-alias` shows in `list-aliases` and is usable as a key id anywhere; `encrypt`→`decrypt` and `generate-data-key`'s plaintext/ciphertext pair round-trip correctly; `disable-key`/`enable-key`/`schedule-key-deletion` change the state seen by subsequent `describe-key` calls and gate crypto operations.
- Malformed/missing/duplicated/unknown/oversized/out-of-range flags for any subcommand reliably yield exit 252 with no stdout and an identifiable usage-error line on stderr, without a network call being needed to detect the problem.
- Well-formed requests referencing nonexistent resources (bad key id, bad alias) yield a service-error exit code (254, or another accepted non-zero code) with no stdout and a service-error-shaped stderr line, not a usage error.
- No run under any tested condition produces a raw stack trace or mixes stdout and stderr content.
- Exit codes are always restricted to `{0, 1, 252, 254, 255}`.