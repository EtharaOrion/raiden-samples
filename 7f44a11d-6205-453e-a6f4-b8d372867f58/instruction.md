# Build an `aws sqs` CLI

## Application overview

You will implement the following `aws sqs` commands:
`sqs create-queue`, `sqs delete-message`, `sqs delete-queue`, `sqs get-queue-attributes`, `sqs get-queue-url`, `sqs list-queues`, `sqs receive-message`, `sqs send-message`.

Your code is invoked as a subprocess:

```bash
aws sqs <command> [args...]
```

Dispatch on the `<command>` token so one program handles every subcommand
above. State must remain consistent across commands so a sequence of
sqs operations behaves correctly end-to-end.

## Commands

### `sqs create-queue`

Argv shapes observed:

- `sqs create-queue --queue-name <string>`

Flags: `--attributes`, `--queue-name`, `--tags`

Behavior:

- After success the queue URL is returned, the queue appears in `list-queues`, and `get-queue-url` resolves its name.
- FIFO queues require a `.fifo` name suffix and the FifoQueue attribute; recreating an existing name with different attributes fails with a queue-name-exists error class.
- Missing, unknown, or malformed arguments: the command must fail with a
  non-zero exit code and a usage/validation error on stderr.

### `sqs delete-message`

Argv shapes observed:

- `sqs delete-message --queue-url <string> --receipt-handle <string>`

Flags: `--queue-url`, `--receipt-handle`

Behavior:

- Deletes a message by the receipt handle from the receive that delivered it; the message stops being redelivered.
- A stale or malformed receipt handle fails with a receipt-handle-is-invalid error class.
- Missing, unknown, or malformed arguments: the command must fail with a
  non-zero exit code and a usage/validation error on stderr.

### `sqs delete-queue`

Argv shapes observed:

- `sqs delete-queue --queue-url <string>`

Flags: `--queue-url`

Behavior:

- After success the queue disappears from `list-queues` and operating on its URL fails with a non-existent-queue error class.
- Missing, unknown, or malformed arguments: the command must fail with a
  non-zero exit code and a usage/validation error on stderr.

### `sqs get-queue-attributes`

Argv shapes observed:

- `sqs get-queue-attributes --queue-url <string>`

Flags: `--attribute-names`, `--queue-url`

Behavior:

- Reports the queue's attributes (every value is a string, even numeric ones); changes made by `set-queue-attributes` and message activity are visible here.
- Missing, unknown, or malformed arguments: the command must fail with a
  non-zero exit code and a usage/validation error on stderr.

### `sqs get-queue-url`

Argv shapes observed:

- `sqs get-queue-url --queue-name <string>`

Flags: `--queue-name`, `--queue-owner-aws-account-id`

Behavior:

- Resolves an existing queue name to its URL; a missing queue fails with a non-existent-queue error class.
- Missing, unknown, or malformed arguments: the command must fail with a
  non-zero exit code and a usage/validation error on stderr.

### `sqs list-queues`

Argv shapes observed:

- `sqs list-queues`
- `sqs list-queues --queue-name-prefix <value> --next-token <value> --max-results <value>`
- `sqs list-queues --next-token <value> --max-results <value>`

Flags: `--max-results`, `--next-token`, `--queue-name-prefix`

Behavior:

- Reflects exactly the cumulative effect of prior creates and deletes.

### `sqs receive-message`

Argv shapes observed:

- `sqs receive-message --queue-url <string>`

Flags: `--attribute-names`, `--max-number-of-messages`, `--message-attribute-names`, `--message-system-attribute-names`, `--queue-url`, `--receive-request-attempt-id`, `--visibility-timeout`, `--wait-time-seconds`

Behavior:

- Returns available messages with body, message id, and a receipt handle; the receipt handle is required to delete or re-time the message.
- A received message becomes temporarily invisible for the queue's visibility timeout.
- Missing, unknown, or malformed arguments: the command must fail with a
  non-zero exit code and a usage/validation error on stderr.

### `sqs send-message`

Argv shapes observed:

- `sqs send-message --queue-url <string> --message-body <string>`

Flags: `--delay-seconds`, `--message-attributes`, `--message-body`, `--message-deduplication-id`, `--message-group-id`, `--message-system-attributes`, `--queue-url`

Behavior:

- Enqueues a message body and acknowledges it with a message id and body MD5; the message is then retrievable via `receive-message` with an identical body.
- FIFO queues additionally require a message group id.
- Missing, unknown, or malformed arguments: the command must fail with a
  non-zero exit code and a usage/validation error on stderr.

## Cross-command behavior

State must remain consistent across the command set:

- After `create-queue`, the queue is visible to `list-queues` and resolvable via `get-queue-url`.
- A body sent by `send-message`/`send-message-batch` is returned byte-identical by `receive-message`, and its receipt handle drives `delete-message` and `change-message-visibility`.
- After `delete-message`, the message is not redelivered; after `purge-queue`, the approximate message count returns to zero.
- Attribute changes from `set-queue-attributes` and tag changes from `tag-queue`/`untag-queue` are visible via `get-queue-attributes` and `list-queue-tags`.
- After `delete-queue`, operations on the queue fail with a non-existent-queue error class.

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
them from the underlying sqs service semantics and standard
`aws sqs` conventions.

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

