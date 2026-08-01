# TRUTH: 4282c1c5-7c6a-4e7a-a3d6-c0ee3754afda

## Problem

Implement a standalone `aws` executable (any language, no `awscli` import, no shelling to the real `aws` binary) placed on `$PATH` (conveniently `/workspace/submission/aws`) that supports a subset of `aws s3` subcommands — `cp`, `ls`, `mv`, `rm`, `sync` — against an S3-compatible endpoint configured via environment variables (credentials, region, endpoint URL). The implementation must talk directly to the S3 HTTP API (e.g. via SigV4-signed requests) since no AWS SDK/awscli may be used, and state (objects, buckets) must be genuinely persisted server-side so that sequences of commands interact correctly (upload → list → download → remove).

## Behavioral contract

- Single executable named `aws` on `$PATH`, invoked as `aws s3 <subcommand> [args...]`.
- `cp`: copies bytes local→S3, S3→local, or S3→S3, based on which arguments are `s3://` URIs vs local paths. Round-trip byte-identity is required. `--sse aws:kms --sse-kms-key-id <key>` must result in the object actually being stored with SSE-KMS such that a subsequent head/get shows that encryption metadata.
- `ls`: no-arg form lists owned buckets with creation dates; bucket/prefix forms list objects/common-prefixes; `--recursive` flattens (no `PRE` lines); `--page-size` bounds underlying page size; empty bucket → exit 0, no entries.
- `mv`: cp + delete-source-on-success semantics, for all three directions (local↔S3, S3↔S3).
- `rm`: deletes a single key by default; `--recursive` deletes everything under a prefix (literal-prefix or directory-style trailing-slash semantics both acceptable); `--request-payer` must be forwarded on the delete call.
- `sync`: transfers only newer-or-absent files in the source→dest direction (either local→S3 or S3→local); destination becomes a superset of source; `--delete` (if implemented) prunes dest items absent from source; a no-op second run is required behavior (nothing changes when nothing changed).
- Cross-command consistency: every state-mutating command must be immediately visible to subsequent commands within the same test run (real network calls, no in-memory-only simulation that another process invocation can't see).
- stdout on success: contains a line matching `<operation>: <resource>` (lowercase op, colon, whitespace, resource) per affected resource, anywhere in stdout (progress lines allowed before it). stderr must be empty on success.
- stdout on failure: empty. stderr contains one error line matching one of the three permitted shapes (AWS error envelope, `<operation> failed: <reason>`, or a client-side usage/validation message with a recognizable class prefix). No stack traces ever.
- Exit codes ⊆ {0,1,2,252,255} per the code's documented meaning; collapsing 2/252 into 255 is acceptable.
- Must not override service address/region/credentials in code — read them from environment as already set.
- No additional packages fetched; use only what's already available in the image.

## Solution decomposition

1. **Config/auth layer**: read `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, session token, region, and endpoint URL from env (never hardcode/override). Implement (or use an already-available library for) SigV4 request signing, since no new packages may be installed and awscli/boto3 may not be present or usable per constraints.
2. **HTTP client to S3 REST API**: raw PUT/GET/HEAD/DELETE/POST against bucket/key paths and query-string list operations (`?list-type=2`, `?uploads`, `?partNumber=&uploadId=`, etc.), XML request/response parsing for list/multipart/error bodies.
3. **Error mapping**: turn non-2xx responses and XML `<Error><Code>/<Message>` into the documented stderr shapes and correct exit code class.
4. **Argument parsing per subcommand**: distinguish local paths vs `s3://` URIs, handle each command's flag set, validate positional arg counts (missing arg → 2/252/255; unknown flag → 252/255).
5. **cp**: three directions dispatched by detecting `s3://` prefixes on src/dest; SSE-KMS handling by attaching the right headers on PUT/COPY and being able to report them back via HEAD; large-file support optional (multipart) but not required beyond byte-correctness — note reference used an 8MiB multipart threshold, but a simple single-PUT approach is equally valid for correctness since only exact bytes matter, not method.
6. **ls**: no-path → ListBuckets API; path → ListObjectsV2 with prefix/delimiter, paginate internally, respect `--page-size` as `max-keys` per page, and `--recursive` to omit delimiter (no CommonPrefixes/PRE entries).
7. **mv**: implemented as cp then delete-source, only removing source once destination write succeeded.
8. **rm**: delete single object, or recursive prefix delete (list-then-delete loop); forward `--request-payer` header/query param to delete calls.
9. **sync**: enumerate both sides (local filesystem walk vs S3 listing), compare by existence + mtime/Last-Modified, transfer only newer/absent, optionally delete extras with `--delete`.
10. **Output formatting**: emit `<op>: <resource>` lines for every mutated resource, suppress all other stdout on failure, keep stderr silent on success.

## Solution space

Many implementation routes are valid; the reference (raw Python + hand-rolled SigV4 HTTP client) is just one:

- Using `boto3` or `botocore` directly if already present in the image (the constraint bans awscli/shelling to the real `aws` binary and fetching new packages — using a pre-installed boto3 is not explicitly forbidden if it's already part of the image and not "the real aws binary"; but the safest, universally-accepted route is a from-scratch SigV4 client since the task title is literally "build this CLI from scratch"). If boto3/botocore isn't available, hand-rolled signing (as in the reference) is required.
- Any language (Go, Node, Bash+curl with hand-rolled SigV4, etc.) is acceptable as long as it produces a single `aws` executable and doesn't shell out to `awscli`.
- Multipart upload is optional — single-shot PUT for all file sizes is fine unless the test suite exercises very large files; correctness (byte-identity) is what's graded, not the transfer strategy.
- `rm --recursive` may treat the prefix literally or normalize to a directory (`prefix/`) — both accepted per spec.
- `sync` comparison may use any reasonable timestamp source (local file mtime vs S3 `LastModified`), and `--delete` support is optional (only "if implemented" is required to work correctly).
- Exit code collapsing (all arg errors → 255) is explicitly permitted.
- Progress/informational lines before the final `<op>: <resource>` line are allowed and not penalized.

## Known pitfalls

- Overriding region/endpoint/credentials in code instead of reading from env — breaks against the test harness's actual S3-compatible backend.
- Forgetting SigV4 canonical request details (URI encoding, empty-body hash `e3b0c44...`, signed-headers list, host header) — causes silent auth failures manifesting as opaque errors rather than the documented shapes.
- Leaking Python/Go tracebacks on unexpected exceptions instead of catching and emitting a classed stderr message — violates the "no stack trace ever" rule.
- Printing anything to stdout when a command fails (must be empty on failure).
- `mv` deleting the source before confirming the destination write succeeded (leads to data loss on failure, and violates the "mv = cp + rm on success" contract).
- `ls --recursive` still emitting `PRE` common-prefix entries (must flatten, using no delimiter).
- Not paginating `ListObjectsV2` (only returns first ~1000 keys) — breaks large listings/recursive rm/sync.
- SSE-KMS: writing the header but not making it retrievable via HEAD, or not actually setting `x-amz-server-side-encryption`/`x-amz-server-side-encryption-aws-kms-key-id` headers on the PUT/COPY call.
- `rm --recursive` deleting keys outside the intended prefix due to literal substring matching without considering the trailing-slash boundary (spec tolerates literal-prefix behavior, but must still only match test's trailing-slash inputs correctly).
- `sync` re-uploading/re-downloading unchanged files every run (breaks "second sync is a no-op") due to skipping the mtime/Last-Modified comparison.
- Not creating parent directories for local downloads (`cp s3://... local/nested/path.txt` failing on missing dirs).
- Off-by-one/format issues in `<operation>: <resource>` lines causing the grader's pattern match to fail (must be `lowercase: whitespace resource`, findable anywhere in stdout).
- Case-sensitivity/whitespace mismatches for `--sse`/`--sse-kms-key-id` flag parsing, or crashing when unrecognized flags appear.

## Cheat surface

- Faking state locally (e.g., writing to a local sidecar file/database instead of the real S3-compatible backend) would make single-process command chains appear to work but fail once the harness runs each invocation as a genuinely separate subprocess against a shared external endpoint — must not simulate S3 in memory.
- Hardcoding bucket/object existence or always returning success without performing real HTTP calls would pass trivial "does it print the line" checks but fail retrieval/listing verification steps that call back into the same S3 endpoint independently.
- Ignoring `--sse`/`--sse-kms-key-id` and just printing the success line without setting the encryption header would pass a naive "exit 0" check but fail metadata verification.
- Ignoring `--request-payer` on `rm` while still deleting the object would pass basic removal checks but fail payer-forwarding verification if the harness inspects the request.
- Printing the `<op>: <resource>` line without actually performing the operation (or after a failed HTTP call) would violate the stdout/stderr success-failure exclusivity contract and get caught by round-trip/listing checks.
- Treating `sync`'s "no-op on second run" loosely by always re-uploading (harmless functionally but wastes calls) is not a correctness cheat but could trip up timestamp-based graders if implemented incorrectly.

## Success criteria

- All targeted state-mutating commands (`cp`, `mv`, `rm`, `sync --delete`) produce durable, externally observable changes on the real S3-compatible endpoint, confirmed by subsequent independent `ls`/`cp` (download) calls in later subprocess invocations.
- Round-trip byte-identity holds for local→S3→local transfers.
- SSE-KMS parameters are persisted and observable via the stored object's metadata.
- `ls` output correctly reflects bucket list / object list / common-prefix behavior, respects `--recursive` and `--page-size`.
- `rm` removes exactly the intended object(s); `--recursive` removes everything under the target prefix/directory; `--request-payer` is honored.
- `sync` transfers only newer/absent items, makes destination a superset of source, and is idempotent (no-op) on immediate re-run over an unchanged pair.
- Success output always follows the `<op>: <resource>` shape with empty stderr; failure output always has empty stdout and a classed stderr message; no stack traces ever surface.
- Exit codes always fall within `{0,1,2,252,255}` and match the documented semantic class for each failure type.
- No use of `awscli`/real `aws` binary as a subprocess; no environment overrides of region/endpoint/credentials; no additional package installs required at runtime.