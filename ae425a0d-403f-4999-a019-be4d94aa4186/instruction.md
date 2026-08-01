# Build an `aws kinesis` CLI

## Application overview

You will implement the following `aws kinesis` commands:
`kinesis add-tags-to-stream`, `kinesis create-stream`, `kinesis decrease-stream-retention-period`, `kinesis delete-stream`, `kinesis describe-stream`, `kinesis describe-stream-summary`, `kinesis get-records`, `kinesis get-shard-iterator`, `kinesis increase-stream-retention-period`, `kinesis list-shards`, `kinesis list-streams`, `kinesis put-record`, `kinesis put-records`, `kinesis remove-tags-from-stream`.

Your code is invoked as a subprocess:

```bash
aws kinesis <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence of
kinesis operations behaves correctly end-to-end.

## Commands

### `kinesis add-tags-to-stream`
- `kinesis add-tags-to-stream --tags <json>`
Flags: `--stream-arn`, `--stream-id`, `--stream-name`, `--tags`
After a successful add, the tags are visible via `list-tags-for-stream`.
Tagging a missing stream fails with a resource-not-found error class.

### `kinesis create-stream`
- `kinesis create-stream --stream-name <string>`
- `kinesis create-stream --stream-name <value> --shard-count 1`
Flags: `--max-record-size-in-ki-b`, `--shard-count`, `--stream-mode-details`, `--stream-name`, `--tags`, `--warm-throughput-mi-bps`
After a successful create the stream appears in `list-streams` and `describe-stream` reports it under the requested name.
Creating a stream whose name already exists fails with a resource-in-use error class.

### `kinesis decrease-stream-retention-period`
- `kinesis decrease-stream-retention-period --retention-period-hours <number>`
Flags: `--retention-period-hours`, `--stream-arn`, `--stream-id`, `--stream-name`
Lowers the stream's retention period (valid range 24..168 hours; new value must be below the current one); the change is visible via `describe-stream-summary`.

### `kinesis delete-stream`
- `kinesis delete-stream`
Flags: `--enforce-consumer-deletion`, `--stream-arn`, `--stream-id`, `--stream-name`
Deleting an existing stream succeeds; deletion is asynchronous, so the stream may remain visible briefly before it disappears from listings.
Deleting a missing stream fails with a resource-not-found error class.

### `kinesis describe-stream`
- `kinesis describe-stream`
- `kinesis describe-stream --limit 0`
- `kinesis describe-stream --limit 1`
- `kinesis describe-stream --limit 10001`
- `kinesis describe-stream --limit 10000`
Flags: `--exclusive-start-shard-id`, `--limit`, `--stream-arn`, `--stream-id`, `--stream-name`
Reports the stream's description: name, ARN, status, and (once the stream is active) its shards.
Describing a missing stream fails with a resource-not-found error class.

### `kinesis describe-stream-summary`
- `kinesis describe-stream-summary`
Flags: `--stream-arn`, `--stream-id`, `--stream-name`
Reports the summary view of the stream, including its retention period in hours; retention changes made by other commands are visible here.
A missing stream fails with a resource-not-found error class.

### `kinesis get-records`
- `kinesis get-records --shard-iterator <string>`
- `kinesis get-records --shard-iterator <value> --limit 1`
Flags: `--limit`, `--shard-iterator`, `--stream-arn`, `--stream-id`
Reads records from a shard iterator; records put on that shard come back with byte-identical payloads and partition keys.

### `kinesis get-shard-iterator`
- `kinesis get-shard-iterator --shard-id <string> --shard-iterator-type <string>`
- `kinesis get-shard-iterator --shard-id <value> --shard-iterator-type AT_SEQUENCE_NUMBER`
- `kinesis get-shard-iterator --shard-id <value> --shard-iterator-type AFTER_SEQUENCE_NUMBER`
- `kinesis get-shard-iterator --shard-id <value> --shard-iterator-type TRIM_HORIZON`
- `kinesis get-shard-iterator --shard-id <value> --shard-iterator-type LATEST`
Flags: `--shard-id`, `--shard-iterator-type`, `--starting-sequence-number`, `--stream-arn`, `--stream-id`, `--stream-name`, `--timestamp`
Returns an opaque iterator token for a shard of an active stream; the token's value is not stable across runs and carries no meaning itself.

### `kinesis increase-stream-retention-period`
- `kinesis increase-stream-retention-period --retention-period-hours <number>`
Flags: `--retention-period-hours`, `--stream-arn`, `--stream-id`, `--stream-name`
Raises the stream's retention period (valid range 24..168 hours; new value must exceed the current one); the change is visible via `describe-stream-summary`.

### `kinesis list-shards`
- `kinesis list-shards`
Flags: `--exclusive-start-shard-id`, `--max-results`, `--next-token`, `--shard-filter`, `--stream-arn`, `--stream-creation-timestamp`, `--stream-id`, `--stream-name`
An active stream exposes one entry per shard with hash-key and sequence-number ranges.
Listing shards of a missing stream fails with a resource-not-found error class.

### `kinesis list-streams`
- `kinesis list-streams --limit 0`
- `kinesis list-streams --limit 1`
- `kinesis list-streams`
- `kinesis list-streams --limit 10001`
- `kinesis list-streams --limit 10000`
Flags: `--exclusive-start-stream-name`, `--limit`, `--next-token`
Reflects exactly the cumulative effect of prior creates and deletes.

### `kinesis put-record`
- `kinesis put-record --data <blob> --partition-key <string>`
Flags: `--data`, `--explicit-hash-key`, `--partition-key`, `--sequence-number-for-ordering`, `--stream-arn`, `--stream-id`, `--stream-name`
Puts a data record (base64 payload + partition key) onto an existing stream and acknowledges it with a shard id and sequence number.
A record put here is retrievable via the shard read path with the same payload and partition key (round-trip identity).

### `kinesis put-records`
- `kinesis put-records --records <json>`
Flags: `--records`, `--stream-arn`, `--stream-id`, `--stream-name`
Batch variant of `put-record`: every entry is acknowledged (zero failed records) and the response carries one entry per input record, in order.

### `kinesis remove-tags-from-stream`
- `kinesis remove-tags-from-stream --tag-keys <json>`
Flags: `--stream-arn`, `--stream-id`, `--stream-name`, `--tag-keys`
After a successful remove, the removed keys no longer appear in `list-tags-for-stream`.

## Cross-command behavior

State must remain consistent across the command set:

- After `create-stream`, the stream is visible to `list-streams`, `describe-stream`, and `describe-stream-summary`.
- A `put-record`/`put-records` payload is retrievable through `get-shard-iterator` + `get-records` with byte-identical data and partition key.
- Tags added by `add-tags-to-stream` appear in `list-tags-for-stream` and disappear after `remove-tags-from-stream`.
- Retention changed by `increase-stream-retention-period` / `decrease-stream-retention-period` is reflected by `describe-stream-summary`.
- After `delete-stream` completes, operations on that stream name fail with a resource-not-found error class.

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
them from the underlying kinesis service semantics and standard
`aws kinesis` conventions.

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
