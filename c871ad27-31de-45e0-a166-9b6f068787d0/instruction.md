# Build an `aws s3` CLI

## Application overview

You will implement the following `aws s3` commands:
`s3 cp`, `s3 ls`, `s3 mv`, `s3 rb`, `s3 sync`.

Your code is invoked as a subprocess:

```bash
aws s3 <command> [args...]
```

State must remain consistent across commands so a sequence such as upload,
list, download, remove behaves correctly end-to-end.

## Commands

### `s3 cp`

Argv shapes observed:

- `<local-path> s3://bucket/key.txt`
- `<local-path> s3://bucket/key.txt --sse aws:kms --sse-kms-key-id <key>`
- `s3://bucket/key.txt <local-path>`
- `s3://source-bucket/key s3://dest-bucket/key`

Flags: `--sse`, `--sse-kms-key-id`

Behavior:

- Local-to-S3: the local file's bytes become the object at the given S3
  URI. After success the object is retrievable and appears in listings.
- S3-to-local: the object's bytes are written to the given local path. The
  resulting local file must be byte-identical to the source object.
- S3-to-S3: an independent copy is created at the destination; both copies
  must exist after the operation.
- Round-trip invariant: `cp local.txt s3://b/k` followed by
  `cp s3://b/k local2.txt` must produce `local2.txt` byte-identical to
  `local.txt`.
- When `--sse aws:kms --sse-kms-key-id <key>` is provided, the object must
  be stored with server-side KMS encryption referencing that key. The
  encryption settings must be readable from the stored object's metadata.

### `s3 ls`

Argv shapes observed:

- `s3 ls`
- `s3 ls s3://bucket`
- `s3 ls s3://bucket/<prefix>`
- `s3 ls s3://bucket/ --recursive`
- `s3 ls --extra-argument-foo`

Flags: `--recursive`, `--page-size`

Behavior:

- No path: list every bucket the caller owns, one per line, each with its
  creation date.
- `s3://<bucket>/`: list objects and common prefixes under the bucket.
- `s3://<bucket>/<prefix>`: list keys matching the prefix.
- `--recursive`: walk every sub-prefix; output is flat (no `PRE` directory
  entries).
- `--page-size <n>`: cap the underlying listing batch size at `n` items.
- Empty bucket: exit 0 with no listed entries.
- Non-existent bucket, or a prefix that matches no key: must fail with a
  non-zero exit code; the exact error message is implementation-defined.
- An unknown flag (for example `--extra-argument-foo`): must fail with a
  non-zero exit code.

### `s3 mv`

Argv shapes observed:

- `s3 mv s3://bucket/key s3://bucket/key`
- `s3 mv <local-path> s3://bucket/key.txt --website-redirect <local-path>`
- `s3 mv s3://bucket/key s3://bucket/`
- `s3 mv s3://bucket/key.txt s3://bucket/key2.txt --metadata-directive REPLACE`
- `mv`

Flags: `--metadata-directive`, `--website-redirect`

Behavior:

- Equivalent to `cp` followed by removal of the source on success.
- Source equal to destination (same S3 URI): must fail with a non-zero
  exit code; an object cannot be moved onto itself.
- Local-to-S3 move: the local file is removed; the S3 object exists at
  the destination.
- S3-to-S3 move: the source S3 key is removed; the destination S3 key
  exists.
- S3-to-local move: the S3 key is removed; the local file is created.
- Missing arguments (for example a bare `mv`): must fail with a non-zero
  exit code.

### `s3 rb`

Argv shapes observed:

- `s3 rb s3://bucket`
- `s3 rb s3://bucket --force`

Flags: `--force`

Behavior:

- After successful removal, the bucket no longer appears in the bucket
  listing.
- Removing a non-existent bucket: must fail with a non-zero exit code;
  the exact error message is implementation-defined.
- Removing a non-empty bucket without `--force`: must fail with a
  non-zero exit code; the exact error message is implementation-defined.
- With `--force`: every object in the bucket is removed first, then the
  bucket itself.

### `s3 sync`

Argv shapes observed:

- `s3 sync . s3://mybucket --recursive`
- `s3 sync <local-path> s3://bucket/`
- `s3 sync s3://bucket/ <local-path>`

Flags: `--recursive`, `--delete`

Behavior:

- Syncs source to destination, transferring only files that are newer or
  absent at the destination.
- Local-to-S3: uploads files that do not exist in S3, or whose local
  modification time is newer than the existing object's last-modified
  time.
