# TRUTH: ac28f9b7-8626-4b52-b861-336fa8bddc6a

## Problem

Implement a stand-alone `aws` executable on `$PATH` that handles four `aws dynamodb` subcommands (`describe-limits`, `list-tables`, `put-item`, `update-item`) by translating CLI argv into DynamoDB JSON-protocol requests against the endpoint configured in the environment, and rendering the response (or a modeled error) in a shape compatible with real `aws` CLI conventions. State (tables/items) must be shared consistently across invocations of the program within a test scenario (e.g. `put-item` followed by `get-item`/`query`), which implies the program talks to a real (already-running, environment-configured) DynamoDB-compatible backend rather than keeping private in-process state.

## Behavioral contract

- Single executable `aws` dispatches on `argv[1] == "dynamodb"`, `argv[2] == <subcommand>`.
- Must not shell out to real `awscli`, must not override endpoint/region/credentials (these come from env vars already set for the test).
- stdout carries only JSON success bodies (parseable via `json.loads`); stderr carries only a one-line, human-readable error identifying the failure class; never both populated together, never a raw traceback.
- Exit codes restricted to `{0,1,252,254,255}` with the documented semantics: 252 = usage/parse error (bad/missing/duplicate/unknown flag, malformed JSON, oversized/empty value), 254 = modeled service exception (e.g. `ResourceNotFoundException`, `ConditionalCheckFailedException`, `ValidationException`), 0 = success. (1/255 reserved for other failure paths but not required to be hit by every case.)
- `list-tables`: returns `TableNames` (and pagination fields) as JSON; empty list is a success, not an error; table-name membership is checked as a set.
- `describe-limits`: returns the DescribeLimits-shaped JSON document, no required flags.
- `put-item`: requires `--table-name` and `--item`; supports the full documented flag set; writing succeeds and is visible to subsequent `get-item`; a failing `--condition-expression` (e.g. `attribute_not_exists(pk)` on an existing key) must fail with `ConditionalCheckFailedException` and must NOT mutate the stored item; writing to a nonexistent table fails with `ResourceNotFoundException`; numbers must be passed through unchanged as `{"N": "<string>"}` — no numeric coercion.
- `update-item`: requires `--table-name` and `--key`; applying `--update-expression` with `--expression-attribute-names`/`--expression-attribute-values` mutates the item, visible via subsequent `get-item`; unescaped reserved words in the expression fail with `ValidationException`; a failing `--condition-expression` fails with `ConditionalCheckFailedException` and does not mutate state.
- Client must NOT validate table names itself (must pass through and let the service reject with `ValidationException`); must not fabricate undocumented flags.
- Argument parsing errors (unknown flag, missing value, duplicate flag, malformed embedded JSON, empty value for a flag that requires a value, oversized value beyond service limits caught client- or server-side) → exit 252, with no network call needed for pure client-side violations (though oversized value is legitimately a case the *service* could also reject — either giving 252 pre-flight or surfacing as a modeled error is acceptable as long as the exit code lands in the required class per the observed test expectation of 252 specifically for that argv pattern).
- Missing required flag entirely (e.g. put-item with only `--item`, no `--table-name`) → 252.
- A syntactically well-formed but semantically-incomplete call reaching the service and getting rejected as a modeled exception (e.g. missing table on the backend for a fully-valid-looking put-item call) → 254.

## Solution decomposition

