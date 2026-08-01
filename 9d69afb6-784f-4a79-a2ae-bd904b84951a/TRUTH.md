# TRUTH: 9d69afb6-784f-4a79-a2ae-bd904b84951a

## Problem

Implement a single executable `aws` on `$PATH` that emulates the subset of the real `aws sqs` CLI needed to drive a full SQS queue/message lifecycle against a service endpoint already configured via environment variables (credentials, region, endpoint). The program must dispatch on `sqs <subcommand>`, translate CLI flags into the correct SQS API calls, and relay the service's JSON responses/errors faithfully to stdout/stderr with a constrained exit-code taxonomy. It must not shell out to the real `aws` binary or import `awscli`, must not hardcode/override endpoint or credentials, and must not perform client-side semantic validation that the service is supposed to perform.

## Behavioral contract

- Invocation: `aws sqs <command> [--flag value ...]`. Only the 17 listed subcommands are valid; each accepts only its documented flag set.
- Success: JSON response document on stdout only (parseable via `json.loads`), stderr empty, exit 0. Operations whose modeled response is essentially empty (e.g. `set-queue-attributes`, `delete-message`, `delete-queue`, `purge-queue`, `tag-queue`, `untag-queue`, `change-message-visibility`) may print `{}`/empty JSON or nothing meaningful — the important thing is stdout is valid JSON (or legitimately empty) and stderr is empty.
- Failure: stdout empty; stderr contains one line identifying the error class in one of three accepted shapes (AWS envelope, bare `<ErrorCode>: <message>`, or a client usage-error prefixed line). Never a Python/library traceback.
- Exit code must be one of `{0,1,252,254,255}`, chosen per category (usage error → 252 typically; service-modeled error → 254; other failures → 1 or 255). Tests only check nonzero on failure paths, so exact code within the failing set is flexible except 0 must mean success.
- Must not fabricate nonexistent flags; must not do client-side semantic validation (e.g., queue name format, FIFO suffix, numeric ranges) — that's the service's job. Basic CLI-parsing usage errors (unknown flag, missing required arg, malformed JSON syntax for a `--entries`/`--attributes` value) are legitimately client-side.
- End-to-end state consistency: create→list/get-url, send→receive (identical body)→delete/change-visibility, purge→zero count, set-attributes/tag/untag→reflected in get-attributes/list-tags, delete-queue→subsequent ops return non-existent-queue error. This consistency is provided by the backing SQS-compatible service itself as long as the CLI correctly relays calls with correct parameters and doesn't fork separate state per invocation (e.g., no local caching that diverges from the server).

## Solution decomposition

1. **Argument parsing / dispatch**: read `sys.argv`, require `sqs` as argv[1], subcommand as argv[2], map to an API operation name; parse remaining `--flag value` pairs into a params dict per-command flag schema.
2. **Type/shape translation of CLI values into API params**:
   - plain strings pass through
   - integers (`--visibility-timeout`, `--delay-seconds`, `--max-results`, etc.) parsed as ints but only for *syntactic* validity, not range checking
   - JSON-blob flags (`--entries`, `--attributes` on set-queue-attributes, `--tags` in some forms) parsed as JSON; malformed JSON syntax is a usage error
   - list flags (`--attribute-names`, `--tag-keys`, `--message-attribute-names`, etc.) accept AWS CLI list/JSON shorthand
   - tags accept AWS CLI map shorthand (`Key=Value,Key2=Value2`) and/or JSON object
3. **Transport**: build a signed (or endpoint-appropriate) HTTP request to the SQS-compatible endpoint taken from environment (`AWS_ENDPOINT_URL`/`AWS_ENDPOINT_URL_SQS`, region, credentials) — using whatever SDK/library is available in the image (boto3, or raw HTTP with SigV4). Must NOT override endpoint/region/credentials that are already set in env; must read them, not hardcode.
4. **Response relay**: on success, serialize the API response as JSON to stdout; on failure, extract the error code/message from the service exception/response and write one of the three accepted stderr shapes, then exit with an appropriate nonzero code from the allowed set, distinguishing usage errors (252) from service errors (254) from generic failures (1/255).
5. **No mixing of channels**: ensure nothing (log lines, warnings, HTTP client noise) leaks onto stdout on success, and nothing leaks onto stdout on failure.
6. **Statelessness of the CLI itself**: since state (queues, messages) is persisted by the backing service, the CLI need not maintain any of its own persistent store — each invocation is a fresh process making one API call. Consistency across commands is inherently satisfied by using the real backend faithfully rather than by any local bookkeeping.

## Solution space

Multiple implementation strategies are equally valid:

- **Using boto3** (if present in the image) to construct an `sqs` client from env-derived config with no explicit endpoint/region/credential overrides, calling the corresponding boto3 method per subcommand, catching `botocore.exceptions.ClientError` for service errors and translating to the required stderr format, and catching parameter/validation issues from boto3's own client-side param validation as usage errors.
- **Using boto3 with `client.exceptions`** to catch specific modeled exceptions (e.g., `QueueDoesNotExist`, `ReceiptHandleIsInvalid`) explicitly, or generically catching `ClientError` and reading `.response['Error']['Code']`.
- **Raw HTTP + SigV4 signing** (using only stdlib `urllib`/`hashlib`/`hmac` or an available `requests`/`botocore.auth` signer) posting `application/x-amz-json-1.0` requests to `AmazonSQS.<Operation>` targets, as in the reference diff — a lower-level but valid path.
- Any language available in the image (Go, Node, etc.) with an SQS-compatible SDK or manual HTTP+signing, as long as it doesn't shell out to `aws` or `awscli`.
- Flag-to-parameter mapping can be done via a declarative table (as in the reference) or ad-hoc argparse-style code — both fine as long as unknown flags are rejected and documented flags are supported per command.
- Any reasonable choice of nonzero exit code per failure category is acceptable as long as it's in `{1,252,254,255}` and 0 is reserved for success.