- S3-to-local: downloads objects that do not exist locally, or whose S3
  last-modified time is newer than the local file's modification time.
- After sync, the destination's file/object set must be a superset of the
  source's.
- Sync does not delete by default; `--delete`, if implemented, removes
  destination items that are not present at the source.
- A second sync over an unchanged source/destination pair transfers
  nothing (idempotent).
- Non-existent source directory (local): must fail with a non-zero exit
  code; the exact error message is implementation-defined.

## Cross-command behavior

State must remain consistent across the command set:

- After `cp <local> s3://bucket/key`, the object is listed by
  `ls s3://bucket/` and retrievable; `cp s3://bucket/key <local2>`
  produces bytes identical to the original.
- `ls` reflects exactly the cumulative effect of all prior commands at
  every step.
- After `mv A B`, the source no longer exists and the destination does
  (`mv` behaves like a copy followed by removal of the source).
- After `rb s3://bucket`, the bucket disappears from the bucket
  listing. `rb` on a non-empty bucket fails unless `--force` is given.
- After `sync`, the destination object set is a superset of the source;
  a second sync over the unchanged pair is a no-op.
- A bucket populated by `cp` or `sync` cannot be removed by a plain
  `rb` until its objects are removed (for example by `rm` or
  `rb --force`).

## Implementation constraints

- Your submission may be written in any language available in the image.
  Use only what the image already provides; no additional packages may be
  fetched.
- Do not import `awscli` or shell out to the real `aws` binary.
- AWS credentials and endpoint are set in the environment; do not
  override the service address, region, or credentials in code.
- Success messages go to stdout; errors go to stderr. Do not mix them.
- Exit codes: `0` on success; `1` on a runtime error (an S3 operation
  failed); and one of `{2, 252, 255}` on an argument-parsing or usage
  error (upstream `aws-cli` returns `252`, bare `argparse` returns `2`,
  and the in-tree reference returns `255` — the grader accepts the
  union). See the "Exit codes" section below for the full contract.
- Do not surface raw library tracebacks; print a brief user-facing
  error string instead.
- Your submission must be an executable named `aws` on `$PATH`. It may be
  written in any language. The image provides `/workspace/submission/`
  first on `$PATH` as a convenient writable install location, but any
  directory on `$PATH` is acceptable. Helper files may live alongside it.

## Output contract

A correct implementation produces output in the *shape* described
below, names the *class* of any error reported, uses the documented
exit-code set, and never surfaces a runtime stack trace. Specific verbs,
error codes, and the exact wording of any message are deliberately not
enumerated here: derive them from the underlying S3 service semantics
and standard `aws s3` conventions.

### stdout (success path)

- A successful command writes one or more lines of the shape
  `<operation>: <resource>`: a lowercase identifier, a colon, whitespace,
  then the affected resource.
- Operations that act on multiple resources emit one such line per
  affected resource.
- Implementations MAY emit informational progress lines (for example,
  `Completed N Bytes/M Bytes ...`) on stdout before the
  `<operation>: <resource>` line(s). Conformance is checked by looking
  for the operation line anywhere in stdout, not as the first line.
- stderr is empty on success.

### stderr (failure path)

- stdout is empty on failure.
- A human-readable error line is written to stderr that identifies the
  failure *class*. Any of the following shapes is acceptable:
  - the underlying AWS service error envelope:
    `An error occurred (<ErrorCode>) when calling the <Operation> operation: <message>`
  - an `<operation> failed: <reason>` template derived from the failing
    command (for example, `remove_bucket failed: ...`)
  - a client-side error line whose prefix names the failure class
    (for example, `usage: ...`, `Unknown options: ...`, `Cannot mv a
    file onto itself: ...`, `The user-provided path ... does not
    exist.`, `Parameter validation failed: ...`)
- Tests assert the failure *class* by matching one of these shapes —
  not verbatim wording — so any spec-compliant phrasing is accepted.
- No runtime stack trace is emitted under any condition.

### Exit codes

The exit code on termination is one of `{0, 1, 2, 252, 255}`:

- `0` — success
- `1` — application error (an S3 operation was attempted and failed)
- `2` — missing or malformed required positional argument
- `252` — parameter/usage error (the real `aws` parameter-validation
  code for an unknown flag, missing/extra argument, malformed value, or
  bad S3 URI)
- `255` — other or general error

Implementations may collapse `2` and `252` into `255` for argument
errors; any non-zero code is acceptable on missing/unknown-argument
paths.
