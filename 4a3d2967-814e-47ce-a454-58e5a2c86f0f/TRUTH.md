# TRUTH: 4a3d2967-814e-47ce-a454-58e5a2c86f0f

## Problem

Implement a minimal `aws` CLI stand-in that supports exactly two DynamoDB subcommands, `query` and `scan`, dispatching from a single `aws` executable on `$PATH`. The program must forward requests to a real (test-provided) DynamoDB-compatible endpoint configured via environment variables, translate CLI flags into the corresponding DynamoDB JSON API request fields, and translate the HTTP/service response (success or modeled error) into the documented stdout/stderr/exit-code contract. State (tables/items) lives in the backing service, not in the CLI process, so sequences like `create-table` → `put-item` → `query` must behave consistently across separate invocations.

## Behavioral contract

- Single executable named `aws` on `$PATH` (may live in `/workspace/submission/`, any language).
- Invoked as `aws dynamodb <query|scan> [flags...]`.
- Only the documented flags per command are accepted; each flag maps to the correct DynamoDB request field (see flag lists in the instruction) with correct JSON/int/string typing.
- `--table-name` is required for both commands; missing it (or missing the command, or malformed args) → exit `252`, empty stdout, brief usage message on stderr.
- Unknown flags, duplicate flags, empty values, malformed JSON in a JSON-typed flag, and oversized values (512+ chars is one probe, though *no client-side length validation is required*—it's fine for that to reach the service, but the resulting failure must still surface as one of the accepted non-zero codes with proper stdout/stderr separation) must produce exit `252` for pure usage errors detected before any network call. Note: the oversized-table-name case and the "not valid json" case are both usage-detectable client-side (malformed JSON parse failure, or arg-parsing failure) and must exit `252`.
- A syntactically valid request against a nonexistent table produces a modeled service error (`ResourceNotFoundException` from DynamoDB) → exit `254`, stderr contains an error line naming the error class, stdout empty.
- On success: stdout contains the full JSON response body (parseable as JSON), stderr empty, exit `0`.
- Never print a raw Python/other-runtime traceback under any failure path.
- Do not hardcode/override AWS region, credentials, or endpoint — read them from environment.
- No client-side validation of table name format — let the service reject it.
- AttributeValue values (in JSON flags like `--expression-attribute-values`, `--exclusive-start-key`) pass through untouched to the service in DynamoDB AttributeValue form (numbers as string-wrapped `{"N": "5"}`), no reinterpretation needed by this CLI since it's just a passthrough of JSON blobs.

## Solution decomposition

1. **Argv dispatch**: recognize `dynamodb` as the service token, then branch on `query` vs `scan`.
2. **Flag table per subcommand**: an allow-list mapping each `--flag-name` to (API field name, value kind: string/int/bool/json).
3. **Arg parser**: consume `--flag value` or `--flag=value` pairs; reject anything not in the allow-list, reject missing values, reject duplicate flags, reject unparsable JSON/int values — all these are usage errors → exit 252 before any network call.
4. **Payload construction**: build the DynamoDB JSON-protocol request body (`Query`/`Scan` operation names under `DynamoDB_20120810.<Op>` X-Amz-Target) from the validated flags, requiring `TableName` present.
5. **Transport**: sign/send (or just send with dummy/env credentials — signature verification is presumably not strictly enforced by the test backend, but must not override endpoint/region/creds env vars) an HTTP POST to the DynamoDB endpoint derived from environment.
6. **Response handling**: 
   - HTTP 2xx → parse body JSON, pretty/plain print to stdout, exit 0.
   - HTTP error → parse `__type`/`message`, emit `<ErrorCode>: <message>`-shaped (or AWS envelope-shaped) line to stderr, exit 254 (or 1/255 per code semantics — 254 for modeled service errors like ResourceNotFoundException is the expected mapping here).
   - Network/connection failure → stderr message, non-zero exit (not a traceback).
7. **Strict stdout/stderr separation**: never write to both streams in the same invocation; on any failure stdout must be empty.

## Solution space

Multiple valid implementations exist beyond the Python+urllib reference:

- Any language (bash+curl, Node, Go, Ruby, etc.) implementing the same argv-parsing + HTTP call, as long as no external packages are fetched and no `awscli`/real `aws` binary is invoked.
- Using boto3 (if already available in the image) instead of hand-rolled HTTP+SigV4, as long as errors are caught and reformatted (not raw tracebacks) and boto3 is not "fetched" (already installed is fine, but instruction says no additional packages — using pre-existing boto3 if present is acceptable; using bare HTTP with dummy auth headers, as reference does, is also acceptable since the backend evidently doesn't hard-require valid SigV4).
- Exit code choices: 254 vs 1 vs 255 for various failure classes are all acceptable as long as they're non-zero and in `{0,1,252,254,255}`; tests reportedly check `returncode != 0` for most failure assertions, with 252 specifically required for usage errors and 254 documented for the "call succeeds in transport but table doesn't exist" cases per the explicit exit-code table in the instruction.
- Error message format: any of the three shapes (AWS envelope, bare `Code: message`, or `usage:`/`Parameter validation failed:`/`Unknown options:` prefix) is acceptable — implementations need not match the reference's exact `"usage error: "` or `"<Code>: <message>"` strings.
- Pretty-printing JSON with indentation is optional; compact JSON also satisfies "parseable with json.loads".
- Validating known-flag lists via argparse/click-style libraries (if available) instead of a hand-rolled loop.
- Implementations may support `--flag=value` only, `--flag value` only, or both — instruction's observed patterns use space-separated, so at minimum that form must work.

## Known pitfalls

- Forgetting that numbers in AttributeValue JSON are strings (`{"N":"5"}`) — must not attempt numeric conversion/validation of embedded JSON blobs; just pass through.
- Doing client-side validation of table-name syntax — instruction explicitly forbids this; only the service may reject malformed names, so implementers must not add a regex check that produces false-positive 252s that don't match expected error class semantics (though in practice an oversized 512-char name given as a plain `--table-name` value with nothing else wrong is not itself a usage error in this framework — the 252 in that test case arises for a different reason, e.g., it's paired with an otherwise-malformed argv in the enumerated case; solutions should be careful not to over-engineer bespoke length checks that diverge from spec, but since the instruction lists that exact case with exit 252, a solution may reasonably reject overlong values as a defensive parse-time abort — either treating it as a value-validation usage error, or letting it flow to the service and get a modeled error under 254 would violate the documented exit code of 252 for that exact case, so client-side length capping is actually necessary here despite the "do not validate table names" line — the two must be reconciled: syntactic content validation is forbidden, but a coarse size/DoS guard producing 252 is expected).
- Mixing stdout/stderr — e.g., printing partial success output before discovering an error, or writing warnings to stdout.
- Letting an uncaught exception (JSON parse error, KeyError, network exception) propagate as a raw traceback — must be caught and converted to a clean one-line message.
- Hardcoding/overriding endpoint, region, or credentials instead of reading from environment — breaks the test harness's ability to point the CLI at its mock/real backend.
- Treating `--consistent-read` / `--scan-index-forward` boolean flags incorrectly (e.g., requiring a value argument) when AWS CLI convention treats them as no-value boolean switches (with `--no-*` negation forms).
- Not requiring `--table-name`, allowing malformed request payloads to reach the service and returning a different exit code than the documented 252 for missing-required-arg cases.
- Restricting the flag allow-list incorrectly (missing a documented flag, or inventing an undocumented one) — instruction explicitly forbids fabricating flags.
- Not detecting duplicate `--table-name --table-name` as a usage error (252).
- Confusing `query`'s `ValidationException` requirement (querying non-key attribute in key-condition) — this is a service-side behavior; the CLI must not swallow/reinterpret this error, just forward it to stderr appropriately labeled and exit non-zero (254 or 1).

## Cheat surface

- Faking canned JSON responses without actually calling any backend (would fail cross-command state consistency tests like query-after-put-item, and would fail ResourceNotFoundException-triggering tests for unknown tables).
- Hardcoding a fixed "success" JSON blob regardless of table existence — would break the `--table-name <string>` alone → exit 254 error-case tests, since a fake always-success implementation would return 0 instead of 254.
- Catching all exceptions and emitting a generic message with exit 0 — would break failure-path assertions requiring non-zero exit and empty stdout.
- Shelling out to a real `aws` CLI or importing `awscli` — explicitly forbidden and likely detected by environment/tooling constraints (no such binary/package available).
- Printing to both stdout and stderr on error (e.g., debug logging to stdout) — violates "stdout empty on failure."
- Ignoring flag types (e.g., treating `--limit` as string) — could still round-trip JSON correctly by accident, but risks service-side type errors surfacing as unexpected error classes.
- Skipping the unknown-flag rejection and silently ignoring unrecognized flags — would make `--not-a-real-flag x` cases return 0 or the wrong code instead of 252.

## Success criteria

- All enumerated observed argv patterns for `query` and `scan` execute without client-side rejection when well-formed, returning valid JSON (`Items`, etc.) on stdout with exit 0.
- All enumerated error cases produce exactly the documented exit code (252 for usage/parse errors, 254 for the bare `--table-name <string>` no-op-table-doesn't-exist case) with stderr containing a recognizable error-class string and stdout empty.
- `query` returns items matching the partition key from `--key-condition-expression`, order-insensitive unless a sort-key range is given; using a non-key attribute in the key condition yields a `ValidationException`-class failure.
- Cross-command state consistency: items written via `put-item` (external to this diff scope but part of the broader suite) are retrievable via `query` on the same table/key.
- No raw tracebacks ever appear on stderr; no output on stdout during any failure; no mixing of the two streams.
- No unauthorized flags accepted; no fabricated flags; no client-side table-name content validation beyond coarse size guarding needed to hit the documented 252 case.
- Environment-provided endpoint/region/credentials are respected, never overridden in code.