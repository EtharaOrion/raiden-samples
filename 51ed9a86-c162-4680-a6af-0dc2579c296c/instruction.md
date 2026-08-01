# Build an `aws cognito-idp` CLI

## Application overview

You will implement the following `aws cognito-idp` commands:
`cognito-idp admin-create-user`, `cognito-idp admin-get-user`, `cognito-idp create-user-pool`, `cognito-idp create-user-pool-client`, `cognito-idp delete-user-pool`, `cognito-idp describe-user-pool`, `cognito-idp list-user-pools`, `cognito-idp list-users`.

Your code is invoked as a subprocess:

```bash
aws cognito-idp <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence of
cognito-idp operations behaves correctly end-to-end.

## Commands

### `cognito-idp admin-create-user`
- `cognito-idp admin-create-user --user-pool-id <user-pool-id> --username <username>`
- `cognito-idp admin-create-user --user-pool-id <user-pool-id> --username <username> --message-action SUPPRESS`
- `cognito-idp admin-create-user --user-pool-id <user-pool-id> --username <username> --temporary-password <password> --desired-delivery-mediums <mediums>`
- `cognito-idp admin-create-user --user-pool-id <user-pool-id> --username <username> --user-attributes <json> --validation-data <json> --client-metadata <json>`
Flags: `--client-metadata`, `--desired-delivery-mediums`, `--force-alias-creation`, `--message-action`, `--temporary-password`, `--user-attributes`, `--user-pool-id`, `--username`, `--validation-data`
Creates a new user in the specified pool and returns the user record; the user is immediately visible to `admin-get-user` and `list-users`.
`--user-pool-id` and `--username` are both required.

### `cognito-idp admin-get-user`
- `cognito-idp admin-get-user --user-pool-id <user-pool-id> --username <username>`
Flags: `--user-pool-id`, `--username`
Returns the user record for a user previously created by `admin-create-user`.
Both `--user-pool-id` and `--username` are required.

### `cognito-idp create-user-pool`
- `cognito-idp create-user-pool --pool-name <pool-name>`
- `cognito-idp create-user-pool --pool-name <pool-name> --deletion-protection ACTIVE`
- `cognito-idp create-user-pool --pool-name <pool-name> --mfa-configuration OPTIONAL --user-pool-tier ESSENTIALS`
- `cognito-idp create-user-pool --pool-name <pool-name> --policies <json> --schema <json> --lambda-config <json>`
Flags: `--account-recovery-setting`, `--admin-create-user-config`, `--alias-attributes`, `--auto-verified-attributes`, `--deletion-protection`, `--device-configuration`, `--email-configuration`, `--email-verification-message`, `--email-verification-subject`, `--lambda-config`, `--mfa-configuration`, `--policies`, `--pool-name`, `--schema`, `--sms-authentication-message`, `--sms-configuration`, `--sms-verification-message`, `--user-attribute-update-settings`, `--user-pool-add-ons`, `--user-pool-tags`, `--user-pool-tier`, `--username-attributes`, `--username-configuration`, `--verification-message-template`
Creates a new user pool and returns its metadata, including the generated `UserPoolId`; the pool immediately appears in `list-user-pools` and is accessible via `describe-user-pool`.
`--pool-name` is required; values of 512 characters or more are a usage error.

### `cognito-idp create-user-pool-client`
- `cognito-idp create-user-pool-client --user-pool-id <user-pool-id> --client-name <client-name>`
- `cognito-idp create-user-pool-client --user-pool-id <user-pool-id> --client-name <client-name> --prevent-user-existence-errors ENABLED`
- `cognito-idp create-user-pool-client --user-pool-id <user-pool-id> --client-name <client-name> --refresh-token-validity <n> --access-token-validity <n> --id-token-validity <n>`
- `cognito-idp create-user-pool-client --user-pool-id <user-pool-id> --client-name <client-name> --callback-ur-ls <urls> --logout-ur-ls <urls> --allowed-o-auth-flows <flows>`
Flags: `--access-token-validity`, `--allowed-o-auth-flows`, `--allowed-o-auth-flows-user-pool-client`, `--allowed-o-auth-scopes`, `--analytics-configuration`, `--auth-session-validity`, `--callback-ur-ls`, `--client-name`, `--default-redirect-uri`, `--enable-propagate-additional-user-context-data`, `--enable-token-revocation`, `--explicit-auth-flows`, `--generate-secret`, `--id-token-validity`, `--logout-ur-ls`, `--prevent-user-existence-errors`, `--read-attributes`, `--refresh-token-rotation`, `--refresh-token-validity`, `--supported-identity-providers`, `--token-validity-units`, `--user-pool-id`, `--write-attributes`
Creates an app client in the specified pool and returns the client record.
Both `--user-pool-id` and `--client-name` are required.

### `cognito-idp delete-user-pool`
- `cognito-idp delete-user-pool --user-pool-id <user-pool-id>`
Flags: `--user-pool-id`
Deletes the named pool; after success the pool no longer appears in `list-user-pools` and `describe-user-pool` returns a service error for it.
`--user-pool-id` is required.

### `cognito-idp describe-user-pool`
- `cognito-idp describe-user-pool --user-pool-id <user-pool-id>`
Flags: `--user-pool-id`
Returns the metadata for a pool created by `create-user-pool`.
`--user-pool-id` is required.

### `cognito-idp list-user-pools`
- `cognito-idp list-user-pools --max-results <n>`
- `cognito-idp list-user-pools --max-results <n> --next-token <token>`
Flags: `--max-results`, `--next-token`
Lists all user pools, reflecting every prior `create-user-pool` and `delete-user-pool`.
`--max-results` is required and must be in the range 1 to 60; 0 and values above 60 are usage errors.

### `cognito-idp list-users`
- `cognito-idp list-users --user-pool-id <user-pool-id>`
- `cognito-idp list-users --user-pool-id <user-pool-id> --limit <n>`
- `cognito-idp list-users --user-pool-id <user-pool-id> --filter <filter> --pagination-token <token>`
- `cognito-idp list-users --user-pool-id <user-pool-id> --attributes-to-get <attrs> --limit <n>`
Flags: `--attributes-to-get`, `--filter`, `--limit`, `--pagination-token`, `--user-pool-id`
Lists users in the named pool, reflecting every prior `admin-create-user`.
`--user-pool-id` is required.

## Cross-command behavior

State must remain consistent across the command set:

- After `create-user-pool`, the pool appears in `list-user-pools` and is accessible via `describe-user-pool`.
- After `admin-create-user`, the user appears in `list-users` and is retrievable via `admin-get-user`.
- After `create-user-pool-client`, the client is associated with its pool; the pool must exist at creation time.
- After `delete-user-pool`, the pool no longer appears in `list-user-pools` and service operations against it return a service error.
- Listings reflect the cumulative effect of all prior commands at every step.

## Argument validation

The same per-flag rules apply to every command above:

- A missing required flag, an unknown flag, a repeated flag, or an empty flag value is a parameter/usage error (exit 252).
- A grossly oversized value (512 characters or more) supplied to any identifier or name flag is a parameter/usage error.
- `--user-pool-id` must be at most 55 characters; 56 or more is a usage error.
- `--username` must be at most 128 characters; 129 or more is a usage error.
- `--filter` must be at most 256 characters; 257 or more is a usage error.
- `--temporary-password` must be at most 255 characters; 256 or more is a usage error.
- `--max-results` must be 1 to 60; 0 or any value above 60 is a usage error.
- `--limit` must be 1 to 60; values below 1 or above 60 are usage errors.
- A well-formed argument naming a resource that does not exist is a service error (exit 254), not a usage error.

## Implementation constraints

- Your submission must be an executable named `aws` on `$PATH`. It may be written in any language available in the image. `/workspace/submission/` is first on `$PATH` as a convenient writable install location, but any directory on `$PATH` is acceptable, and helper files may live alongside it.
- Use only what the image already provides; no additional packages may be fetched.
- Do not import `awscli` or shell out to the real `aws` binary.
- AWS credentials and endpoint are set in the environment; do not override the service address, region, or credentials in code.
- Success output (JSON) goes to **stdout**; errors go to **stderr**. Do not mix them.
- Do not surface raw library tracebacks; print a brief user-facing error string instead.
- Do not fabricate flags that do not exist upstream. Do not validate input client-side; the service rejects malformed input with a validation error.

## Output contract

A correct implementation produces output in the *shape* described below,
names the *class* of any error reported, uses the documented exit-code
set, and never surfaces a runtime stack trace. Specific verbs and the
exact wording of any message are deliberately not enumerated here: derive
them from the underlying cognito-idp service semantics and standard
`aws cognito-idp` conventions.

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
- Tests match the failure *class* against one of these shapes, not
  verbatim wording, so any spec-compliant phrasing is accepted.
- No runtime stack trace is emitted under any condition.

### Exit codes

The exit code on termination is one of `{0, 1, 252, 254, 255}`:

- `0`: success
- `1`: application error (an operation was attempted and failed)
- `252`: parameter/usage error (unknown flag, missing/extra argument,
  malformed value)
- `254`: service-modeled error (the service returned a modeled exception)
- `255`: other or general error

Tests only check `returncode != 0` on failure; any non-zero code in this set
is acceptable.
