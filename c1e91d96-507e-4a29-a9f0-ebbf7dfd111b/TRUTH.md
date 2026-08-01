# TRUTH: c1e91d96-507e-4a29-a9f0-ebbf7dfd111b

## Problem

Implement a standalone `aws` executable that emulates the subset of the real `aws dynamodb` CLI needed for `create-table`, `describe-table`, `get-item`, and `put-item`. The program must talk to a DynamoDB-compatible service already reachable via environment-configured endpoint/credentials, translate CLI flags into the DynamoDB JSON wire protocol, and relay responses/errors faithfully. State (tables and items) is owned by the backing service, not by the CLI process, so correctness is judged across sequences of invocations (create → put → get) as well as per-command argument validation and error-code discipline.

## Behavioral contract

- Single executable `aws` on `$PATH`, dispatching on `argv[1] == "dynamodb"` and `argv[2]` as the subcommand.
- Success: DynamoDB JSON response document on stdout only, exit 0, nothing on stderr.
- Failure: nothing on stdout, one human-readable line on stderr naming the error class (service error code like `ResourceNotFoundException`/`ResourceInUseException`/`ConditionalCheckFailedException`/`ValidationException`, or a client usage-error prefix), exit code from `{0,1,252,254,255}`, never a stack trace.
- Argument parsing (usage-level) failures → exit 252: unknown flag, missing required flag, missing value for a flag, empty value for `--table-name`, duplicate flag, malformed JSON passed to a JSON-valued flag, oversized `--table-name` (512 chars) rejected client-side as a usage error (note: general table-name *content* validation is service-side, but this oversized case is explicitly required to fail at 252 — i.e. some client-side length guard is expected, or it's rejected before ever reaching the network in a way that maps to 252).
- Service-modeled failures (table not found, table already exists, conditional check failed, key/attribute-definition mismatch) → exit 254 (or 1, both are in the allowed set; per the error-case table for these 4 commands, the expected value is 254).
- Numbers in Item/Key JSON must be passed through as-is (`{"N": "5"}` — a string value), never coerced to native JSON numbers.
- Reads must be strongly consistent: immediately after a `put-item`, a `get-item` for that key returns the written attributes.
- `get-item` on a non-existent key returns a JSON object with no `Item` key (still exit 0, not an error).
- `create-table` twice with the same name is an application-level failure (`ResourceInUseException`), not a usage error.
- `--key-schema` referencing an attribute name absent from `--attribute-definitions` is a `ValidationException`.
- No flags beyond each command's documented set may be implemented/accepted; unrecognized flags always error at 252.
- Do not hardcode/override region, endpoint, or credentials — read them from environment only.
- No shelling out to real `aws`/awscli; no network calls beyond the configured DynamoDB endpoint.

## Solution decomposition

1. **Argv dispatch**: read `sys.argv[1]` (`dynamodb`) and `sys.argv[2]` (subcommand); route to one of 4 handlers; unknown subcommand or too few args → usage error.
2. **Flag parser** shared across commands: walks remaining args, recognizing `--flag value` pairs and boolean flags (e.g. `--consistent-read`); rejects tokens that aren't in the command's known flag set; rejects duplicate flags; rejects a flag with no following value when one is required; treats an empty string as no value for `--table-name`.
3. **Value/type translation**: values that are meant to be JSON (`--key`, `--item`, `--attribute-definitions` when JSON-shaped, `--sse-specification`, etc.) get `json.loads`'d and any parse failure becomes a usage error (252) — never silently passed through or crashing with a traceback. Shorthand syntax (`AttributeName=id,AttributeType=S`) must also be accepted and converted to the equivalent JSON structure for `--attribute-definitions` / `--key-schema` in create-table.
4. **Oversized-value guard**: reject overlong `--table-name` (and similarly oversized values noted in the observed patterns) before dispatching to the service, exit 252.
5. **HTTP call layer**: build a DynamoDB `x-amz-json-1.0` request with correct `X-Amz-Target` (`DynamoDB_20120810.<Operation>`) against the endpoint from environment variables, POST, and on success print the parsed JSON body (or `{}`/appropriate default) to stdout, exit 0.
6. **Error mapping**: on HTTP error, extract the DynamoDB `__type`/`message` from the JSON error body and print a `<ErrorCode>: <message>` or AWS-envelope-style line to stderr, exit 254 (or another allowed non-zero code); on network/connection failure, still exit non-zero without a stack trace and without printing to stdout.
7. **create-table defaults**: when the caller omits `--attribute-definitions`/`--key-schema`/billing info, the implementation may supply sane defaults, but must still forward whatever the caller specified, and must not silently drop `--billing-mode PAY_PER_REQUEST`.
8. **Per-command payload building**: map each documented flag 1:1 to the corresponding DynamoDB API JSON field (TableName, Key, Item, ConditionExpression, ConsistentRead, etc.), only including fields that were actually passed (aside from defaults in create-table).

## Solution space

Any of these are equally valid and should not be penalized:
- Language choice: Python, Node, Go, shell+curl, etc. — anything already available in the image, calling the DynamoDB endpoint directly over HTTP(S) with the `x-amz-json-1.0` protocol and SigV4-style (even dummy/placeholder) auth headers, OR using a pre-installed SDK (e.g., `boto3`, if present in the image) configured purely from environment variables without overriding endpoint/region/credentials.
- Using boto3's `client("dynamodb")` (letting boto3 read env-configured endpoint/creds) and catching `botocore.exceptions.ClientError` to map `error.response["Error"]["Code"]` to the stderr line, instead of hand-rolling HTTP requests and signing.
- Implementing argument parsing with `argparse` (customizing error handling to hit exit 252) instead of a hand-rolled flag walker, as long as duplicate/unknown/missing-value flags still map to 252.
- Emitting the AWS CLI-style full error envelope vs. the bare `<ErrorCode>: <message>` form — both are accepted per the output contract.
- Supplying default `AttributeDefinitions`/`KeySchema`/throughput for create-table vs. requiring the caller to always pass them (as long as behavior matches when they ARE passed, and the flagged create-table-without-required-fields case correctly surfaces as some service/usage error already covered by test cases).
- Using exit code 1 instead of 254 for service-modeled errors, or 255 for other/general failures — the spec explicitly allows any non-zero code in `{1,252,254,255}` for failures; tests reportedly check `returncode != 0` for generic failure classification, though the per-case tables specify particular codes (252 vs 254) that should still be honored where explicitly given.
- Any internal state management is irrelevant since state lives in the backing service — the CLI is stateless per-invocation.

## Known pitfalls

- Conflating usage errors (bad flags/JSON/missing args — 252) with service errors (bad business state — 254): e.g. a duplicate `--table-name` flag must be a *parse-time* 252 failure, not forwarded to the service.
- Coercing DynamoDB numeric `N` attribute values into native JSON numbers when reflecting responses — must preserve the AttributeValue envelope shapes exactly as returned by the service (pass-through, don't re-model).
- Printing partial output before an error occurs (mixing stdout/stderr) — every code path must fully commit to either the success or failure branch and only write once.
- Letting library exceptions (JSON decode errors, KeyError, connection exceptions) propagate as raw tracebacks — must be caught and converted to a controlled stderr message + exit code.
- Not validating `--key-schema` against `--attribute-definitions` client-side is FINE (should be left to the service) — only explicit usage-shape errors (bad flags, bad JSON syntax, size limits, duplicates) belong client-side; do not add extra client-side semantic/business validation (e.g. table-name character validation) beyond what's explicitly required.
- Forgetting that `get-item` on a missing key is a **success** (exit 0, no `Item` key) rather than an error — a common overcorrection is to treat "not found" as an error condition.
- Swallowing `--billing-mode`/`--provisioned-throughput`/other pass-through flags instead of forwarding them into the request payload.
- Not handling boolean/no-value flags (`--consistent-read`) distinctly from value-taking flags, causing them to consume the next token as a bogus "value" and break subsequent parsing.
- Hardcoding endpoint/region/credentials instead of reading from environment — breaks in the sandboxed test environment.

## Cheat surface

- A submission that always exits 0 with a plausible-looking JSON blob without ever contacting the service would fail cross-command consistency tests (put then get) and the explicit ResourceInUseException/ConditionalCheckFailedException/ResourceNotFoundException checks — these require real service round-trips, so pure stubbing is caught.
- A submission that just greps argv for flag substrings instead of proper parsing may pass simple cases but fail duplicate-flag/unknown-flag/missing-value 252 checks — these are explicitly enumerated per command and must be checked deliberately, not incidentally.
- A submission that ignores `--consistent-read` (since the backing store may already be consistent) can still pass, since strong consistency is required regardless — but must not error out when the flag is present.
- Printing the entire raw exception message on failures might accidentally satisfy the "contains error class name" check for some libraries (e.g., botocore raises exceptions whose `str()` includes the error code) — this is legitimate use, not a violation, as long as it isn't a stack trace.

## Success criteria

- All 90 shipped tests pass: per-command argv/flag validation (252 cases), per-command service-error cases (254 cases), and functional round-trip assertions (create-table→list-tables visibility, put-item→get-item consistency, conditional-check failure leaving state unchanged, missing-key get returning no `Item`).
- stdout only ever contains valid parseable JSON on success runs, and is empty on failure runs; stderr is empty on success and non-empty with a class-identifying message on failure.
- No stack traces under any tested input, including malformed JSON, oversized values, and missing/duplicate/unknown flags.
- Exit codes fall within `{0,1,252,254,255}` and match the specific value given in each documented error case table where one is specified.
- Behavior is consistent across a full command sequence within one test (state persists in the backing service across separate subprocess invocations).