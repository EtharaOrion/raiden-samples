# Build an `aws cognito-idp` CLI

## Application overview

You will implement the following `aws cognito-idp` commands:
`cognito-idp add-custom-attributes`, `cognito-idp admin-add-user-to-group`, `cognito-idp admin-confirm-sign-up`, `cognito-idp admin-create-user`, `cognito-idp admin-delete-user-attributes`, `cognito-idp admin-get-user`, `cognito-idp admin-list-groups-for-user`, `cognito-idp admin-remove-user-from-group`, `cognito-idp admin-set-user-password`, `cognito-idp create-group`, `cognito-idp create-user-pool`, `cognito-idp create-user-pool-client`, `cognito-idp delete-group`, `cognito-idp delete-user-pool`, `cognito-idp delete-user-pool-client`, `cognito-idp describe-user-pool`, `cognito-idp describe-user-pool-client`, `cognito-idp get-group`, `cognito-idp get-user-pool-mfa-config`, `cognito-idp list-groups`, `cognito-idp list-user-pool-clients`, `cognito-idp list-user-pools`, `cognito-idp list-users`, `cognito-idp list-users-in-group`, `cognito-idp set-user-pool-mfa-config`, `cognito-idp update-group`, `cognito-idp update-user-pool`, `cognito-idp update-user-pool-client`.

Your code is invoked as a subprocess:

