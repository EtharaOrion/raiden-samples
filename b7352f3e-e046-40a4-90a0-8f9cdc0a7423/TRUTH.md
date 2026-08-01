# TRUTH: b7352f3e-e046-40a4-90a0-8f9cdc0a7423

## Problem

Implement a single executable `aws` on `$PATH` that, when invoked as `aws sqs <command> [args...]`, behaves like the real `aws sqs` CLI against a locally-configured SQS-compatible endpoint (credentials/endpoint provided via environment — never hard-coded or overridden in code). The program must dispatch across 17 subcommands, maintain consistent state across calls (queues, messages, attributes, tags persist and interact correctly), emit well-formed JSON on stdout for success, emit a classifiable error line on stderr for failure, never leak a raw traceback, and exit with a code from `{0,1,252,254,255}` matching the failure category.

## Behavioral contract

- Invocation shape: `aws sqs <subcommand> --flag value ...`. Only the documented subcommands/flags exist; unlisted flags must be rejected as usage errors, not silently accepted or invented.
- No client-side semantic validation of input content (e.g. don't reject a queue name for "looks wrong"); let the backing service enforce this and surface the resulting service error. Basic CLI-shape parsing (missing required flag, malformed option syntax) is legitimately checked before dispatch.
- stdout carries only the JSON response body on success and is empty on failure; stderr carries only the error line on failure and is empty on success — the two streams must never mix.
- Error line must name a failure class: either the full AWS-style envelope, a bare `<ErrorCode>: <message>`, or a client usage-error line with a recognizable prefix (`usage:`, `Parameter validation failed:`, `Unknown options:`, etc.).
- Exit codes: 0 success; 252 usage/parameter error; 254 modeled service exception (e.g. QueueDoesNotExist, ReceiptHandleIsInvalid, QueueNameExists); 1 or 255 for other/general failures. Tests generally only assert `!= 0` for failure cases, but must land in this set.
- State continuity across process invocations is mandatory: since each command is a fresh subprocess, all queue/message/attribute/tag state must live in the external SQS-compatible service reachable via the environment-provided endpoint — not in any local file cache that could desync from the real service state model (e.g., visibility timeouts, redelivery, purge). Using the endpoint as source of truth is the natural way to satisfy this; anything that reproduces the same observable semantics is acceptable.
- Specific cross-command guarantees to verify:
  - `create-queue` → queue immediately visible in `list-queues` and via `get-queue-url`.
  - `send-message`/`send-message-batch` body → byte-identical on `receive-message`; returned receipt handle is valid for `delete-message`/`change-message-visibility` while live.
  - `delete-message` with a stale/reused/malformed handle → ReceiptHandleIsInvalid-class error, not silently ignored or accepted.
  - `purge-queue` → approximate message count converges to 0 (eventual consistency tolerated).
  - `set-queue-attributes` changes and `tag-queue`/`untag-queue` changes → visible via `get-queue-attributes`/`list-queue-tags` respectively; read-only attributes (Arn, approximate counts, timestamps) must not be settable.
  - `delete-queue` → subsequent operations against that URL fail with a non-existent-queue class error.
  - FIFO: queue name must end `.fifo` and set `FifoQueue` attribute; `send-message` to a FIFO queue without `MessageGroupId` must fail (service-side).
  - Recreating an existing queue name with different attributes → QueueNameExists-class error.
- `get-queue-attributes` numeric values must be returned as strings (this is native SQS wire behavior, so it falls out automatically if the raw service response is passed through un-mangled).

## Solution decomposition

1. **Argument parsing / dispatch**: parse `argv[1]=="sqs"`, `argv[2]` = subcommand name, map to a table of allowed flags per subcommand. Reject unknown flags/subcommands and missing required flags with exit 252.
2. **Flag value parsing**: convert CLI string values to the shapes the backend expects — plain strings, integers, JSON blobs (`--entries`, `--attributes` for some commands may accept either JSON or `key=value` shorthand per aws-cli conventions), lists (comma-separated or JSON array) for things like `--tag-keys`, `--attribute-names`.
3. **Transport to backend**: Every subcommand ultimately needs to reach the real SQS-protocol backend configured via environment (endpoint URL, region, credentials already set in env — must not be overridden). This can be done via raw HTTP (JSON protocol / X-Amz-Target headers) or via an SDK client (boto3, or a Node/Go/Java SQS SDK) already present in the image, letting the SDK/library pick up endpoint+creds from environment automatically.
4. **Response shaping**: On success, emit the operation's response as JSON to stdout. Empty-body operations (delete-queue, purge-queue, tag/untag-queue, delete-message, change-message-visibility, set-queue-attributes) should still emit *some* valid JSON-parseable output per the general contract description ("stdout writes the JSON response document") — an empty object `{}` is acceptable since the spec only requires stdout be parseable JSON and empty on failure, not necessarily non-empty on success for these ops. (Reference implementation just exits with no stdout at all for these — this is a defensible reading since "empty" success responses arguably satisfy "stdout empty on failure only," but graders comparing JSON content on these ops would just check no failure occurred / exit 0.)
5. **Error handling**: catch service-level errors (HTTP 4xx from the SQS endpoint) and translate them into one of the three acceptable stderr shapes, using the modeled error code returned by the service (QueueDoesNotExist, ReceiptHandleIsInvalid, QueueNameExists, MessageNotInflight, etc.), exit 254. Catch connectivity/unexpected errors, print a brief message (no traceback), exit 255 (or 1). Usage errors caught earlier exit 252.
6. **Special-case defaults**: `get-queue-attributes` with no `--attribute-names` should still return the full/expected attribute set (many implementations default to requesting `All`).

## Solution space

Multiple implementation strategies are equally valid:

- **Any language**: Python, Node, Go, Java, Ruby, shell+curl — whatever the image provides.
- **Transport**: raw HTTP requests against the SQS JSON protocol (manually building `X-Amz-Target`/JSON body, as in the reference) OR using a preinstalled AWS SDK (boto3 `client('sqs')`, AWS SDK for JS/Go/Java) that reads endpoint/region/credentials purely from environment variables/config — both are correct as long as no hardcoded endpoint/region/credential override occurs in code.
- **Auth headers**: if hand-rolling HTTP, a dummy/placeholder SigV4-shaped Authorization header is acceptable if the target test backend doesn't enforce real signature verification; using a real SDK sidesteps this entirely by letting the SDK sign requests properly. Both are valid; a solution is not required to implement real SigV4 signing if the harness's backend doesn't check it, but a solution that *does* implement full correct SigV4 is equally valid and arguably more robust/general.
- **Attribute/tag shorthand parsing**: accepting only strict JSON for `--attributes`/`--tags`/`--entries` is valid too, since the task doesn't strictly mandate shorthand support — as long as the documented `--flag <json>` usage from the instructions works. Supporting both JSON and `key=value` shorthand is a superset, also fine.
- **Response emission for empty-body ops**: emitting `{}` or omitting stdout output entirely (exit 0, empty stdout) are both defensible given the ambiguity in the spec; emitting the actual (empty) response object `{}` is the safer choice since the spec says "writes the operation's JSON response document to stdout" — pure omission risks failing a stray test that does `json.loads(stdout)` and expects at least valid JSON. A fully correct solution should lean toward always printing *something* JSON-parseable on stdout for every successful op, including empty-body ones.
- **State storage**: the state must live wherever the graded harness's SQS-compatible service (moto/localstack-like) persists it; a solution must not maintain a private duplicate store since that would desync from what the test's separate verification queries observe. Any transport method that talks to that shared backend is correct.

## Known pitfalls

- Mixing stdout/stderr: printing any diagnostic (even a warning) to stdout on success, or printing partial JSON to stdout before an error, breaks the "stdout empty on failure" / "stderr empty on success" contract.
- Letting an SDK exception's raw traceback leak to stderr instead of a formatted one-line message — must be caught and reformatted.
- Client-side over-validation: rejecting values (e.g. queue names, attribute values) based on guessed format rules instead of letting the service decide — spec explicitly forbids this ("Do not validate input client-side").
- Under-validation of CLI *syntax* — e.g. accepting a completely unknown `--foo` flag silently instead of exiting 252, or accepting a genuinely missing required flag and passing an empty/None value straight to the backend, causing a confusing service-level failure instead of a clean usage error.
- Forgetting that repeated flags in aws-cli conventions overwrite (last wins) — not fatal to get wrong, but inconsistent handling could cause a mismatched-code failure.
- Hardcoding an endpoint/region/credentials in code instead of relying on environment — explicitly disallowed and will break under the test harness's env-injected endpoint.
- Treating numeric queue attributes as JSON numbers instead of passing through the service's native string representation.
- Not defaulting `AttributeNames` on `get-queue-attributes` when omitted, causing attributes tests to see missing data (though this depends on what the graders expect back — omitting is risky since the instruction implies attributes are visible by default).
- FIFO validation: assuming the CLI (not the service) should validate `.fifo` suffix / `MessageGroupId` presence — should be left to the service, but the CLI must correctly relay these fields through so the service can reject them.
- Swallowing HTTP error bodies without extracting the error code, producing an error line that doesn't name a failure class matching the required shapes.
- Exit code selection: using an out-of-set code (e.g., 2) for usage errors, or returning 0 alongside an error message.

## Cheat surface

- A stub that hardcodes fixed JSON output ignoring actual queue/message state would fail cross-command consistency checks (list-queues after create, receive after send, deletion of message body-matching, etc.) — not viable given end-to-end sequence testing.
- A local-only fake datastore (not backed by the real configured SQS endpoint) risks diverging from whatever the test harness independently queries/expects (e.g., real endpoint's timeout/visibility semantics, ARNs, message MD5) — likely fails unless it precisely reimplements all needed semantics, which is effectively as much work as calling through.
- Blanket `try/except: exit(1)` catching everything into an application error may pass some failure tests (`returncode != 0`) but risks emitting stdout+stderr both or missing the required class-naming line — could fail on stderr content checks distinguishing usage vs. service vs. app errors, and could fail exit-code-class expectations if graders check e.g. "usage error expects one of {252}" specifically (spec says only `!=0` is checked broadly, but per-scenario tests may target specific classes via message content).
- Ignoring the "no fabricated flags" rule to add convenience flags not in the upstream API is a low-value cheat that doesn't help pass tests and risks unknown-flag mismatches.

## Success criteria

- For each of the 17 subcommands, valid invocations produce exit 0 with stdout containing valid JSON reflecting real, queryable state (queue URLs resolvable, messages round-trip, attributes/tags mutate and are visible, deletions take effect).
- Invalid/missing/unknown flags produce exit 252 with no stdout and a usage-classed stderr line.
- Service-rejected operations (bad receipt handle, non-existent queue, duplicate queue name with different attrs, FIFO violations) produce a non-zero exit (254 typical) with no stdout and a stderr line naming the specific service error code/class.
- No scenario produces both non-empty stdout and non-empty stderr, and no scenario prints a raw stack trace.
- Full end-to-end sequences (create → send → receive → delete → purge → tag → untag → delete-queue) behave consistently as if driven against one real, stateful SQS-like backend, without cross-invocation state loss.