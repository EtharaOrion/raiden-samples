# Build an `aws kms` CLI

## Application overview

You will implement the following `aws kms` commands:
`kms create-alias`, `kms create-key`, `kms decrypt`, `kms describe-key`, `kms disable-key`, `kms encrypt`, `kms generate-data-key`, `kms list-aliases`, `kms list-keys`, `kms schedule-key-deletion`.

Your code is invoked as a subprocess:

```bash
aws kms <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence of
kms operations behaves correctly end-to-end.

## Commands

### `kms create-alias`
- `kms create-alias --alias-name <string> --target-key-id <string>`
Flags: `--alias-name`, `--target-key-id`
Binds an `alias/<name>` to a key; the alias appears in `list-aliases` and resolves to the key for other operations.
Creating a duplicate alias fails with an already-exists error class; a missing target key fails with a not-found error class.

### `kms create-key`
- `kms create-key --key-usage SIGN_VERIFY`
- `kms create-key`
- `kms create-key --key-usage ENCRYPT_DECRYPT`
- `kms create-key --key-usage GENERATE_VERIFY_MAC`
- `kms create-key --key-usage KEY_AGREEMENT`
- `kms create-key --customer-master-key-spec RSA_2048`
Flags: `--bypass-policy-lockout-safety-check`, `--custom-key-store-id`, `--customer-master-key-spec`, `--description`, `--key-spec`, `--key-usage`, `--multi-region`, `--origin`, `--policy`, `--tags`, `--xks-key-id`
Creates a key and returns its metadata; the new key id appears in `list-keys` and is usable by the cryptographic operations.
Keys default to symmetric encrypt/decrypt usage; signing keys are created with SIGN_VERIFY usage and an asymmetric key spec, MAC keys with GENERATE_VERIFY_MAC usage and an HMAC key spec.

### `kms decrypt`
- `kms decrypt --ciphertext-blob <blob>`
- `kms decrypt --ciphertext-blob <value> --encryption-algorithm SYMMETRIC_DEFAULT`
- `kms decrypt --ciphertext-blob <value> --encryption-algorithm RSAES_OAEP_SHA_1`
- `kms decrypt --ciphertext-blob <value> --encryption-algorithm RSAES_OAEP_SHA_256`
- `kms decrypt --ciphertext-blob <value> --encryption-algorithm SM2PKE`
- `kms decrypt --ciphertext-blob <value> --encryption-context <value> --grant-tokens <value> --key-id <value> --encryption-algorithm <value> --recipient <value> --dry-run <value>`
Flags: `--ciphertext-blob`, `--dry-run`, `--encryption-algorithm`, `--encryption-context`, `--grant-tokens`, `--key-id`, `--recipient`
Decrypts a ciphertext produced by this service and returns the original plaintext (base64) plus the key id that protected it.

### `kms describe-key`
- `kms describe-key --key-id <string>`
- `kms describe-key --key-id <value> --grant-tokens <value>`
Flags: `--grant-tokens`, `--key-id`
Reports the key's metadata (id, ARN, state, usage, description); state changes made by other commands are visible here.
Describing a missing key fails with a not-found error class.

### `kms disable-key`
- `kms disable-key --key-id <string>`
Flags: `--key-id`
After success the key state is disabled and cryptographic use of the key fails with a disabled-key error class.

### `kms encrypt`
- `kms encrypt --key-id <string> --plaintext <blob>`
- `kms encrypt --key-id <value> --plaintext <value> --encryption-algorithm SYMMETRIC_DEFAULT`
- `kms encrypt --key-id <value> --plaintext <value> --encryption-algorithm RSAES_OAEP_SHA_1`
- `kms encrypt --key-id <value> --plaintext <value> --encryption-algorithm RSAES_OAEP_SHA_256`
- `kms encrypt --key-id <value> --plaintext <value> --encryption-algorithm SM2PKE`
- `kms encrypt --key-id <value> --plaintext <value> --encryption-context <value> --grant-tokens <value> --encryption-algorithm <value> --dry-run <value>`
Flags: `--dry-run`, `--encryption-algorithm`, `--encryption-context`, `--grant-tokens`, `--key-id`, `--plaintext`
Encrypts plaintext under an enabled key and returns a ciphertext blob (base64) plus the key id used.
Ciphertext decrypts back to the original plaintext (round-trip identity).

### `kms generate-data-key`
- `kms generate-data-key --key-id <string>`
- `kms generate-data-key --key-id <value> --key-spec AES_256`
- `kms generate-data-key --key-id <value> --key-spec AES_128`
- `kms generate-data-key --key-id <value> --number-of-bytes 1`
- `kms generate-data-key --key-id <value> --number-of-bytes 1024`
- `kms generate-data-key --key-id <value> --encryption-context <value> --number-of-bytes <value> --key-spec <value> --grant-tokens <value> --recipient <value> --dry-run <value>`
Flags: `--dry-run`, `--encryption-context`, `--grant-tokens`, `--key-id`, `--key-spec`, `--number-of-bytes`, `--recipient`
Returns a fresh data key as both plaintext and ciphertext; the ciphertext decrypts to exactly that plaintext.

### `kms list-aliases`
- `kms list-aliases`
- `kms list-aliases --limit 0`
- `kms list-aliases --limit 1`
- `kms list-aliases --limit 1001`
- `kms list-aliases --limit 1000`
- `kms list-aliases --key-id <value> --limit <value> --marker <value>`
Flags: `--key-id`, `--limit`, `--marker`
Reflects the cumulative effect of alias creates, updates, and deletes.

### `kms list-keys`
- `kms list-keys --limit 0`
- `kms list-keys --limit 1`
- `kms list-keys`
- `kms list-keys --limit 1001`
- `kms list-keys --limit 1000`
- `kms list-keys --limit <value> --marker <value>`
Flags: `--limit`, `--marker`
Reflects every key created so far in this account.

### `kms schedule-key-deletion`
- `kms schedule-key-deletion --key-id <string>`
- `kms schedule-key-deletion --key-id <value> --pending-window-in-days 1`
- `kms schedule-key-deletion --key-id <value> --pending-window-in-days 365`
- `kms schedule-key-deletion --key-id <value> --pending-window-in-days <value>`
- `kms schedule-key-deletion --key-id <value> --pending-window-in-days 0`
- `kms schedule-key-deletion --key-id <value> --pending-window-in-days 366`
Flags: `--key-id`, `--pending-window-in-days`
Moves the key into the pending-deletion state (visible via `describe-key`); a pending-deletion key rejects cryptographic use.

## Cross-command behavior

State must remain consistent across the command set:

- A key created by `create-key` is visible to `list-keys` and `describe-key` and usable by every cryptographic command.
- `encrypt` -> `decrypt` and `generate-data-key` ciphertext -> `decrypt` both return the original plaintext; `re-encrypt` preserves it across keys.
- `disable-key` blocks cryptographic use until `enable-key`; `schedule-key-deletion` blocks it until `cancel-key-deletion` + `enable-key`.
- `sign` output verifies via `verify`; `generate-mac` output verifies via `verify-mac` (same key, message, algorithm).
- Alias, tag, rotation, and policy changes are observable via their read commands (`list-aliases`, `list-resource-tags`, `get-key-rotation-status`, `get-key-policy`).

## Implementation constraints

- Your submission may be written in any language available in the image.
  Use only what the image already provides; no additional packages may be
  fetched.
- Do not import `awscli` or shell out to the real `aws` binary.
- AWS credentials and endpoint are set in the environment; do not override
  the service address, region, or credentials in code.
- Success output (JSON) goes to **stdout**; errors go to **stderr**. Do not
  mix them.
- Do not surface raw library tracebacks; print a brief user-facing error
  string instead.
- Do not fabricate flags that do not exist upstream. Do not validate input
  client-side; the service rejects malformed input with a validation error.
- Your submission must be an executable named `aws` on `$PATH`. It may be
  written in any language. The image provides `/workspace/submission/` first
  on `$PATH` as a convenient writable install location, but any directory on
  `$PATH` is acceptable. Helper files may live alongside it.

## Output contract

A correct implementation produces output in the *shape* described below,
names the *class* of any error reported, uses the documented exit-code
set, and never surfaces a runtime stack trace. Specific verbs and the
exact wording of any message are deliberately not enumerated here: derive
them from the underlying kms service semantics and standard
`aws kms` conventions.

### stdout (success path)

- A successful command writes the operation's JSON response document to
  stdout (parseable with `json.loads`).
- Assertions are on JSON semantic content, never on key order, whitespace,
  or any textual preamble.
- stderr is empty on success.

### stderr (failure path)

- stdout is empty on failure.
- A human-readable error line is written to stderr that identifies the
  failure *class*. Any of the following shapes is acceptable:
  - the underlying AWS service error envelope:
    `An error occurred (<ErrorCode>) when calling the <Operation> operation: <message>`
  - a bare `<ErrorCode>: <message>` line naming the service error code
  - a client-side usage-error line whose prefix names the failure class
    (for example, `usage: ...`, `Parameter validation failed: ...`,
    `Unknown options: ...`)
- Tests match the failure *class* against one of these shapes — not
  verbatim wording — so any spec-compliant phrasing is accepted.
- No runtime stack trace is emitted under any condition.

### Exit codes

The exit code on termination is one of `{0, 1, 252, 254, 255}`:

- `0` — success
- `1` — application error (an operation was attempted and failed)
- `252` — parameter/usage error (unknown flag, missing/extra argument,
  malformed value)
- `254` — service-modeled error (the service returned a modeled exception)
- `255` — other or general error

Tests only check `returncode != 0` on failure; any non-zero code in this set
is acceptable.
