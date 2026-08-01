# TRUTH: c871ad27-31de-45e0-a166-9b6f068787d0

## Problem

Implement a standalone executable named `aws` (placed on `$PATH`, canonically at `/workspace/submission/aws`) that emulates the subset of the real `aws s3` CLI needed for `cp`, `ls`, `mv`, `rb`, and `sync` against an S3-compatible endpoint whose address/region/credentials are supplied entirely through the environment. The implementation must talk to the actual S3-compatible service over HTTP(S) (e.g., via SigV4-signed REST calls, or any available SDK/library already in the image) — it must not shell out to a real `aws` binary and must not import `awscli`. State lives in the remote service, not in the process, so sequences of commands (`cp` then `ls` then `mv` then `rb`) must compose correctly end-to-end because each command is a fresh subprocess invocation.

## Behavioral contract

- Five subcommands (`cp`, `ls`, `mv`, `rb`, `sync`) each accepting the documented positional/flag argv shapes.
- `cp`: local→S3, S3→local, and S3→S3 copies, byte-identical content preservation, round-trip invariant, and optional SSE-KMS encryption (`--sse aws:kms --sse-kms-key-id <key>`) that is verifiably attached to the stored object.
- `ls`: bucket listing (no path), prefix/object listing under a bucket, `--recursive` flattening (no `PRE` lines), `--page-size` cap, empty-bucket success, nonexistent-bucket/empty-match failure, unknown-flag failure.
- `mv`: cp + delete-source-on-success semantics; self-move (identical source/dest URI) must fail; missing args must fail.
- `rb`: removes an empty bucket; fails on nonexistent or non-empty bucket unless `--force`, which empties then removes.
- `sync`: one-directional, timestamp-based delta transfer (upload/download only newer-or-absent files), idempotent on repeat, optional `--delete` for destination pruning, failure on nonexistent local source directory.
- Output contract: stdout-only `<op>: <resource>` line(s) on success (optionally preceded by progress lines), empty stderr on success; on failure, empty stdout and one of several acceptable stderr shapes identifying the failure class, no tracebacks.
- Exit codes: 0 success; 1 runtime/service failure; one of {2,252,255} for usage/argument errors (collapsing to 255 is acceptable).
- Must not hardcode/override service endpoint, region, or credentials — read purely from environment.

## Solution decomposition

