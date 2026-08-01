# Build an `aws kms` CLI

## Application overview

You will implement the following `aws kms` commands:
`kms create-alias`, `kms create-key`, `kms decrypt`, `kms describe-key`, `kms disable-key`, `kms enable-key`, `kms encrypt`, `kms generate-data-key`, `kms list-aliases`, `kms list-keys`, `kms schedule-key-deletion`.

Your code is invoked as a subprocess:

```bash
aws kms <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence of kms
operations behaves correctly end-to-end.

## Commands

### `kms create-alias`
- `kms create-alias --alias-name alias/<name> --target-key-id <key-id>`
Flags: `--alias-name`, `--target-key-id`
Binds a friendly alias to an existing key. After success the alias appears in `list-aliases`, and commands that take a key id also accept the alias.
Alias names follow the standard KMS `alias/<name>` form and are at most 256 characters.

### `kms create-key`
- `kms create-key`
- `kms create-key --key-usage ENCRYPT_DECRYPT --key-spec SYMMETRIC_DEFAULT`
- `kms create-key --description <text> --policy <json> --tags <json> --multi-region <bool>`
Flags: `--policy`, `--description`, `--key-usage`, `--customer-master-key-spec`, `--key-spec`, `--origin`, `--custom-key-store-id`, `--bypass-policy-lockout-safety-check`, `--tags`, `--multi-region`, `--xks-key-id`
Creates a customer master key and returns its metadata. The new key id is immediately visible to `list-keys` and `describe-key` and usable by the cryptographic commands.
Defaults match KMS: a `SYMMETRIC_DEFAULT` key with `ENCRYPT_DECRYPT` usage, enabled on creation.

### `kms decrypt`
- `kms decrypt --ciphertext-blob <blob>`
- `kms decrypt --ciphertext-blob <blob> --key-id <key-id> --encryption-algorithm SYMMETRIC_DEFAULT`
Flags: `--ciphertext-blob`, `--encryption-context`, `--grant-tokens`, `--key-id`, `--encryption-algorithm`, `--recipient`, `--dry-run`
Decrypts a blob produced by `encrypt` and returns the key id, the plaintext, and the algorithm used.
Round-trip invariant: decrypting the ciphertext of `encrypt` yields the original plaintext.

### `kms describe-key`
- `kms describe-key --key-id <key-id-or-alias>`
Flags: `--key-id`, `--grant-tokens`
Returns the key metadata document, including the key id, state, usage and spec.
Reflects the effect of earlier commands: the reported state tracks enable/disable and scheduled deletion.

### `kms disable-key`
- `kms disable-key --key-id <key-id>`
Flags: `--key-id`
Moves the key to the disabled state; `describe-key` reports it as disabled afterwards.
A disabled key cannot be used for cryptographic operations until re-enabled.

### `kms enable-key`
- `kms enable-key --key-id <key-id>`
Flags: `--key-id`
Returns the key to the enabled state; `describe-key` reports it as enabled afterwards and cryptographic operations succeed again.
Enabling an already-enabled key is idempotent.

### `kms encrypt`
- `kms encrypt --key-id <key-id> --plaintext <blob>`
- `kms encrypt --key-id <key-id> --plaintext <blob> --encryption-algorithm SYMMETRIC_DEFAULT --encryption-context <json>`
Flags: `--key-id`, `--plaintext`, `--encryption-context`, `--grant-tokens`, `--encryption-algorithm`, `--dry-run`
Encrypts the plaintext under the named key and returns the ciphertext blob, the key id, and the algorithm used.
The ciphertext it returns must be accepted by `decrypt`.

### `kms generate-data-key`
- `kms generate-data-key --key-id <key-id> --key-spec AES_256`
- `kms generate-data-key --key-id <key-id> --number-of-bytes <1-1024>`
Flags: `--key-id`, `--encryption-context`, `--number-of-bytes`, `--key-spec`, `--grant-tokens`, `--recipient`, `--dry-run`
Returns a data key both in plaintext and encrypted under the CMK, together with the key id.
The returned ciphertext must decrypt back to the returned plaintext.

### `kms list-aliases`
- `kms list-aliases`
- `kms list-aliases --key-id <key-id>`
- `kms list-aliases --limit <n> --marker <token>`
Flags: `--key-id`, `--limit`, `--marker`
Lists aliases, reflecting every prior `create-alias`. `--key-id` restricts the listing to aliases bound to that key.
`--limit` is 1 to 1000 and caps the page size; a truncated listing carries a marker to pass back via `--marker`.

### `kms list-keys`
- `kms list-keys`
- `kms list-keys --limit <n> --marker <token>`
Flags: `--limit`, `--marker`
Lists key ids, reflecting every prior `create-key`.
`--limit` is 1 to 1000 and caps the page size; a truncated listing carries a marker to pass back via `--marker`.

### `kms schedule-key-deletion`
- `kms schedule-key-deletion --key-id <key-id>`
- `kms schedule-key-deletion --key-id <key-id> --pending-window-in-days <days>`
Flags: `--key-id`, `--pending-window-in-days`
Marks the key for deletion and returns the key id and the deletion date; `describe-key` then reports the pending-deletion state.
`--pending-window-in-days` accepts 1 to 365.

## Cross-command behavior

State must remain consistent across the command set:

- After `create-key`, the key id is listed by `list-keys`, described by
  `describe-key`, and usable by `encrypt` and `generate-data-key`.
- After `create-alias`, the alias appears in `list-aliases` and resolves
  anywhere a key id is accepted.
- `encrypt` then `decrypt` round-trips to the original plaintext;
  `generate-data-key`'s ciphertext decrypts to the plaintext it returned.
- `disable-key`, `enable-key`, and `schedule-key-deletion` are observable
  through the key state reported by `describe-key`, and gate whether
  cryptographic operations succeed.
- Listings reflect exactly the cumulative effect of all prior commands at
  every step.

## Argument validation

The same per-flag rules apply to every command above, and are exercised for
each of them:

- A missing required flag, an unknown flag, a repeated flag, or an empty flag
  value is a parameter/usage error.
- A grossly oversized value (for example a 512-character key id, or an alias
  name past its 256-character limit) is a parameter/usage error.
- Numeric flags outside their documented range (`--limit`,
  `--number-of-bytes`, `--pending-window-in-days`) are parameter/usage errors,
  as is an over-long `--grant-tokens` value.
- A well-formed argument naming a resource that does not exist is a *service*
  error, not a usage error.

## Implementation constraints

- Your submission must be an executable named `aws` on `$PATH`. It may be
  written in any language available in the image. `/workspace/submission/` is
  first on `$PATH` as a convenient writable install location, but any
  directory on `$PATH` is acceptable, and helper files may live alongside it.
- Use only what the image already provides; no additional packages may be
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

## Output contract

A correct implementation produces output in the *shape* described below,
names the *class* of any error reported, uses the documented exit-code set,
and never surfaces a runtime stack trace. Specific verbs and the exact
wording of any message are deliberately not enumerated here: derive them from
the underlying kms service semantics and standard `aws kms` conventions.

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
- Tests match the failure *class* against one of these shapes — not verbatim
  wording — so any spec-compliant phrasing is accepted.
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