None of these are more "correct" than another; grading is behavioral (stdout/stderr shape, JSON content, exit code, end-to-end consistency), not implementation-specific.

## Known pitfalls

- **Overriding endpoint/region/credentials in code** (hardcoding a different endpoint or ignoring env vars) — forbidden and will break connectivity to the test harness's SQS-compatible backend.
- **Client-side semantic validation** (e.g., rejecting a FIFO name without `.fifo`, checking numeric ranges) instead of letting the service reject and relaying its error — spec explicitly says not to validate input client-side beyond basic parse-ability.
- **Mixing stdout/stderr**: printing partial JSON before an error, or writing library warnings/log lines to stdout.
- **Leaking tracebacks**: an uncaught exception (network error, KeyError, JSONDecodeError) must be caught and converted into a clean one-line stderr message, not a Python stack trace.
- **Wrong exit code for success** (must be exactly 0) or reusing 0 on failure.
- **Not distinguishing empty-response operations**: some ops (delete-message, purge-queue, set-queue-attributes, tag/untag-queue, change-message-visibility) have essentially empty responses; printing `null` or leaving stdout truly empty must still count as "valid JSON on stdout" — printing nothing at all could fail a `json.loads(stdout)` assertion depending on test harness expectations, so emitting `{}` is the safer choice than printing nothing.
- **Batch operations**: must build correct successful/failed entry lists reflecting the service's actual response, not synthesize success without checking the service payload.
- **List/tags shorthand parsing bugs**: e.g., failing to accept both JSON array and space/comma separated forms for `--attribute-names`/`--tag-keys`, or both JSON object and `Key=Value` shorthand for `--tags`.
- **Duplicate/missing flag handling**: must raise usage errors (not crash) for missing required flags, unknown flags, or duplicate flags.
- **FIFO/MD5 fields**: not fabricating fields the service doesn't return, and correctly passing through fields like `MessageGroupId`, `MessageDeduplicationId` when provided.
- **Region/credential env var naming mismatches** — must respect whatever the harness sets (e.g., `AWS_ENDPOINT_URL`, `AWS_ENDPOINT_URL_SQS`, `AWS_DEFAULT_REGION`/`AWS_REGION`) without silently defaulting to something incompatible with the test environment.

## Cheat surface

- Fabricating a fake local queue/message store instead of calling the real backend — would pass isolated single-process tests but fail cross-invocation consistency checks (since each CLI invocation is a fresh process with no shared state) and fail against the actual harness backend the grader uses.
- Hardcoding canned JSON responses for known test commands rather than actually calling the service — would fail on the real random message ids/receipt handles/ARNs and on state consistency checks (list-queues after create/delete).
- Shelling out to the real `aws` CLI or importing `awscli` — explicitly forbidden and detectable.
- Swallowing all errors and always exiting 0 — would fail negative-path tests expecting nonzero exit and stderr class identification.
- Printing the full exception/traceback text to stderr as the "error message" — could superficially resemble an error message but violates "no raw tracebacks" and likely fails class-matching regexes expected by the harness (envelope/bare-code/usage-prefix shapes).
- Doing client-side validation to preemptively reject/accept inputs the service would judge — risks diverging from actual service semantics (e.g., wrongly rejecting a valid FIFO name variant, or wrongly accepting something the service would reject) and violates the "don't validate client-side" constraint.

## Success criteria

- All 17 subcommands parse their documented flags (and only those) correctly, reject unrelated/unknown flags with a usage error, and forward properly-typed parameters to the SQS-compatible backend.
- Successful invocations print only a JSON document to stdout, nothing to stderr, exit 0.
- Failed invocations print nothing to stdout, print a single stderr line matching one of the three accepted error-class shapes, and exit with a nonzero code drawn from `{1,252,254,255}`.
- No raw stack trace is ever emitted regardless of failure mode (network error, malformed JSON argument, service-side exception, unknown command).
- End-to-end sequences work correctly through the real backend: create-queue → list-queues/get-queue-url see it; send-message(-batch) → receive-message returns byte-identical body and a working receipt handle; delete-message/change-message-visibility work with valid handles and fail with a receipt-handle-is-invalid class on bad handles; purge-queue zeroes the approximate count; set-queue-attributes/tag-queue/untag-queue changes are visible via get-queue-attributes/list-queue-tags; delete-queue causes subsequent operations on that queue to fail with a non-existent-queue error class.
- Batch operations (`send-message-batch`, `delete-message-batch`, `change-message-visibility-batch`) correctly report per-entry success/failure lists reflecting real per-entry outcomes.
- No hardcoded/overridden endpoint, region, or credentials in the submission; it relies entirely on the environment already configured by the harness.