1. **Environment-driven S3 connectivity**: read `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, region, and endpoint URL env vars; build a low-level client capable of signed GET/PUT/DELETE/List requests against buckets/objects (e.g., hand-rolled SigV4 signer + `http.client`, or `boto3`/`botocore` if present in the image, or any other available HTTP+auth library).
2. **URI parsing**: shared helper to split `s3://bucket/key` into bucket and key, distinguishing local paths from S3 URIs by the `s3://` prefix.
3. **Argument parsing per subcommand**: tolerant parsers that accept documented flags, reject/flag unknown ones with a usage error and appropriate exit code, and validate required positional counts (e.g., `mv` alone must error).
4. **cp implementation**: three transfer directions (local→S3 via PUT with body bytes, S3→local via GET writing to disk, S3→S3 via GET+PUT or a native copy call); attach SSE headers/params when `--sse`/`--sse-kms-key-id` given; ensure any needed multipart handling for large files works transparently (not required by tests but shouldn't break on typical file sizes).
5. **ls implementation**: no-arg → `ListBuckets`; bucket path → `ListObjectsV2` with delimiter `/` unless `--recursive`; format each line with timestamp + size + key (or `PRE` prefix marker in non-recursive mode); treat empty result set specially — empty bucket at bucket-root is success/no-output, but a prefix matching nothing is failure; propagate `--page-size` as `max-keys`/pagination limit; reject unrecognized flags with usage-error exit code.
6. **mv implementation**: reuse cp's transfer logic, then delete the source object/local file only after the copy succeeds; short-circuit with a failure before performing any operation when source URI equals destination URI.
7. **rb implementation**: attempt `DeleteBucket`; on failure due to non-empty bucket, check `--force` — if set, enumerate and delete all objects (paginated) then retry delete-bucket; if not set, propagate the non-empty error; nonexistent bucket surfaces as a runtime error.
8. **sync implementation**: enumerate source (local directory walk or S3 listing) and destination in parallel; for each source item compare existence/mtime (local file mtime vs. S3 `LastModified`) and transfer only when destination missing or stale; when `--delete` is set, remove destination entries absent from source; must be a no-op on unchanged repeat run — meaning the comparison logic must not falsely consider a freshly-uploaded object "newer" due to clock skew, or must at least be stable across two sequential invocations with no source changes.
9. **Output formatting layer**: centralize success messages as `<operation>: <resource>` (e.g., `upload: file to s3://...`, `download: s3://... to file`, `delete: s3://...`) written to stdout only; centralize error formatting to stderr only, never both, and always translate exceptions/tracebacks into one of the accepted error-line shapes.
10. **Exit-code mapping**: distinguish argument/usage errors (missing positionals, unknown flags, malformed S3 URI) → {2,252,255} from service/runtime errors (bucket not found, object not found, self-move, non-empty bucket without force, sync source missing) → 1, and success → 0.

## Solution space

- Any language available in the image (Python, Node, Go, Rust, shell+curl, etc.) is acceptable; the reference uses hand-rolled SigV4 in Python, but using `boto3`, `aiobotocore`, `s3cmd`-style libraries, or a Go/Java AWS SDK is equally valid provided credentials/endpoint come from env vars set by the harness and are not overridden.
- Argument parsing may use `argparse`, manual `sys.argv` walking, `getopt`, or any equivalent, as long as the observed flag/positional shapes are accepted and unknown flags are rejected.
- `ls` bucket-vs-prefix distinction, "PRE" formatting, and date formatting may differ in exact spacing/columns — only the operation-line shape and content classification (bucket names, keys, recursive flatness) are checked.
- SSE-KMS support may be implemented via request headers (`x-amz-server-side-encryption`, `x-amz-server-side-encryption-aws-kms-key-id`) or via an SDK's high-level parameter; either is fine as long as it's readable back from the object (e.g., via `HeadObject`/`GetObject` response headers or equivalent listing/metadata call).
- `mv`/`sync` may be implemented as literal wrappers that call the `cp` logic internally, or as independent code paths — no requirement that `mv` invoke `cp`'s code as a subprocess.
- Multipart upload for large files is optional; single PUT is sufficient unless test fixtures use very large files (not indicated).
- Sync's "newer" comparison can use any reasonable timestamp granularity/strategy (mtime seconds, ETag/hash comparison as a supplement, etc.) as long as it satisfies: untouched files skip transfer on second run, and files absent at destination always transfer.
- Error message text is explicitly unconstrained beyond matching one of the listed shape patterns — implementers can choose AWS-envelope-style, `<op> failed: <reason>`, or a client-side prefixed line.

## Known pitfalls

- **Exit code confusion**: returning 0 on failure paths (e.g., forgetting to propagate a non-zero return from a caught exception) breaks nearly every negative test. Every `ClientError`/exception path must map to a nonzero code, and every success path must return 0 explicitly.
- **Mixing stdout/stderr**: printing partial progress or the operation-success line before an error is later discovered corrupts the "stdout empty on failure" invariant — do transfer/validation first, print success only after confirmed completion.
- **`ls` empty-bucket vs. empty-match ambiguity**: an empty bucket at the root must succeed with no output, but a prefix/key that matches nothing must fail — conflating these (as the reference's naive `if key and not found: return 1` attempts) is easy to get wrong, especially when `key` is empty but the bucket doesn't exist, or when recursive vs. non-recursive listings interact with the delimiter differently.
- **`mv` self-move check**: must compare canonicalized bucket+key (not raw strings that might differ in trailing slashes) before performing any destructive action; must not delete source before confirming destination write succeeded.
- **`rb --force` ordering**: must delete objects first, then the bucket; deleting the bucket first will always fail on non-empty buckets regardless of `--force`.
- **Sync idempotency**: naive "always newer" or unconditional overwrite logic makes the second sync run non-idempotent (transfers everything again), failing the required no-op-on-repeat check. Clock-skew between local filesystem mtimes and S3 `LastModified` timestamps can cause false positives/negatives — needs care (e.g., only transferring on strict inequality plus existence checks, not on any timestamp mismatch within a few seconds).
- **SigV4 signing correctness** (if hand-rolling): canonical request construction, header case-sensitivity, host header port handling, and path-style vs. virtual-hosted-style URLs for custom endpoints are common sources of silent auth failures that surface as opaque service errors rather than test-specific failures.
- **Argument parsers swallowing unknown flags silently**: using a lenient parser (e.g., `argparse.parse_known_args`) without explicitly checking `unknown` for `--`-prefixed tokens defeats the "unknown flag must fail" requirement.
- **Tracebacks leaking to stderr**: any unhandled exception (e.g., `KeyError`, `FileNotFoundError`, XML parse errors on unexpected responses) must be caught at the top level and converted into an accepted error-shape line, never a raw Python/Go/Node stack trace.
- **Not reading endpoint/region/credentials from env**: hardcoding `us-east-1` or `https://s3.amazonaws.com` instead of honoring `AWS_ENDPOINT_URL`/`AWS_ENDPOINT_URL_S3` breaks connectivity to the test harness's local S3-compatible service entirely.

## Cheat surface

- Shelling out to a real `aws` binary or importing `awscli`/`botocore`'s CLI layer directly to do the actual work is explicitly disallowed — a submission that pipes to `os.system("aws ...")` violates the constraint even if it "passes" locally with a real AWS CLI present.
- Faking success by printing the expected `<operation>: <resource>` line without actually performing any network call (e.g., always echoing "upload: ..." unconditionally) would pass shape-only stdout checks but fail because subsequent `ls`/`cp` round-trip commands depend on real state changes in the S3 backend — cross-command consistency checks close this loophole.
- Hardcoding fake bucket-listing output rather than querying the service would fail as soon as a test creates/removes buckets before listing.
- Returning exit code 0 unconditionally would pass some stdout-shape checks but fail all explicit exit-code assertions on error paths (nonexistent bucket, self-move, non-empty rb without force, unknown flags, missing args).
- Ignoring `--sse-kms-key-id` and just uploading plaintext would pass basic cp round-trip tests but fail any check that inspects the stored object's encryption metadata.
- Implementing `sync` as "always copy everything" (ignoring timestamps) would pass a single-run superset check but fail the idempotent-second-run-transfers-nothing requirement if that requirement is checked by asserting no stdout transfer lines / no re-upload calls on the second invocation.

## Success criteria

- All five subcommands operate against the environment-configured S3-compatible endpoint with no hardcoded connection parameters and no shelling out to `awscli`.
- `cp` round-trip byte-identity holds for local→S3→local and direct S3→S3 copies; SSE-KMS parameters are persisted and observable when specified.
- `ls` correctly distinguishes bucket-listing, prefix-listing, recursive-flat listing, and page-size-bounded listing, succeeding with no output on an empty bucket and failing (nonzero exit) on a nonexistent bucket, an empty-match prefix, or an unrecognized flag.
- `mv` performs copy+delete atomically enough that failure prevents source deletion, refuses self-moves, and fails cleanly on missing arguments.
- `rb` refuses non-empty-bucket removal without `--force`, succeeds with `--force` by emptying then deleting, and fails on nonexistent buckets.
- `sync` transfers only newer/absent items in the correct direction, is idempotent on an unchanged second run, optionally deletes extraneous destination items under `--delete`, and fails on a nonexistent local source path.
- Every success path emits at least one `<operation>: <resource>` line to stdout with empty stderr and exit code 0; every failure path emits empty stdout, a class-identifying line on stderr, and an exit code drawn from `{1, 2, 252, 255}` — with no raw tracebacks under any tested condition.
- Cross-command sequences (cp→ls→mv→ls→rb, sync→sync) reflect consistent, real backend state at every step, verifying the implementation is not merely printing expected text without performing real operations.