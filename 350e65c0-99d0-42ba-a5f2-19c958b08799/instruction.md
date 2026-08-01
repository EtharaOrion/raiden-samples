# Build an `aws kms` CLI

## Application overview

You will implement the following `aws kms` commands:
`kms cancel-key-deletion`, `kms create-alias`, `kms create-key`, `kms decrypt`, `kms delete-alias`, `kms describe-key`, `kms disable-key`, `kms enable-key`, `kms encrypt`, `kms list-aliases`, `kms list-keys`, `kms schedule-key-deletion`.

Your code is invoked as a subprocess:

```bash
aws kms <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence of
kms operations behaves correctly end-to-end.

## Commands

### `kms cancel-key-deletion`

Argv shapes observed:

- `kms cancel-key-deletion --key-id x`
- `kms cancel-key-deletion --key-id <string>`

Flags: `--key-id`

Behavior:

- Moves a pending-deletion key back to disabled (visible via `describe-key`); re-enable it with `enable-key` before using it.
- Service-level failures must exit non-zero and name the error class on
  stderr; classes exercised for this command include: `NotFoundException`.

### `kms create-alias`

Argv shapes observed:

- `kms create-alias --alias-name x --target-key-id <value>`
- `kms create-alias --alias-name <string> --target-key-id <string>`
- `kms create-alias --alias-name <value> --target-key-id x`

Flags: `--alias-name`, `--target-key-id`

Behavior:

- Binds an `alias/<name>` to a key; the alias appears in `list-aliases` and resolves to the key for other operations.
- Creating a duplicate alias fails with an already-exists error class; a missing target key fails with a not-found error class.
- Service-level failures must exit non-zero and name the error class on
  stderr; classes exercised for this command include: `NotFoundException`.

### `kms create-key`

Argv shapes observed:

- `kms create-key --key-usage SIGN_VERIFY`
- `kms create-key`
- `kms create-key --key-usage ENCRYPT_DECRYPT`
- `kms create-key --key-usage GENERATE_VERIFY_MAC`

Flags: `--bypass-policy-lockout-safety-check`, `--custom-key-store-id`, `--customer-master-key-spec`, `--description`, `--key-spec`, `--key-usage`, `--multi-region`, `--origin`, `--policy`, `--tags`, `--xks-key-id`

Behavior:

- Creates a key and returns its metadata; the new key id appears in `list-keys` and is usable by the cryptographic operations.
- Keys default to symmetric encrypt/decrypt usage; signing keys are created with SIGN_VERIFY usage and an asymmetric key spec, MAC keys with GENERATE_VERIFY_MAC usage and an HMAC key spec.

### `kms decrypt`

Argv shapes observed:

- `kms decrypt --ciphertext-blob <value> --encryption-algorithm SYMMETRIC_DEFAULT`
- `kms decrypt --ciphertext-blob <blob>`
- `kms decrypt --ciphertext-blob <value> --encryption-algorithm RSAES_OAEP_SHA_1`
- `kms decrypt --ciphertext-blob <value> --encryption-algorithm RSAES_OAEP_SHA_256`

Flags: `--ciphertext-blob`, `--dry-run`, `--encryption-algorithm`, `--encryption-context`, `--grant-tokens`, `--key-id`, `--recipient`

Behavior:

- Decrypts a ciphertext produced by this service and returns the original plaintext (base64) plus the key id that protected it.
- Service-level failures must exit non-zero and name the error class on
  stderr; classes exercised for this command include: `NotFoundException`.

### `kms delete-alias`

Argv shapes observed:

- `kms delete-alias --alias-name x`
- `kms delete-alias --alias-name <string>`

Flags: `--alias-name`

Behavior:

- After success the alias no longer appears in `list-aliases`; the underlying key is unaffected.
- Service-level failures must exit non-zero and name the error class on
  stderr; classes exercised for this command include: `NotFoundException`.

### `kms describe-key`

Argv shapes observed:

- `kms describe-key --key-id x`
- `kms describe-key --key-id <string>`
- `kms describe-key --key-id <value> --grant-tokens xxxxxxxxxx`

Flags: `--grant-tokens`, `--key-id`

Behavior:

- Reports the key's metadata (id, ARN, state, usage, description); state changes made by other commands are visible here.
- Describing a missing key fails with a not-found error class.
- Service-level failures must exit non-zero and name the error class on
  stderr; classes exercised for this command include: `NotFoundException`.

### `kms disable-key`

Argv shapes observed:

- `kms disable-key --key-id x`
- `kms disable-key --key-id <string>`

Flags: `--key-id`

Behavior:

- After success the key state is disabled and cryptographic use of the key fails with a disabled-key error class.
- Service-level failures must exit non-zero and name the error class on
  stderr; classes exercised for this command include: `NotFoundException`.

### `kms enable-key`

Argv shapes observed:

- `kms enable-key --key-id x`
- `kms enable-key --key-id <string>`

Flags: `--key-id`

Behavior:

- Restores a disabled key to the enabled state so cryptographic operations succeed again.
- Service-level failures must exit non-zero and name the error class on
  stderr; classes exercised for this command include: `NotFoundException`.

### `kms encrypt`

Argv shapes observed:

- `kms encrypt --key-id <value> --plaintext <value> --encryption-algorithm SYMMETRIC_DEFAULT`
- `kms encrypt --key-id <string> --plaintext <blob>`
- `kms encrypt --key-id <value> --plaintext <value> --encryption-algorithm RSAES_OAEP_SHA_1`
- `kms encrypt --key-id <value> --plaintext <value> --encryption-algorithm RSAES_OAEP_SHA_256`

Flags: `--dry-run`, `--encryption-algorithm`, `--encryption-context`, `--grant-tokens`, `--key-id`, `--plaintext`

Behavior:

- Encrypts plaintext under an enabled key and returns a ciphertext blob (base64) plus the key id used.
- Ciphertext decrypts back to the original plaintext (round-trip identity).
- Encrypting under a missing key fails with a not-found error class; under a disabled key, with a disabled-key error class.
- Service-level failures must exit non-zero and name the error class on
  stderr; classes exercised for this command include: `NotFoundException`.

### `kms list-aliases`

Argv shapes observed:

- `kms list-aliases --key-id x`
- `kms list-aliases`
- `kms list-aliases --limit 1`
- `kms list-aliases --limit 1000`

Flags: `--key-id`, `--limit`, `--marker`

Behavior:

- Reflects the cumulative effect of alias creates, updates, and deletes.

### `kms list-keys`

Argv shapes observed:

- `kms list-keys --limit 1`
- `kms list-keys`
- `kms list-keys --limit 1000`
- `kms list-keys --marker x`

Flags: `--limit`, `--marker`

Behavior:

- Reflects every key created so far in this account.

### `kms schedule-key-deletion`

Argv shapes observed:

- `kms schedule-key-deletion --key-id x`
- `kms schedule-key-deletion --key-id <string>`
- `kms schedule-key-deletion --key-id <value> --pending-window-in-days 1`
- `kms schedule-key-deletion --key-id <value> --pending-window-in-days 365`

Flags: `--key-id`, `--pending-window-in-days`

Behavior:

- Moves the key into the pending-deletion state (visible via `describe-key`); a pending-deletion key rejects cryptographic use.
- Service-level failures must exit non-zero and name the error class on
  stderr; classes exercised for this command include: `NotFoundException`.

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

