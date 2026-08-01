# Build an `aws kms` CLI

## Application overview

You will implement the following `aws kms` commands:
`kms cancel-key-deletion`, `kms create-alias`, `kms create-key`, `kms decrypt`, `kms delete-alias`, `kms describe-key`, `kms disable-key`, `kms disable-key-rotation`, `kms enable-key`, `kms enable-key-rotation`, `kms encrypt`, `kms generate-data-key`, `kms generate-data-key-without-plaintext`, `kms generate-mac`, `kms generate-random`, `kms get-key-policy`, `kms get-key-rotation-status`, `kms get-public-key`, `kms list-aliases`, `kms list-keys`, `kms list-resource-tags`, `kms put-key-policy`, `kms re-encrypt`, `kms schedule-key-deletion`, `kms sign`, `kms tag-resource`, `kms untag-resource`, `kms update-alias`, `kms update-key-description`, `kms verify`, `kms verify-mac`.

Your code is invoked as a subprocess:

```bash
aws kms <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence of
kms operations behaves correctly end-to-end.

## Commands

### `kms cancel-key-deletion`
- `kms cancel-key-deletion --key-id <string>`
Flags: `--key-id`
Moves a pending-deletion key back to disabled (visible via `describe-key`); re-enable it with `enable-key` before using it.

### `kms create-alias`
- `kms create-alias --alias-name <string> --target-key-id <string>`
Flags: `--alias-name`, `--target-key-id`
Binds an `alias/<name>` to a key; the alias appears in `list-aliases` and resolves to the key for other operations.

### `kms create-key`
- `kms create-key --key-usage SIGN_VERIFY`
Flags: `--bypass-policy-lockout-safety-check`, `--custom-key-store-id`, `--customer-master-key-spec`, `--description`, `--key-spec`, `--key-usage`, `--multi-region`, `--origin`, `--policy`, `--tags`, `--xks-key-id`
Creates a key and returns its metadata; the new key id appears in `list-keys` and is usable by the cryptographic operations.

### `kms decrypt`
- `kms decrypt --encryption-algorithm SYMMETRIC_DEFAULT`
Flags: `--ciphertext-blob`, `--dry-run`, `--dry-run-modifiers`, `--encryption-algorithm`, `--encryption-context`, `--grant-tokens`, `--key-id`, `--recipient`
Decrypts a ciphertext produced by this service and returns the original plaintext (base64) plus the key id that protected it.

### `kms delete-alias`
- `kms delete-alias --alias-name <string>`
Flags: `--alias-name`
After success the alias no longer appears in `list-aliases`; the underlying key is unaffected.

### `kms describe-key`
- `kms describe-key --key-id <string>`
Flags: `--grant-tokens`, `--key-id`
Reports the key's metadata (id, ARN, state, usage, description); state changes made by other commands are visible here.

### `kms disable-key`
- `kms disable-key --key-id <string>`
Flags: `--key-id`
After success the key state is disabled and cryptographic use of the key fails with a disabled-key error class.

### `kms disable-key-rotation`
- `kms disable-key-rotation --key-id <string>`
Flags: `--key-id`
Turns rotation off; `get-key-rotation-status` then reports rotation disabled.

### `kms enable-key`
- `kms enable-key --key-id <string>`
Flags: `--key-id`
Restores a disabled key to the enabled state so cryptographic operations succeed again.

### `kms enable-key-rotation`
- `kms enable-key-rotation --key-id <string>`
Flags: `--key-id`, `--rotation-period-in-days`
Turns annual rotation on for the key; `get-key-rotation-status` then reports rotation enabled.

### `kms encrypt`
- `kms encrypt --key-id <string> --plaintext <blob>`
Flags: `--dry-run`, `--encryption-algorithm`, `--encryption-context`, `--grant-tokens`, `--key-id`, `--plaintext`
Encrypts plaintext under an enabled key and returns a ciphertext blob (base64) plus the key id used.

### `kms generate-data-key`
- `kms generate-data-key --key-id <string>`
Flags: `--dry-run`, `--encryption-context`, `--grant-tokens`, `--key-id`, `--key-spec`, `--number-of-bytes`, `--recipient`
Returns a fresh data key as both plaintext and ciphertext; the ciphertext decrypts to exactly that plaintext.

### `kms generate-data-key-without-plaintext`
- `kms generate-data-key-without-plaintext --key-id <string>`
Flags: `--dry-run`, `--encryption-context`, `--grant-tokens`, `--key-id`, `--key-spec`, `--number-of-bytes`
Returns only the encrypted form of a fresh data key (no plaintext field in the response).

### `kms generate-mac`
- `kms generate-mac --message <blob> --key-id <string> --mac-algorithm <string>`
Flags: `--dry-run`, `--grant-tokens`, `--key-id`, `--mac-algorithm`, `--message`
Computes a MAC over a message with an HMAC key; the MAC verifies successfully via `verify-mac` with the same inputs.

### `kms generate-random`
- `kms generate-random --number-of-bytes 0`
Flags: `--custom-key-store-id`, `--number-of-bytes`, `--recipient`
Returns the requested number of random bytes (base64); no key is involved.

### `kms get-key-policy`
- `kms get-key-policy --key-id <string>`
Flags: `--key-id`, `--policy-name`
Returns the key's policy document as a JSON string; the only policy name is `default`.

### `kms get-key-rotation-status`
- `kms get-key-rotation-status --key-id <string>`
Flags: `--key-id`
Reports whether rotation is enabled as a boolean that follows the enable/disable rotation commands.

### `kms get-public-key`
- `kms get-public-key --key-id <string>`
Flags: `--grant-tokens`, `--key-id`
Returns the public half of an asymmetric key (base64 DER) along with its spec, usage, and supported algorithms.

### `kms list-aliases`
- `kms list-aliases`
Flags: `--key-id`, `--limit`, `--marker`
Reflects the cumulative effect of alias creates, updates, and deletes.

### `kms list-keys`
- `kms list-keys --limit 0`
Flags: `--limit`, `--marker`
Reflects every key created so far in this account.

### `kms list-resource-tags`
- `kms list-resource-tags --key-id <string>`
Flags: `--key-id`, `--limit`, `--marker`
Reflects the key's current tags, order-independent.

### `kms put-key-policy`
- `kms put-key-policy --key-id <string> --policy <string>`
Flags: `--bypass-policy-lockout-safety-check`, `--key-id`, `--policy`, `--policy-name`
Replaces the key's `default` policy; the new document is returned by `get-key-policy`.

### `kms re-encrypt`
- `kms re-encrypt --destination-key-id <string>`
Flags: `--ciphertext-blob`, `--destination-encryption-algorithm`, `--destination-encryption-context`, `--destination-key-id`, `--dry-run`, `--dry-run-modifiers`, `--grant-tokens`, `--source-encryption-algorithm`, `--source-encryption-context`, `--source-key-id`
Re-wraps an existing ciphertext under a destination key; decrypting the new ciphertext yields the original plaintext.

### `kms schedule-key-deletion`
- `kms schedule-key-deletion --key-id <string>`
Flags: `--key-id`, `--pending-window-in-days`
Moves the key into the pending-deletion state (visible via `describe-key`); a pending-deletion key rejects cryptographic use.

### `kms sign`
- `kms sign --key-id <string> --message <blob> --signing-algorithm <string>`
Flags: `--dry-run`, `--grant-tokens`, `--key-id`, `--message`, `--message-type`, `--signing-algorithm`
Signs a message with an asymmetric SIGN_VERIFY key and returns a signature blob; the signature verifies successfully via `verify` with the same key, message, and algorithm.

### `kms tag-resource`
- `kms tag-resource --key-id <string> --tags <json>`
Flags: `--key-id`, `--tags`
Attaches tags (TagKey/TagValue pairs) to a key; they become visible via `list-resource-tags`.

### `kms untag-resource`
- `kms untag-resource --key-id <string> --tag-keys <json>`
Flags: `--key-id`, `--tag-keys`
Removes tags by key; removed tags disappear from `list-resource-tags`.

### `kms update-alias`
- `kms update-alias --alias-name <string> --target-key-id <string>`
Flags: `--alias-name`, `--target-key-id`
Repoints an existing alias at a different key; the new binding is visible via `list-aliases`.

### `kms update-key-description`
- `kms update-key-description --key-id <string> --description <string>`
Flags: `--description`, `--key-id`
After success the new description is visible via `describe-key`.

### `kms verify`
- `kms verify --key-id <string> --message <blob> --signature <blob> --signing-algorithm <string>`
Flags: `--dry-run`, `--grant-tokens`, `--key-id`, `--message`, `--message-type`, `--signature`, `--signing-algorithm`
Confirms a signature produced by `sign`: reports the signature as valid for the original message and algorithm.

### `kms verify-mac`
- `kms verify-mac --message <blob> --key-id <string> --mac-algorithm <string> --mac <blob>`
Flags: `--dry-run`, `--grant-tokens`, `--key-id`, `--mac`, `--mac-algorithm`, `--message`
Confirms a MAC produced by `generate-mac`: reports it valid for the same key, message, and algorithm.

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