```bash
aws cognito-idp <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence of
cognito-idp operations behaves correctly end-to-end.

## Commands

### `cognito-idp add-custom-attributes`
- `cognito-idp add-custom-attributes --user-pool-id <string> --custom-attributes <json>`
Flags: `--custom-attributes`, `--user-pool-id`
Registers custom schema attributes on the pool; afterwards the attribute appears in the pool's schema (via `describe-user-pool`) and is referenced on users as `custom:<name>`.

### `cognito-idp admin-add-user-to-group`
- `cognito-idp admin-add-user-to-group --user-pool-id <string> --username <string> --group-name <string>`
Flags: `--group-name`, `--user-pool-id`, `--username`
After success the membership is visible from both directions: `admin-list-groups-for-user` lists the group and `list-users-in-group` lists the user.

### `cognito-idp admin-confirm-sign-up`
- `cognito-idp admin-confirm-sign-up --user-pool-id <string> --username <string>`
Flags: `--client-metadata`, `--user-pool-id`, `--username`
Moves the user to CONFIRMED status (visible via `admin-get-user`).

### `cognito-idp admin-create-user`
- `cognito-idp admin-create-user --user-pool-id <string> --username <string>`
Flags: `--client-metadata`, `--desired-delivery-mediums`, `--force-alias-creation`, `--message-action`, `--temporary-password`, `--user-attributes`, `--user-pool-id`, `--username`, `--validation-data`
Creates a user under the caller-supplied username; the user is visible via `admin-get-user` and `list-users`.
Creating the same username again fails with a username-exists error class; a missing pool fails with a resource-not-found error class.

### `cognito-idp admin-delete-user-attributes`
- `cognito-idp admin-delete-user-attributes --user-pool-id <string> --username <string> --user-attribute-names <json>`
Flags: `--user-attribute-names`, `--user-pool-id`, `--username`
Removes the named attributes; they disappear from `admin-get-user`.

### `cognito-idp admin-get-user`
- `cognito-idp admin-get-user --user-pool-id <string> --username <string>`
Flags: `--user-pool-id`, `--username`
Reports the user's username, status, enabled flag, and attributes; attribute, password, enable/disable, and confirm operations are all visible here.
A missing user fails with a user-not-found error class.

### `cognito-idp admin-list-groups-for-user`
- `cognito-idp admin-list-groups-for-user --username <string> --user-pool-id <string>`
Flags: `--limit`, `--next-token`, `--user-pool-id`, `--username`
Reflects the user's current group memberships, order-independent.

### `cognito-idp admin-remove-user-from-group`
- `cognito-idp admin-remove-user-from-group --user-pool-id <string> --username <string> --group-name <string>`
Flags: `--group-name`, `--user-pool-id`, `--username`
After success the membership disappears from `admin-list-groups-for-user` and `list-users-in-group`.

### `cognito-idp admin-set-user-password`
- `cognito-idp admin-set-user-password --user-pool-id <string> --username <string> --password <string>`
Flags: `--password`, `--permanent`, `--user-pool-id`, `--username`
Sets the user's password; with the permanent flag the user's status becomes CONFIRMED (visible via `admin-get-user`).

### `cognito-idp create-group`
- `cognito-idp create-group --group-name <string> --user-pool-id <string>`
Flags: `--description`, `--group-name`, `--precedence`, `--role-arn`, `--user-pool-id`
Creates a group under the caller-supplied group name; the group appears in `list-groups` and `get-group` reports it.

### `cognito-idp create-user-pool`
- `cognito-idp create-user-pool --pool-name <value> --deletion-protection ACTIVE`
Flags: `--account-recovery-setting`, `--admin-create-user-config`, `--alias-attributes`, `--auto-verified-attributes`, `--deletion-protection`, `--device-configuration`, `--email-configuration`, `--email-verification-message`, `--email-verification-subject`, `--issuer-configuration`, `--key-configuration`, `--lambda-config`, `--mfa-configuration`, `--policies`, `--pool-name`, `--schema`, `--sms-authentication-message`, `--sms-configuration`, `--sms-verification-message`, `--user-attribute-update-settings`, `--user-pool-add-ons`, `--user-pool-tags`, `--user-pool-tier`, `--username-attributes`, `--username-configuration`, `--verification-message-template`
Creates a pool and returns its id; the pool appears in `list-user-pools` and `describe-user-pool` reports it.
A brand-new pool contains no users, clients, or groups.

### `cognito-idp create-user-pool-client`
- `cognito-idp create-user-pool-client --user-pool-id <string> --client-name <string>`
Flags: `--access-token-validity`, `--allowed-o-auth-flows`, `--allowed-o-auth-flows-user-pool-client`, `--allowed-o-auth-scopes`, `--analytics-configuration`, `--auth-session-validity`, `--callback-ur-ls`, `--client-name`, `--client-secret`, `--default-redirect-uri`, `--enable-propagate-additional-user-context-data`, `--enable-token-revocation`, `--explicit-auth-flows`, `--generate-secret`, `--id-token-validity`, `--logout-ur-ls`, `--prevent-user-existence-errors`, `--read-attributes`, `--refresh-token-rotation`, `--refresh-token-validity`, `--supported-identity-providers`, `--token-validity-units`, `--user-pool-id`, `--write-attributes`
Creates an app client in the pool and returns its client id; the client appears in `list-user-pool-clients`.

### `cognito-idp delete-group`
- `cognito-idp delete-group --group-name <string> --user-pool-id <string>`
Flags: `--group-name`, `--user-pool-id`
After success the group disappears from `list-groups` and `get-group` fails with a resource-not-found error class.

### `cognito-idp delete-user-pool`
- `cognito-idp delete-user-pool --user-pool-id <string>`
Flags: `--user-pool-id`
After success the pool disappears from `list-user-pools`; deletion cascades to the pool's clients, users, and groups, and further operations on the pool id fail with a resource-not-found error class.

### `cognito-idp delete-user-pool-client`
- `cognito-idp delete-user-pool-client --user-pool-id <string> --client-id <string>`
Flags: `--client-id`, `--user-pool-id`
After success the client disappears from `list-user-pool-clients` and describing it fails with a resource-not-found error class.

### `cognito-idp describe-user-pool`
- `cognito-idp describe-user-pool --user-pool-id <string>`
Flags: `--user-pool-id`
Reports the pool object, including its schema attributes; updates and custom attributes added later are visible here.
A missing pool id fails with a resource-not-found error class.

### `cognito-idp describe-user-pool-client`
- `cognito-idp describe-user-pool-client --user-pool-id <string> --client-id <string>`
Flags: `--client-id`, `--user-pool-id`
Reports the client (id, name, owning pool); a missing client or pool fails with a resource-not-found error class.

### `cognito-idp get-group`
- `cognito-idp get-group --group-name <string> --user-pool-id <string>`
Flags: `--group-name`, `--user-pool-id`
Reports the group (name, owning pool, description, precedence); a missing group fails with a resource-not-found error class.

### `cognito-idp get-user-pool-mfa-config`
- `cognito-idp get-user-pool-mfa-config --user-pool-id <string>`
Flags: `--user-pool-id`
Reports the pool's MFA configuration (OFF, ON, or OPTIONAL).

### `cognito-idp list-groups`
- `cognito-idp list-groups --user-pool-id <string>`
Flags: `--limit`, `--next-token`, `--user-pool-id`
Reflects the pool's current groups after creates and deletes.

### `cognito-idp list-user-pool-clients`
- `cognito-idp list-user-pool-clients --user-pool-id <string>`
Flags: `--max-results`, `--next-token`, `--user-pool-id`
Reflects the pool's current clients after creates and deletes.

### `cognito-idp list-user-pools`
- `cognito-idp list-user-pools --max-results <number>`
Flags: `--max-results`, `--next-token`
Reflects exactly the cumulative effect of pool creates and deletes.

### `cognito-idp list-users`
- `cognito-idp list-users --user-pool-id <string>`
Flags: `--attributes-to-get`, `--filter`, `--limit`, `--pagination-token`, `--user-pool-id`
Reflects the pool's current users after creates and deletes.

### `cognito-idp list-users-in-group`
- `cognito-idp list-users-in-group --user-pool-id <string> --group-name <string>`
Flags: `--group-name`, `--limit`, `--next-token`, `--user-pool-id`
Reflects the group's current members, order-independent.

### `cognito-idp set-user-pool-mfa-config`
- `cognito-idp set-user-pool-mfa-config --user-pool-id <string>`
Flags: `--email-mfa-configuration`, `--mfa-configuration`, `--sms-mfa-configuration`, `--software-token-mfa-configuration`, `--user-pool-id`, `--web-authn-configuration`
Sets the pool's MFA configuration; the new value round-trips through `get-user-pool-mfa-config`.

### `cognito-idp update-group`
- `cognito-idp update-group --group-name <string> --user-pool-id <string>`
Flags: `--description`, `--group-name`, `--precedence`, `--role-arn`, `--user-pool-id`
Applies group changes (description, precedence); the updated values are visible via `get-group`.

### `cognito-idp update-user-pool`
- `cognito-idp update-user-pool --user-pool-id <string>`
Flags: `--account-recovery-setting`, `--admin-create-user-config`, `--auto-verified-attributes`, `--deletion-protection`, `--device-configuration`, `--email-configuration`, `--email-verification-message`, `--email-verification-subject`, `--issuer-configuration`, `--key-configuration`, `--lambda-config`, `--mfa-configuration`, `--policies`, `--pool-name`, `--sms-authentication-message`, `--sms-configuration`, `--sms-verification-message`, `--user-attribute-update-settings`, `--user-pool-add-ons`, `--user-pool-id`, `--user-pool-tags`, `--user-pool-tier`, `--verification-message-template`
Applies pool-level configuration changes; the updated values are visible via `describe-user-pool`.

### `cognito-idp update-user-pool-client`
- `cognito-idp update-user-pool-client --user-pool-id <string> --client-id <string>`
Flags: `--access-token-validity`, `--allowed-o-auth-flows`, `--allowed-o-auth-flows-user-pool-client`, `--allowed-o-auth-scopes`, `--analytics-configuration`, `--auth-session-validity`, `--callback-ur-ls`, `--client-id`, `--client-name`, `--default-redirect-uri`, `--enable-propagate-additional-user-context-data`, `--enable-token-revocation`, `--explicit-auth-flows`, `--id-token-validity`, `--logout-ur-ls`, `--prevent-user-existence-errors`, `--read-attributes`, `--refresh-token-rotation`, `--refresh-token-validity`, `--supported-identity-providers`, `--token-validity-units`, `--user-pool-id`, `--write-attributes`
Applies client configuration changes; the updated values are visible via `describe-user-pool-client`.

## Cross-command behavior

State must remain consistent across the command set:

- After `create-user-pool`, the pool id works across every other command; after `delete-user-pool`, they all fail with a resource-not-found error class (deletion cascades to clients, users, and groups).
- A user created by `admin-create-user` is visible via `admin-get-user` and `list-users`; attribute, password, enable/disable, and confirm changes are all observable through `admin-get-user`.
- Group membership added by `admin-add-user-to-group` is visible from both `admin-list-groups-for-user` and `list-users-in-group`, and disappears after `admin-remove-user-from-group`.
- Clients created by `create-user-pool-client` are observable via `describe-user-pool-client` and `list-user-pool-clients` until deleted.
- Custom attributes registered by `add-custom-attributes` appear in the pool schema and on users as `custom:<name>`.

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
