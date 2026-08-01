# TRUTH: ae425a0d-403f-4999-a019-be4d94aa4186

## Problem

Implement a single executable `aws` on `$PATH` that intercepts `aws kinesis <command> ...` invocations and behaves like the real `aws kinesis` CLI against a locally-reachable Kinesis-compatible service (endpoint/credentials pre-supplied via environment). The program must dispatch across 14 subcommands, translate CLI flags into the correct Kinesis JSON-protocol API calls, forward requests to the configured endpoint, and render responses/errors in the documented shapes. State (streams, shards, records, tags, retention) must be consistent across a sequence of subcommand invocations because the tests exercise cross-command workflows (create → put → read → tag → delete, etc.).

## Behavioral contract

- Invocation: `aws kinesis <subcommand> [--flag value ...]`. Only the 14 listed subcommands need to work; each has a fixed set of accepted flags (enumerated in the instruction) — no other flags may be silently invented or accepted as if real.
- stdout carries only a JSON document (parseable by `json.loads`) on success, and is empty otherwise.
- stderr carries only a single human-readable error line on failure (naming the error class per one of the three accepted shapes), and is empty on success.
- No Python/other-language tracebacks ever reach stderr/stdout.
- Exit code ∈ {0,1,252,254,255}, with 0 for success, 252 for usage/parameter errors, 254 for modeled service errors, 1/255 acceptable for other failures.
- Client code must NOT do semantic/business validation itself (e.g. must not client-side reject a bad shard-iterator-type) — such rejections must come from the backing service, except for pure CLI-parsing concerns (unknown flag, missing value, non-integer where int expected, missing required flag entirely) which are legitimately usage errors (252).
- Must not call the real `aws` CLI or import awscli; must not override endpoint/region/credentials configuration that's already present in env.
- State consistency requirements (see Cross-command behavior in the instruction) must hold: created streams appear in list/describe; put records round-trip through shard-iterator/get-records with byte-identical data+partition key; tags add/remove visible via list-tags-for-stream; retention changes visible via describe-stream-summary; deleted streams eventually 404 out.

## Solution decomposition

1. **Argument parsing / dispatch layer**: read `argv[1]` (`kinesis`) and `argv[2]` (subcommand), route to a per-command handler. Parse `--flag value` pairs generically, with special handling for multi-token values (e.g. `--tags` shorthand, `--records`/`--tag-keys` as JSON blobs), `file://` value dereferencing, and int-typed flags.
2. **Flag → API parameter mapping**: each subcommand maps its documented CLI flags to the corresponding Kinesis API JSON field names (StreamName/StreamARN, ShardCount, RetentionPeriodHours, Tags, Records, ShardIterator, Limit, etc.), matching upstream `aws kinesis` semantics.
3. **Backend transport**: build and send a request to the Kinesis-protocol endpoint (JSON RPC over HTTP with `X-Amz-Target: Kinesis_20131202.<Operation>`), using whatever credentials/endpoint are already in the environment (do not hardcode a different region/endpoint that overrides env-provided ones — reading env vars for endpoint discovery as a fallback is fine, but must not stomp on real AWS_* env config when present). This can be done via raw HTTP (urllib) with a real or dummy SigV4 signature if the target endpoint doesn't enforce signature validation, or via boto3/botocore already present in the image (if available) pointed at the environment's configured endpoint.
4. **Response shaping**: on success, print exactly one JSON document to stdout; on HTTP error, extract the service error code/message and print one line to stderr in one of the three accepted shapes, returning exit code 254 (or 1) for service errors and 252 for local parse errors caught before any network call.
5. **State semantics**: rely on the backend service itself for consistency (created stream visible in list/describe, shards populated once active, put/get round-trip, tag add/remove, retention change, delete then 404) — this is the backend's job as long as requests are correctly translated and consistently addressed (same StreamName/StreamARN/StreamId resolution logic across commands).
6. Handle stream identification consistently: many commands accept any of `--stream-name`, `--stream-arn`, `--stream-id` (where applicable per the flag lists) and must forward whichever was given, without requiring all three.

## Solution space

