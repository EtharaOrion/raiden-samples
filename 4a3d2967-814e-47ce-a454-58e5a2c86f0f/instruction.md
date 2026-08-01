# Build an `aws dynamodb` CLI

## Application overview

You will implement the following `aws dynamodb` commands:
`dynamodb query`, `dynamodb scan`.

Your code is invoked as a subprocess:

```bash
aws dynamodb <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence such as
create-table, put-item, get-item, query behaves correctly end-to-end.

## Commands

### Command: `dynamodb query`

Observed argv patterns:

- `dynamodb query --table-name <string>`
- `dynamodb query --table-name <string> --key-condition-expression id = :pk --expression-attribute-values {":pk":{"S":"k1"}}`
- `dynamodb query --table-name <string> --key-condition-expression id = :pk --expression-attribute-values {":pk":{"S":"k1"}} --limit 1`
- `dynamodb query --table-name <string_v1>`
- `dynamodb query --table-name <string_v2>`
- `dynamodb query --table-name <string_v3>`
- `dynamodb query --table-name <string_v4>`
- `dynamodb query --table-name <string_v5>`
- `dynamodb query --table-name <string_v6>`
- `dynamodb query --table-name <string_v7>`

Documented flags: `--attributes-to-get`, `--conditional-operator`, `--consistent-read`, `--exclusive-start-key`, `--expression-attribute-names`, `--expression-attribute-values`, `--filter-expression`, `--index-name`, `--key-condition-expression`, `--key-conditions`, `--limit`, `--projection-expression`, `--query-filter`, `--return-consumed-capacity`, `--scan-index-forward`, `--select`, `--table-name`

Flags observed: `--attributes-to-get`, `--conditional-operator`, `--consistent-read`, `--exclusive-start-key`, `--expression-attribute-names`, `--expression-attribute-values`, `--filter-expression`, `--index-name`, `--key-condition-expression`, `--key-conditions`, `--limit`, `--projection-expression`, `--query-filter`, `--return-consumed-capacity`, `--scan-index-forward`, `--select`, `--table-name`

Behaviour & state expectations:

- Returns items whose partition key matches the `--key-condition-expression`
  (e.g. `pk = :v`), as `Items` on stdout.
- Assert result membership as an order-insensitive set unless a sort-key range
  is specified.
- Querying on a non-key attribute in the key condition FAILS with `ValidationException`.

Error cases:
- `dynamodb query --table-name <string>` -> exit `254`
- `dynamodb query` -> exit `252`
- `dynamodb query --table-name <string> --not-a-real-flag x` -> exit `252`
- `dynamodb query --table-name ` -> exit `252`
- `dynamodb query --table-name <string> --attribute-definitions {not valid json` -> exit `252`
- `dynamodb query --table-name <string> --table-name <string>` -> exit `252`
- `dynamodb query --table-name <oversized-value:512-chars>` -> exit `252`

### Command: `dynamodb scan`

Observed argv patterns:

- `dynamodb scan --table-name <string>`
- `dynamodb scan --table-name <string_v1>`
- `dynamodb scan --table-name <string_v2>`
- `dynamodb scan --table-name <string_v3>`
- `dynamodb scan --table-name <string_v4>`
- `dynamodb scan --table-name <string_v5>`
- `dynamodb scan --table-name <string_v6>`
- `dynamodb scan --table-name <string_v7>`

Documented flags: `--attributes-to-get`, `--conditional-operator`, `--consistent-read`, `--exclusive-start-key`, `--expression-attribute-names`, `--expression-attribute-values`, `--filter-expression`, `--index-name`, `--limit`, `--projection-expression`, `--return-consumed-capacity`, `--scan-filter`, `--segment`, `--select`, `--table-name`, `--total-segments`

Flags observed: `--attributes-to-get`, `--conditional-operator`, `--consistent-read`, `--exclusive-start-key`, `--expression-attribute-names`, `--expression-attribute-values`, `--filter-expression`, `--index-name`, `--limit`, `--projection-expression`, `--return-consumed-capacity`, `--scan-filter`, `--segment`, `--select`, `--table-name`, `--total-segments`

Error cases:
- `dynamodb scan --table-name <string>` -> exit `254`
- `dynamodb scan` -> exit `252`
- `dynamodb scan --table-name <string> --not-a-real-flag x` -> exit `252`
- `dynamodb scan --table-name ` -> exit `252`
- `dynamodb scan --table-name <string> --attribute-definitions {not valid json` -> exit `252`
- `dynamodb scan --table-name <string> --table-name <string>` -> exit `252`
- `dynamodb scan --table-name <oversized-value:512-chars>` -> exit `252`

## Cross-command behavior

State must remain consistent across the command set:

- `query` returns exactly the items previously written under the partition key.

## Data model notes

- Item and key values use DynamoDB AttributeValue form; **numbers are JSON
  strings** (`{"N": "5"}`).
- Tables use on-demand capacity (`PAY_PER_REQUEST`).

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
- Do not fabricate flags that do not exist upstream. Do not validate table
  names client-side; the service rejects malformed input with
  `ValidationException`.
- Your submission must be an executable named `aws` on `$PATH`. It may be
  written in any language. The image provides `/workspace/submission/` first
  on `$PATH` as a convenient writable install location, but any directory on
  `$PATH` is acceptable. Helper files may live alongside it.

## Output contract

A correct implementation produces output in the *shape* described below,
names the *class* of any error reported, uses the documented exit-code
set, and never surfaces a runtime stack trace. Specific verbs and the
exact wording of any message are deliberately not enumerated here: derive
them from the underlying DynamoDB service semantics and standard
`aws dynamodb` conventions.

### stdout (success path)

- A successful command writes the operation's DynamoDB JSON response
  document to stdout (parseable with `json.loads`).
- Assertions are on JSON semantic content, never on key order, whitespace,
  or any textual preamble.
- stderr is empty on success.

### stderr (failure path)

- stdout is empty on failure.
- A human-readable error line is written to stderr that identifies the
  failure *class*. Any of the following shapes is acceptable:
  - the underlying AWS service error envelope:
    `An error occurred (<ErrorCode>) when calling the <Operation> operation: <message>`
  - a bare `<ErrorCode>: <message>` line naming the DynamoDB error code
    (for example, `ResourceNotFoundException`, `ResourceInUseException`,
    `ConditionalCheckFailedException`, `ValidationException`)
  - a client-side usage-error line whose prefix names the failure class
    (for example, `usage: ...`, `Parameter validation failed: ...`,
    `Unknown options: ...`)
- Tests match the failure *class* against one of these shapes — not
  verbatim wording — so any spec-compliant phrasing is accepted.
- No runtime stack trace is emitted under any condition.

### Exit codes

The exit code on termination is one of `{0, 1, 252, 254, 255}`:

- `0` — success
- `1` — application error (a DynamoDB operation was attempted and failed)
- `252` — parameter/usage error (unknown flag, missing/extra argument,
  malformed value)
- `254` — service-modeled error (the service returned a modeled exception
  such as `ResourceNotFoundException`)
- `255` — other or general error

Tests only check `returncode != 0` on failure; any non-zero code in this set
is acceptable.

