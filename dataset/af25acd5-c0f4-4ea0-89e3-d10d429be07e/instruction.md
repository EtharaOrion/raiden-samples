# Build an `aws dynamodb` CLI

## Application overview

You will implement the following `aws dynamodb` commands:
`dynamodb create-table`, `dynamodb delete-item`, `dynamodb get-item`, `dynamodb list-tables`, `dynamodb put-item`, `dynamodb query`.

Your code is invoked as a subprocess:

```bash
aws dynamodb <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence such as
create-table, put-item, get-item, query behaves correctly end-to-end.

## Commands

### Command: `dynamodb create-table`

Observed argv patterns:

- `dynamodb create-table --table-name <string> --attribute-definitions <oversized-value:65-chars> --key-schema <oversized-value:60-chars> --billing-mode PAY_PER_REQUEST`
- `dynamodb create-table --table-name <string>`
- `dynamodb create-table --table-name <string> --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --billing-mode PROVISIONED --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5`
- `dynamodb create-table --table-name <string_v1>`
- `dynamodb create-table --table-name <string_v2>`
- `dynamodb create-table --table-name <string_v3>`
- `dynamodb create-table --table-name <string_v4>`
- `dynamodb create-table --table-name <string_v5>`
- `dynamodb create-table --table-name <string_v6>`
- `dynamodb create-table --table-name <string_v7>`

Documented flags: `--attribute-definitions`, `--billing-mode`, `--deletion-protection-enabled`, `--global-secondary-indexes`, `--global-table-settings-replication-mode`, `--global-table-source-arn`, `--key-schema`, `--local-secondary-indexes`, `--on-demand-throughput`, `--provisioned-throughput`, `--resource-policy`, `--sse-specification`, `--stream-specification`, `--table-class`, `--table-name`, `--tags`, `--warm-throughput`

Flags observed: `--attribute-definitions`, `--billing-mode`, `--deletion-protection-enabled`, `--global-secondary-indexes`, `--global-table-settings-replication-mode`, `--global-table-source-arn`, `--key-schema`, `--local-secondary-indexes`, `--on-demand-throughput`, `--provisioned-throughput`, `--resource-policy`, `--sse-specification`, `--stream-specification`, `--table-class`, `--table-name`, `--tags`, `--warm-throughput`

Behaviour & state expectations:

- After successful creation the table appears in `list-tables`.
- Re-creating an existing table name FAILS with `ResourceInUseException`.
- `--billing-mode PAY_PER_REQUEST` is used; do NOT rely on provisioned-throughput
  behaviour (it is ignored by the sandbox).
- `--key-schema` + `--attribute-definitions` must agree; a key attribute missing
  from the definitions FAILS with `ValidationException`.

Error cases:
- `dynamodb create-table` -> exit `252`
- `dynamodb create-table --table-name <string> --not-a-real-flag x` -> exit `252`
- `dynamodb create-table --table-name ` -> exit `252`
- `dynamodb create-table --table-name <string> --attribute-definitions {not valid json` -> exit `252`
- `dynamodb create-table --table-name <string> --table-name <string>` -> exit `252`
- `dynamodb create-table --table-name <oversized-value:512-chars>` -> exit `252`
- `dynamodb create-table --table-name <string>` -> exit `254`

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

### Command: `dynamodb put-item`

Observed argv patterns:

- `dynamodb put-item --table-name <string> --item <json>`
- `dynamodb put-item --table-name <string> --item <oversized-value:92-chars>`
- `dynamodb put-item --table-name <string> --item {"id":{"S":"k1"},"v":{"S":"first"}} --condition-expression attribute_not_exists(id)`
- `dynamodb put-item --table-name <string_v1> --item <json_v1>`
- `dynamodb put-item --table-name <string_v2> --item <json_v2>`
- `dynamodb put-item --table-name <string_v3> --item <json_v3>`
- `dynamodb put-item --table-name <string_v4> --item <json_v4>`
- `dynamodb put-item --table-name <string_v5> --item <json_v5>`
- `dynamodb put-item --table-name <string_v6> --item <json_v6>`
- `dynamodb put-item --table-name <string_v7> --item <json_v7>`

Documented flags: `--condition-expression`, `--conditional-operator`, `--expected`, `--expression-attribute-names`, `--expression-attribute-values`, `--item`, `--return-consumed-capacity`, `--return-item-collection-metrics`, `--return-values`, `--return-values-on-condition-check-failure`, `--table-name`

Flags observed: `--condition-expression`, `--conditional-operator`, `--expected`, `--expression-attribute-names`, `--expression-attribute-values`, `--item`, `--return-consumed-capacity`, `--return-item-collection-metrics`, `--return-values`, `--return-values-on-condition-check-failure`, `--table-name`

Behaviour & state expectations:

- Writes an item; afterward `get-item` on the same key returns it.
- `--condition-expression attribute_not_exists(pk)` on an existing key FAILS
  with `ConditionalCheckFailedException` and leaves the stored item unchanged.
- Numbers are JSON strings (`{"N": "5"}`).
- Writing to a missing table FAILS with `ResourceNotFoundException`.

Error cases:
- `dynamodb put-item --table-name <string> --item <json>` -> exit `254`
- `dynamodb put-item --item <json>` -> exit `252`
- `dynamodb put-item --table-name <string>` -> exit `252`
- `dynamodb put-item --table-name <string> --item <json> --not-a-real-flag x` -> exit `252`
- `dynamodb put-item --table-name  --item <json>` -> exit `252`
- `dynamodb put-item --table-name <string> --item <json> --attribute-definitions {not valid json` -> exit `252`
- `dynamodb put-item --table-name <string> --item <json> --table-name <string>` -> exit `252`
- `dynamodb put-item --table-name <oversized-value:512-chars> --item <json>` -> exit `252`

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

## Cross-command behavior

State must remain consistent across the command set:

- After `create-table`, the table appears in `list-tables`.
- After `delete-item`, `get-item` on the key returns no `Item`.
- `get-item` reflects exactly the cumulative effect of prior writes/updates.
- After `put-item`, `get-item` on the same key returns the written item.
- `query` returns exactly the items previously written under the partition key.
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