1. **Argv tokenizer / flag parser** per subcommand: map `--flag value` pairs to API parameter names; reject unknown flags, duplicated flags, flags with no following value (or value starting with `--`), and enforce required flags per operation.
2. **JSON decoding for JSON-valued flags** (`--item`, `--key`, `--expected`, `--expression-attribute-names`, `--expression-attribute-values`, `--attribute-updates`): parse with a JSON decoder; on `json.JSONDecodeError` (or equivalent) exit 252 with a usage-shaped stderr line.
3. **Length/size guard for oversized values**: reject overlong string flag values (e.g. table name > some limit) client-side with exit 252, matching the "oversized-value:512-chars" test cases; note the oversized *item* value test case expects normal processing (not necessarily a 252) — read the specific test list: oversized table-name → 252 (client-side), oversized item value in the "Observed argv patterns" list has no explicit exit code attached (it's just listed as an observed pattern, not an error case) so it should be sent through and let the service arbitrate.
4. **Wire protocol client**: construct DynamoDB JSON 1.0 request (`X-Amz-Target: DynamoDB_20120810.<Operation>`), POST body = JSON parameter map, to the endpoint URL taken from environment (e.g. `AWS_ENDPOINT_URL` / `AWS_ENDPOINT_URL_DYNAMODB`), with a syntactically valid (dummy signature acceptable since local endpoint doesn't verify SigV4 in this harness) `Authorization` header — do NOT hardcode a real signature computation is not required unless the local DynamoDB requires SigV4 validation; if it does, real credential env vars are already present and must be forwarded/used only via config, not overridden.
5. **Response handling**: on 2xx, parse body as JSON, print to stdout, exit 0; on non-2xx, parse the `__type`/`message` envelope, print an error line naming `<ErrorCode>: <message>` (or the full AWS envelope sentence), exit 254 for modeled service exceptions.
6. **Dispatch table** mapping subcommand → (required fields, per-flag type, target operation name) shared by argument validation and request construction.
7. **No client-side business logic reimplementation** — condition-expression evaluation, reserved-word checking, conditional put/update semantics, table existence checks all delegate to the real backend; the program is a thin protocol translator, not a database.

## Solution space

Multiple valid implementation routes exist:

- **boto3-based implementation**: use `boto3.client("dynamodb")` with default env-based credential/endpoint resolution, catch `botocore.exceptions.ClientError` and re-emit a compliant one-line error (do not let boto3 print its own traceback), translate CLI flags to the boto3 kwargs (converting `--limit` to int, JSON flags via `json.loads`), and serialize the response with `json.dumps`. This is likely simpler and more robust than hand-rolled SigV4/JSON-protocol HTTP, and is explicitly allowed since boto3 is a Python standard library-adjacent package commonly preinstalled in the image (not "awscli" and not shelling to `aws`).
- **Raw HTTP JSON-protocol client** (as in the reference): construct requests by hand with `urllib`/`http.client` and a placeholder/dummy Authorization header if the local test endpoint does not enforce real SigV4 signatures. This works only if the environment's DynamoDB endpoint (e.g. DynamoDB Local or a moto server) does not require valid signatures — a real assumption for this harness given the reference does so.
- **Any language** (Go, Node, etc.) with an equivalent AWS SDK or raw HTTP client, provided the process is exposed as an executable file named `aws` on `$PATH` (a shell wrapper delegating to a script in another language is fine, provided it doesn't shell out to the real `aws` CLI).
- Argument parsing can be done via a generic argparse-like library or manual token-walking, as long as unknown/duplicate/missing-value flags produce 252 and required-field omissions produce 252.
- Error class detection can rely on botocore's `ClientError.response["Error"]["Code"]` or manual parsing of the JSON-protocol error envelope (`__type`) — both are acceptable as long as the resulting stderr line names the error class per the three permitted shapes.
- Whether oversized/malformed values are rejected purely client-side vs. forwarded to the service and rejected there is a valid design choice **except** where the test's declared exit code demands one specific class (252 for the listed error cases) — those specific enumerated cases must reliably produce 252, but the general oversized-item case (not listed as an error case) can be handled either way as long as it doesn't crash and doesn't fabricate an incorrect success.

## Known pitfalls

- Emitting both stdout and stderr on the same invocation (e.g. printing partial output before failing) breaks the "stdout empty on failure" contract.
- Letting an uncaught exception (JSON decode error, KeyError, connection error, boto3/botocore traceback) reach the terminal — must be caught and converted to a one-line message.
- Treating `--limit` or other int flags loosely (e.g. accepting non-numeric strings) instead of failing with 252.
- Not enforcing "duplicate flag" rejection (`--table-name <x> --table-name <y>` must be 252, per test).
- Not rejecting an invalid trailing flag with no value or a flag whose value looks like another flag (`--table-name --item ...`) as 252 — must not silently consume it as the value.
- Missing required-flag detection entirely delegated to the server (server might return a different exception class or crash) instead of validating client-side, causing the wrong exit code (254 or 255 instead of 252) for the pure omission cases.
- Client-side validation of table name *content* (format/charset) is explicitly forbidden — only enforce size/empty-value/parse issues that are genuinely client-parsing problems, not business rules; let the service raise `ValidationException` for malformed table names otherwise.
- Reformatting/mutating numeric AttributeValues (e.g. coercing `{"N": "5"}` to a JSON number) — must remain a string.
- Overriding region/endpoint/credentials in code, which breaks the test harness's ability to point the CLI at its local DynamoDB double.
- Forgetting `list-tables` with zero tables is success (empty list), not an error.
- Assuming table/item ordering in list assertions — tests check membership only.
- Mixing up exit codes 252 vs 254: pure argv/parse problems must never surface as 254, and genuine service-side modeled failures (missing table on a well-formed put-item call) must never surface as 252.
- Not flushing/buffering causing interleaved or truncated output under the test harness's subprocess capture.

## Cheat surface

- Faking `list-tables` output from an in-memory Python dict instead of a real backend would satisfy simple single-call tests but fail the cross-command consistency requirement (put-item → get-item → query) since state wouldn't be shared with other commands' processes — this is the central trap the task is testing against: no local, non-persistent, in-process state that vanishes between subprocess invocations.
- Hardcoding a canned "ResourceNotFoundException" style response for every put-item to missing-table case without actually asking a real service would break the case where the table *does* exist and the put should succeed.
- Special-casing exact expected JSON literal strings for known table names seen in the observed argv examples (e.g. treating `<string>` placeholders as if literal) instead of generically parsing whatever table name is passed.
- Suppressing all errors and always exiting 0 to dodge the failure-path checks — would fail every negative test (ConditionalCheckFailedException, ValidationException, missing-table, usage errors).
- Printing a generic "error" without naming the class (breaks the stderr shape requirement that error class must be identifiable).
- Ignoring `--condition-expression` / `--update-expression` and always succeeding regardless of semantics — fails the explicit conditional-failure and reserved-word test cases.

## Success criteria

- All four subcommands dispatch correctly from a single `aws` executable on `$PATH`, sharing state through a real DynamoDB-compatible backend so that put-item/update-item effects are visible to subsequent get-item/query calls issued as separate subprocess invocations.
- `list-tables` and `describe-limits` produce valid JSON on stdout with expected top-level keys (`TableNames`, limits fields respectively), empty-state list-tables succeeds with `[]`.
- `put-item`/`update-item` happy paths produce valid JSON (or empty document) on stdout, exit 0, and are reflected in later reads.
- Conditional-expression failures and reserved-word violations surface as `ConditionalCheckFailedException`/`ValidationException` on stderr with exit 254, without mutating stored state.
- Missing table triggers `ResourceNotFoundException`, exit 254.
- All enumerated client-side usage errors (missing required flag, unknown flag, empty value, duplicate flag, malformed embedded JSON, oversized table-name) exit 252 with a usage-class stderr line and empty stdout.
- No stdout/stderr mixing, no tracebacks, in any of the 115 shipped tests, exit codes always within `{0,1,252,254,255}`.