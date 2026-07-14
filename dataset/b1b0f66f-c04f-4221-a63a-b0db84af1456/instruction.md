# Build an `aws dynamodb` CLI

## Application overview

You will implement the following `aws dynamodb` commands:
`dynamodb delete-item`, `dynamodb delete-table`, `dynamodb get-item`, `dynamodb list-tables`, `dynamodb query`, `dynamodb update-item`.

Your code is invoked as a subprocess:

```bash
aws dynamodb <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence such as
create-table, put-item, get-item, query behaves correctly end-to-end.

## Commands

### Command: `dynamodb delete-item`

Observed argv patterns:

- `dynamodb delete-item --table-name <string> --key <json>`
- `dynamodb delete-item --table-name <string> --key {"id":{"S":"never-existed"}} --condition-expression attribute_exists(id)`
- `dynamodb delete-item --table-name <string_v1> --key <json_v1>`
- `dynamodb delete-item --table-name <string_v2> --key <json_v2>`
- `dynamodb delete-item --table-name <string_v3> --key <json_v3>`
- `dynamodb delete-item --table-name <string_v4> --key <json_v4>`
- `dynamodb delete-item --table-name <string_v5> --key <json_v5>`
- `dynamodb delete-item --table-name <string_v6> --key <json_v6>`
- `dynamodb delete-item --table-name <string_v7> --key <json_v7>`

Documented flags: `--condition-expression`, `--conditional-operator`, `--expected`, `--expression-attribute-names`, `--expression-attribute-values`, `--key`, `--return-consumed-capacity`, `--return-item-collection-metrics`, `--return-values`, `--return-values-on-condition-check-failure`, `--table-name`

Flags observed: `--condition-expression`, `--conditional-operator`, `--expected`, `--expression-attribute-names`, `--expression-attribute-values`, `--key`, `--return-consumed-capacity`, `--return-item-collection-metrics`, `--return-values`, `--return-values-on-condition-check-failure`, `--table-name`

Behaviour & state expectations:

- After success `get-item` on the key returns no `Item`.
- Deleting a non-existent key SUCCEEDS silently (idempotent).
- A failing `--condition-expression` FAILS with `ConditionalCheckFailedException`.

Error cases:
- `dynamodb delete-item --table-name <string> --key <json>` -> exit `254`
- `dynamodb delete-item --key <json>` -> exit `252`
- `dynamodb delete-item --table-name <string>` -> exit `252`
- `dynamodb delete-item --table-name <string> --key <json> --not-a-real-flag x` -> exit `252`
- `dynamodb delete-item --table-name  --key <json>` -> exit `252`
- `dynamodb delete-item --table-name <string> --key <json> --attribute-definitions {not valid json` -> exit `252`
- `dynamodb delete-item --table-name <string> --key <json> --table-name <string>` -> exit `252`
- `dynamodb delete-item --table-name <oversized-value:512-chars> --key <json>` -> exit `252`

### Command: `dynamodb delete-table`

Observed argv patterns:

- `dynamodb delete-table --table-name <string>`
- `dynamodb delete-table --table-name <string_v1>`
- `dynamodb delete-table --table-name <string_v2>`
- `dynamodb delete-table --table-name <string_v3>`
- `dynamodb delete-table --table-name <string_v4>`
- `dynamodb delete-table --table-name <string_v5>`
- `dynamodb delete-table --table-name <string_v6>`
- `dynamodb delete-table --table-name <string_v7>`

Documented flags: `--table-name`

Flags observed: `--table-name`

Behaviour & state expectations:

- After success the table no longer appears in `list-tables`.
- Deleting a non-existent table FAILS with `ResourceNotFoundException`.

Error cases:
- `dynamodb delete-table --table-name <string>` -> exit `254`
- `dynamodb delete-table` -> exit `252`
- `dynamodb delete-table --table-name <string> --not-a-real-flag x` -> exit `252`
- `dynamodb delete-table --table-name ` -> exit `252`
- `dynamodb delete-table --table-name <string> --attribute-definitions {not valid json` -> exit `252`
- `dynamodb delete-table --table-name <string> --table-name <string>` -> exit `252`
- `dynamodb delete-table --table-name <oversized-value:512-chars>` -> exit `252`

### Command: `dynamodb get-item`

Observed argv patterns:

- `dynamodb get-item --table-name <string> --key <json>`
- `dynamodb get-item --table-name <string> --key {"id":{"S":"k1"}} --consistent-read`
- `dynamodb get-item --table-name <string_v1> --key <json_v1>`
- `dynamodb get-item --table-name <string_v2> --key <json_v2>`
- `dynamodb get-item --table-name <string_v3> --key <json_v3>`
- `dynamodb get-item --table-name <string_v4> --key <json_v4>`
- `dynamodb get-item --table-name <string_v5> --key <json_v5>`
- `dynamodb get-item --table-name <string_v6> --key <json_v6>`
- `dynamodb get-item --table-name <string_v7> --key <json_v7>`

Documented flags: `--attributes-to-get`, `--consistent-read`, `--expression-attribute-names`, `--key`, `--projection-expression`, `--return-consumed-capacity`, `--table-name`

Flags observed: `--attributes-to-get`, `--consistent-read`, `--expression-attribute-names`, `--key`, `--projection-expression`, `--return-consumed-capacity`, `--table-name`

Behaviour & state expectations:

- Returns `{"Item": ...}` for an existing key; when the key is absent the
  response has NO `Item` member (exit 0).
- Reading from a missing table FAILS with `ResourceNotFoundException`.
- Reads are strongly consistent.

Error cases:
- `dynamodb get-item --table-name <string> --key <json>` -> exit `254`
- `dynamodb get-item --key <json>` -> exit `252`
- `dynamodb get-item --table-name <string>` -> exit `252`
- `dynamodb get-item --table-name <string> --key <json> --not-a-real-flag x` -> exit `252`
- `dynamodb get-item --table-name  --key <json>` -> exit `252`
- `dynamodb get-item --table-name <string> --key <json> --attribute-definitions {not valid json` -> exit `252`
- `dynamodb get-item --table-name <string> --key <json> --table-name <string>` -> exit `252`
- `dynamodb get-item --table-name <oversized-value:512-chars> --key <json>` -> exit `252`

### Command: `dynamodb list-tables`

Observed argv patterns:

- `dynamodb list-tables --limit 1`
- `dynamodb list-tables`

Documented flags: `--exclusive-start-table-name`, `--limit`

Flags observed: `--exclusive-start-table-name`, `--limit`

Behaviour & state expectations:

- Returns the set of existing table names on stdout as JSON.
- With no tables, succeeds (exit 0) with an empty `TableNames` list.
- Assert membership as a set — never rely on ordering.

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

### Command: `dynamodb update-item`

Observed argv patterns:

- `dynamodb update-item --table-name <string> --key <json>`
- `dynamodb update-item --table-name <string> --key {"id":{"S":"k1"}} --update-expression SET v = :v --expression-attribute-values {":v":{"S":"updated"}}`
- `dynamodb update-item --table-name <string> --key {"id":{"S":"k1"}} --update-expression ADD c :inc --expression-attribute-values {":inc":{"N":"1"}}`
- `dynamodb update-item --table-name <string_v1> --key <json_v1>`
- `dynamodb update-item --table-name <string_v2> --key <json_v2>`
- `dynamodb update-item --table-name <string_v3> --key <json_v3>`
- `dynamodb update-item --table-name <string_v4> --key <json_v4>`
- `dynamodb update-item --table-name <string_v5> --key <json_v5>`
- `dynamodb update-item --table-name <string_v6> --key <json_v6>`
- `dynamodb update-item --table-name <string_v7> --key <json_v7>`

Documented flags: `--attribute-updates`, `--condition-expression`, `--conditional-operator`, `--expected`, `--expression-attribute-names`, `--expression-attribute-values`, `--key`, `--return-consumed-capacity`, `--return-item-collection-metrics`, `--return-values`, `--return-values-on-condition-check-failure`, `--table-name`, `--update-expression`

Flags observed: `--attribute-updates`, `--condition-expression`, `--conditional-operator`, `--expected`, `--expression-attribute-names`, `--expression-attribute-values`, `--key`, `--return-consumed-capacity`, `--return-item-collection-metrics`, `--return-values`, `--return-values-on-condition-check-failure`, `--table-name`, `--update-expression`

Behaviour & state expectations:

- Applies an `UpdateExpression` (e.g. `SET #s = :v`) with
  `--expression-attribute-names` / `--expression-attribute-values`; afterward
  `get-item` reflects the change.
- A reserved word used unescaped in the expression FAILS with `ValidationException`
  (use `--expression-attribute-names` to alias reserved words like `Status`).
- A failing `--condition-expression` FAILS with `ConditionalCheckFailedException`
  and does NOT mutate the item.

Error cases:
- `dynamodb update-item --table-name <string> --key <json>` -> exit `254`
- `dynamodb update-item --key <json>` -> exit `252`
- `dynamodb update-item --table-name <string>` -> exit `252`
- `dynamodb update-item --table-name <string> --key <json> --not-a-real-flag x` -> exit `252`
- `dynamodb update-item --table-name  --key <json>` -> exit `252`
- `dynamodb update-item --table-name <string> --key <json> --attribute-definitions {not valid json` -> exit `252`
- `dynamodb update-item --table-name <string> --key <json> --table-name <string>` -> exit `252`
- `dynamodb update-item --table-name <oversized-value:512-chars> --key <json>` -> exit `252`

## Cross-command behavior

State must remain consistent across the command set:

- After `delete-item`, `get-item` on the key returns no `Item`.
- After `delete-table`, the table disappears from `list-tables`.
- `get-item` reflects exactly the cumulative effect of prior writes/updates.
- `query` returns exactly the items previously written under the partition key.
- After `update-item`, `get-item` reflects the mutated attributes.
- Reads are strongly consistent: a write's effect is visible to the very next read of the same key.

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

