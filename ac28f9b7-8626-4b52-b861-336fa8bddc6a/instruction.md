# Build an `aws dynamodb` CLI

## Application overview

You will implement the following `aws dynamodb` commands:
`dynamodb describe-limits`, `dynamodb list-tables`, `dynamodb put-item`, `dynamodb update-item`.

Your code is invoked as a subprocess:

```bash
aws dynamodb <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence such as
create-table, put-item, get-item, query behaves correctly end-to-end.

## Commands

### Command: `dynamodb describe-limits`

Observed argv patterns:

- `dynamodb describe-limits`

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

- After `put-item`, `get-item` on the same key returns the written item.
- After `update-item`, `get-item` reflects the mutated attributes.

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