Valid alternative approaches include:
- Using **boto3/botocore** (if present in the image) configured to read `AWS_ENDPOINT_URL`/`AWS_ENDPOINT_URL_KINESIS` and other AWS_* environment variables normally (i.e., letting botocore's default credential/endpoint resolution work, not hardcoding overrides) instead of hand-rolling HTTP+SigV4.
- Using raw `urllib`/`http.client` requests with a dummy/placeholder Authorization header, relying on the local test backend not enforcing real SigV4 validation — acceptable since credentials are dummy/local.
- Implementing the CLI in any language available in the image (Go, Node, Java, etc.) rather than Python, as long as the executable is named `aws` and is on `$PATH`.
- Different internal state-machine simulation vs. delegating fully to a real backend service — since the instructions imply an actual Kinesis-compatible service is reachable via env-configured endpoint, delegating entirely to it (rather than reimplementing Kinesis semantics in-process) is the expected/simplest approach, but an in-memory reimplementation of Kinesis stream/shard/record semantics would also satisfy the contract as long as all cross-command consistency holds within a single process invocation — note however that each CLI invocation is a *separate* process, so any in-memory approach must persist state to disk between invocations (e.g., a JSON/sqlite state file) to satisfy cross-command consistency. This is harder and riskier than delegating to a real backend and is not the recommended route, but is not ruled out.
- Various acceptable error-line formats (envelope, bare code, or usage-prefixed) — a solution should not be penalized for choosing one shape over another, as long as it's one of the three.
- Different flag-parsing strategies (manual loop vs. use of a full argparse-like framework) as long as unknown flags/missing values map to 252.

## Known pitfalls

- **Mixing stdout/stderr**: printing debug info, warnings, or partial JSON to stdout on failure, or leaking error text to stdout, breaks the "stdout empty on failure" / "stderr empty on success" contract.
- **Tracebacks leaking**: any unhandled exception (e.g., JSON decode error, KeyError, network exception) must be caught and converted to a one-line error, not allowed to print a Python stack trace.
- **Client-side over-validation**: rejecting an otherwise well-formed request (e.g., checking shard-iterator-type against an allow-list, checking retention bounds) at the client instead of letting the service return the modeled error — the instruction explicitly says not to validate input client-side beyond basic parsing; over-validating risks producing 252 in cases tests expect 254, or vice versa. (The reference implementation itself has some pre-checks like limit ranges — these are edge risks; a strictly compliant solution defers such semantic checks to the backend where feasible.)
- **Wrong exit code choice**: e.g., using exit code 2 (argparse default) instead of one of {0,1,252,254,255}, or not distinguishing usage errors (252) from service errors (254) at all.
- **Not supporting all three stream-identifier flags** (`--stream-name`/`--stream-arn`/`--stream-id`) where documented — forwarding only stream-name and ignoring stream-arn/stream-id would break tests that use those forms.
- **Multi-value / JSON-blob flags**: `--tags`, `--tag-keys`, `--records` can be given as JSON strings or (for tags) shorthand `key=value,...`, or via `file://` — mishandling these breaks add/remove-tags and put-records.
- **Base64 handling for `--data`**: the AWS CLI base64-decodes `--data` client-side before sending, or accepts raw bytes/`fileb://` — get this wrong and round-trip byte-identity tests fail.
- **Retention validity bounds enforcement**: hardcoding 24–168 checks client-side changes which layer produces the error; letting the service enforce it is safer/more spec-compliant, but the instruction does document the valid range as informational context, not necessarily mandating client-side enforcement.
- **Async delete semantics**: tests tolerate the stream still appearing briefly after delete-stream; a solution that assumes synchronous deletion and asserts immediate absence would be a test-writer pitfall, not a submission pitfall, but a submission that artificially blocks until deletion completes isn't wrong either as long as it doesn't break other invariants.
- **Environment/credential override**: explicitly overriding `AWS_ENDPOINT_URL`, region, or credentials in code instead of relying on env is disallowed and could break the test harness's ability to point the CLI at its backend.
- **Forgetting `--limit` bounds validation is service-side**: tests exercise `--limit 0`, `--limit 10001` explicitly expecting failure — as long as *some* correct error class/exit code results (whether from client pre-check or from the service), this is fine; the risk is only in getting the exit-code/class wrong.

## Cheat surface

- Since tests only assert JSON *semantic* shape, exit code class, and error-class matching (not exact wording or exact byte-for-byte responses beyond described identity constraints), a submission could technically stub out most logic and directly proxy to a real Kinesis-compatible backend, deriving nearly all correctness "for free" from that backend rather than reimplementing service semantics — this is expected/intended, not a violation, since the task is a thin CLI wrapper.
- A submission might try to hardcode canned JSON responses without actually calling any backend and without persisting state across process invocations — this would fail cross-command consistency tests (e.g., create-then-list, put-then-get) since each invocation is a fresh process; graders should check that state genuinely propagates across independent `aws kinesis ...` process invocations, not just within one call.
- A submission might swallow all errors and always exit 0 with fabricated success JSON to dodge failure-path tests — graders should verify genuine failure classes are surfaced for resource-not-found / resource-in-use / validation scenarios (missing stream operations, duplicate create-stream, out-of-range retention, etc.), not just success-path happy cases.
- Fabricating flags not in the documented set, or silently accepting/ignoring unsupported flags instead of erroring, would deviate from "do not fabricate flags" and "unknown flag → usage error" requirements.
- Returning exit code 0 alongside an error message on stderr (or vice versa) to game a naive "check stdout has JSON" test — the exit code and stream discipline must be jointly correct.

## Success criteria

- For every one of the 14 subcommands' documented invocation forms, running the CLI produces stdout-only JSON on success and stderr-only error-class line on failure, with exit code in the allowed set and the 0-vs-nonzero split matching intent.
- Cross-command workflows behave consistently within a test run: create→list/describe/summary see the new stream; put→(get-shard-iterator+get-records) round-trips payload/partition-key exactly; add-tags→list-tags-for-stream shows tags, remove-tags removes them; increase/decrease-retention reflected in describe-stream-summary; delete-stream eventually removes the stream and later operations 404.
- Operations against nonexistent streams (describe-stream, describe-stream-summary, list-shards, delete-stream, add-tags-to-stream, etc.) fail with a resource-not-found-class error and non-zero exit.
- create-stream against a duplicate name fails with a resource-in-use-class error.
- Malformed CLI usage (unknown flag, missing required value, non-numeric where int required) yields exit code 252 with a usage-prefixed error line and no stdout output.
- No stack traces appear under any tested scenario.
- Only the documented flags per subcommand are accepted; no undocumented flags are silently invented as functional.