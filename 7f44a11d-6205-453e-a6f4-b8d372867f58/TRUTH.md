# TRUTH: 7f44a11d-6205-453e-a6f4-b8d372867f58

## Problem

Implement a single executable named `aws` on `$PATH` that emulates the subset of the real `aws sqs` CLI needed for these eight subcommands: `create-queue`, `delete-message`, `delete-queue`, `get-queue-attributes`, `get-queue-url`, `list-queues`, `receive-message`, `send-message`. The program is invoked as `aws sqs <command> [flags...]`, must talk to a real SQS-compatible backend already reachable via environment-provided endpoint/credentials (e.g. ElasticMQ or similar, exposed through `AWS_ENDPOINT_URL`/`AWS_ENDPOINT_URL_SQS` and standard AWS credential env vars), and must preserve state consistency across a sequence of invocations (each invocation is a fresh process — state lives in the backend service, not in the CLI process).

## Behavioral contract

- Entry point: an executable file `aws` on `$PATH` (any language), dispatching on `argv[1] == "sqs"` and `argv[2]` as the subcommand.
- Success: JSON response document to stdout only (must be `json.loads`-parseable), nothing on stderr, exit code `0`.
- Failure: nothing on stdout, a single human-readable line on stderr identifying the failure class (service error envelope, bare `<ErrorCode>: <message>`, or a client usage-error line with a recognizable prefix), exit code non-zero and in `{1,252,254,255}` (client picks the code; tests only check `!= 0`).
- No raw tracebacks ever, on any path.
- No client-side semantic validation of *values* (e.g. don't invent your own "message body too long" check) — malformed input should be forwarded to the service and its rejection surfaced; but missing/unknown/extra CLI arguments must be rejected by the CLI itself before any network call.
- Must not shell out to `awscli`/real `aws` binary, must not import awscli, must not override region/endpoint/credentials in code (must read them from environment as already configured).
- Only flags that exist upstream may be accepted; each command only accepts the flags enumerated in the task for that command.
- Cross-command state consistency: created queues appear in `list-queues` and resolve via `get-queue-url`; sent messages are retrievable byte-identical via `receive-message`; receipt handles from `receive-message` work with `delete-message`; deleted queues disappear from `list-queues` and yield a non-existent-queue error on subsequent operations; FIFO queue rules (name suffix `.fifo`, `FifoQueue` attribute, `MessageGroupId` required on send) are enforced by the backing service, not necessarily by the client.

## Solution decomposition

1. **Argument parsing per subcommand** — a table/dispatch of allowed `--flag` names per subcommand, each mapped to the correct API parameter name and type (string, int, JSON map, list). Reject: unknown flags, missing required flags, missing values, duplicate flags, extra positional args → usage error, exit 252 (or any non-zero in the allowed set) on stderr, nothing on stdout.
2. **Type coercion for known "typed" parameters** — e.g. `--max-number-of-messages`, `--visibility-timeout`, `--wait-time-seconds`, `--delay-seconds`, `--max-results` as integers; `--attributes`, `--message-attributes`, `--message-system-attributes`, `--tags` as JSON objects; `--attribute-names`, `--message-attribute-names`, `--message-system-attribute-names` as lists. Failing to parse a value that's supposed to be JSON should be a usage error, not a crash.
3. **Transport to backend** — build and send the appropriate SQS API request (JSON protocol `X-Amz-Target: AmazonSQS.<Op>` over HTTP to the endpoint from env, or equivalent via a bundled SDK such as boto3/AWS SDK if available in the image) using credentials/region from env unmodified. Map CLI subcommand → underlying SQS operation name (CreateQueue, ListQueues, GetQueueUrl, GetQueueAttributes, SendMessage, ReceiveMessage, DeleteMessage, DeleteQueue).
4. **Response shaping** — translate the service's response into the CLI's JSON stdout document. Field naming should match what boto3/`aws sqs` clients would return (e.g. `QueueUrl`, `QueueUrls`, `Attributes`, `Messages`, `MessageId`, `MD5OfMessageBody`, `ReceiptHandle`) since downstream tests inspect semantic JSON content (queue URL, message ids, receipt handles, attribute values as strings) — not a specific serialization library's key style, but must be internally consistent with the "Behavior" bullets (e.g. attribute values always strings even if numeric).
5. **Error translation** — catch HTTP/service errors and print one of the three acceptable stderr shapes, without leaking stack traces; catch network/transport-level exceptions too and turn them into a clean one-line message with a non-zero exit rather than an unhandled exception.
6. **Empty success bodies** — commands like `delete-message`/`delete-queue` return an empty object `{}` on success (not blank stdout — must still be valid JSON per "success output (JSON) goes to stdout"); parseable by `json.loads`.

## Solution space

Multiple implementation routes are valid and none should be penalized relative to others:

- **Any language**: Python (using `boto3`/`botocore` if present in the image, or raw HTTP via stdlib), Bash + `curl`/`jq`, Go, Node, etc. — as long as no extra packages are fetched and no `awscli`/real `aws` binary is invoked.
- **Transport implementation**: using an installed AWS SDK client (if available) vs. hand-rolled HTTP requests with SigV4 signing vs. even unsigned requests if the target backend doesn't enforce signature validation — any is acceptable as long as it doesn't hardcode/override the endpoint, region, or credentials supplied by the environment.
- **Argument parsing**: hand-rolled loop, `argparse`, a declarative flag-spec table, or a full argv grammar per command — as long as unknown/missing/malformed flags are rejected before any network call with a clear class-identifying message.
- **Attribute/tag/JSON-value flags** (`--attributes`, `--message-attributes`, `--tags`, etc.) may be parsed as JSON text or as AWS CLI's `key=value,key=value` shorthand syntax — either is acceptable as long as it round-trips correctly to the underlying API's expected shape.
- **Error code choice**: any of 1/252/254/255 for a given failure is fine; tests only assert non-zero.
- **Response document shape**: exact key capitalization/nesting should mirror standard `aws sqs` JSON output structure, but pretty vs. compact JSON, key ordering, and extra harmless metadata fields (e.g. `ResponseMetadata`) are not tested and may be included or omitted.

## Known pitfalls

- Mixing stdout and stderr: writing partial success JSON before an error occurs, or writing error text to stdout. Must be strictly one-or-the-other.
- Printing Python (or other runtime) tracebacks on unexpected exceptions (e.g. connection refused, JSON decode error) — must be caught and converted to a one-line message.
- Not validating CLI-level argument shape (missing required flag, unknown flag) before making a network call — sending garbage to the service and hoping it 400s is not sufficient if the flag itself is nonsensical/unrecognized; the task explicitly wants usage errors surfaced client-side for structural issues (missing/unknown/malformed argv), while leaving semantic/business validation to the service.
- Client-side "helpfully" validating values (e.g. checking message body length, queue name pattern) — the spec explicitly forbids inventing client-side semantic validation; that must come from the service.
- Coercing numeric attribute values to JSON numbers in `get-queue-attributes` output — SQS attributes are always strings; must not "improve" typing.
- FIFO validation implemented incorrectly or duplicated client-side in a way that conflicts with what the service actually enforces — safest is to pass through and let the service reject with its real error class.
- Losing receipt handles' fidelity by re-encoding/truncating them — must pass through opaque handles unchanged between receive and delete/visibility calls.
- Hardcoding the SQS endpoint/region/credentials in code instead of reading them from the environment, which breaks the test harness's ability to point at its own backend.
- Fabricating flags not in the allowed list per command (e.g. adding `--region` handling in argv, or accepting flags for a different command).
- Not returning valid JSON (e.g. empty stdout) on successful `delete-message`/`delete-queue`, when the contract requires JSON-parseable stdout on the success path.
- Exit code outside `{0,1,252,254,255}`.

## Cheat surface

- Faking success output without contacting a real backend (hardcoding a queue URL, fabricating `MessageId`/`ReceiptHandle` locally, keeping an in-process fake store) would fail because state must be observably consistent through the *actual* configured service across independent process invocations — this is the main way a low-effort "solution" would visibly break under end-to-end sequences (create → send → receive → delete → verify gone).
- Ignoring `--wait-time-seconds`/`--visibility-timeout` semantics and just always returning canned data likely fails redelivery/invisibility timing checks.
- Swallowing all errors and always exiting 0 would fail the negative-path tests that check `returncode != 0` and stderr content on invalid input or service-level errors (e.g. non-existent queue, invalid receipt handle).
- Blindly forwarding every flag/value without minimal argv validation could let genuinely malformed invocations (unknown flags, missing required args) silently succeed or crash with a traceback rather than a clean usage error.
- Shelling out to the real `aws` CLI or `awscli` library is explicitly disallowed even though it would trivially satisfy behavior — a compliant submission must not depend on/import awscli or invoke an `aws` binary from itself.

## Success criteria

- All 132 shipped tests pass: for each command, valid-argument invocations produce parseable JSON on stdout, empty stderr, exit 0, and correct semantic content (queue URLs resolve, messages round-trip by body, receipt handles are honored, attributes reflect state, list-queues reflects create/delete history); invalid-argument invocations (missing/unknown/malformed flags) produce empty stdout, a class-identifying stderr line, and a non-zero exit code in `{1,252,254,255}`.
- Cross-command sequences (create→list/get-url, send→receive→delete, create→delete→operate-on-stale-url) behave with consistent, service-backed state — not merely per-command in isolation.
- No stdout/stderr mixing, no stack traces, under any success or failure scenario across all eight commands.