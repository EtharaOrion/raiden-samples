# TRUTH: f0436714-7110-40a9-8230-cfb384d03166

## Problem

Build a single executable, `/workspace/submission/kubectl`, that reimplements a subset of real `kubectl` against a live (kwok-backed) Kubernetes apiserver reachable via `$KUBECONFIG`. The CLI must be **verb-first** (`kubectl <verb> [TYPE] [NAME] [flags]`), dispatching on `argv[1]` into one of: `apply`, `create`, `delete`, `describe`, `get`, `label`, `patch`, `scale`. It must correctly handle all 13 required kinds (ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Namespace, PersistentVolumeClaim, Pod, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet), entered either via a manifest's `kind:` field (apply/create -f) or via the TYPE positional (get/delete/describe/patch/scale/label). Other RBAC/policy kinds referenced in manifests must be handled via generic discovery rather than being unsupported. The program is exercised as a black-box subprocess across ~390 tests covering success paths, idempotency, state consistency across verb sequences, and a large set of explicit error/exit-code contracts.

## Behavioral contract

- Single binary/script at the fixed path, executable, dispatches on `argv[1]`.
- Reads `KUBECONFIG` from env; never hardcodes cluster endpoints; talks to a real apiserver over HTTP(S) (REST or an SDK client) — no in-memory fake state.
- Exit codes are load-bearing and must match exactly:
  - `0`: success (including `--ignore-not-found` on missing delete target).
  - `1`: server-side/semantic failures — resource not found, already exists, invalid manifest, missing manifest file, generic "no verb/positional given" cases. Stderr must contain `NotFound`/`not found`, `AlreadyExists`, or `Invalid`/`invalid` as documented per case.
  - `2`: CLI-usage/argument-parsing errors — unknown flags (`--invalid-flag`, `--bogus`), missing required positional combined with missing `--all` on delete. Stderr contains `invalid`.
- Stdout success-message shapes must match real kubectl:
  - apply: `<kind>/<name> created|configured|unchanged`
  - create: `<kind>/<name> created`
  - delete: `<kind> "<name>" deleted` (quoted-name form; `<kind>` may be short or `kind.group` qualified)
  - get: tabular by default; machine-parseable for `-o json`/`-o yaml`
  - describe: multi-section human text containing `Name:`, and for Namespace also `Status:` or `Labels:`
  - label/patch/scale: real-kubectl-analogous confirmation text (not pinned exactly, but must not error on valid input)
- State consistency: operations must be immediately visible to subsequent verbs against the same underlying store (create→get→patch→scale→delete must chain correctly; delete removes from list and read returns 404 afterward).
- `apply` is idempotent (re-apply of identical spec → `unchanged`, or `configured` when spec differs); `create` is NOT idempotent (second create → `AlreadyExists`, exit 1).
- Flag surface per verb must be tolerated per the tables in the spec even if some flags are effectively no-ops (e.g., `--dry-run`, `--force`, `--wait`, `--recursive`, `--field-manager`), and unknown/invalid flags must trigger exit 2 usage errors, not crash or exit 1.
- Namespace resolution: `-n`/`--namespace` explicit value takes precedence; otherwise default namespace (`default`) is used; cluster-scoped kinds (Namespace, ClusterRole, ClusterRoleBinding, PriorityClass) must not be namespace-qualified in the actual API call.

## Solution decomposition

1. **Argument parsing / dispatch**: a top-level switch on the verb, per-verb flag parser that recognizes the documented flags/aliases (`-f`/`--filename`, `-n`/`--namespace`, `-o`/`--output`, `-l`/`--selector`, `-A`/`--all-namespaces`, `--force`, `--grace-period`, `--all`, `--ignore-not-found`, `--dry-run[=mode]`, `--field-manager`, `--from-literal`, `--image`, `--tcp`, `--rule`, `--schedule`, etc.) and rejects unrecognized flags with exit 2.
2. **Manifest ingestion**: a YAML (and JSON) parser sufficient for typical K8s manifests (mappings, sequences, scalars, flow collections, block scalars, multi-doc `---`), turning file content into a generic object graph; missing file / parse failure → exit 1 with `Invalid`-bearing message. Must support `-f -` or repeated invocation is out of scope unless implied by argv shapes given.
3. **Kind resolution**: map manifest `kind:` or verb's TYPE positional (including plural/short aliases: `po`, `svc`, `cm`, `deploy`, `ds`, `sts`, `rs`, `ns`, `sa`, `pvc`, `cj`, `ing`, etc.) to canonical Kind + apiVersion/group + REST plural + namespaced-or-not, covering all 13 required kinds plus the extra "not required but must work via discovery" kinds (Role, RoleBinding, ClusterRole, ClusterRoleBinding, NetworkPolicy, LimitRange, ResourceQuota, PriorityClass, PodDisruptionBudget). An unknown kind for delete/describe → exit 1 with appropriate message (per "invalidkind" test cases); for other verbs behave sensibly (fail rather than crash).
4. **HTTP client to apiserver**: construct REST calls (GET/POST/PUT/PATCH/DELETE) against `{apiVersion}/namespaces/{ns}/{plural}/{name}` (or cluster-scoped path), using kubeconfig for host/CA/auth (cert, token, or exec-based auth as present in the sandboxed kubeconfig). Must load and honor TLS config from kubeconfig (CA data / client cert) — this is the most failure-prone plumbing piece.
5. **Per-verb business logic**:
   - `apply`: GET current; if 404 → POST create → print `created`; if exists → compute whether spec differs (or blindly PATCH via merge/strategic-merge/JSON-merge and compare resourceVersion / a returned diff) → PATCH → print `configured` or `unchanged`. Must be safe to call twice with identical input.
   - `create`: from `-f` manifest (fails on existing with 409→`AlreadyExists`), or from typed sub-forms (`create namespace NAME`, `create configmap/secret --from-literal=...`, `create deployment --image=`, `create service clusterip --tcp=`, `create ingress --rule=`, `create cronjob --image --schedule`). Secret values from `--from-literal` must be base64-encoded in `data`.
   - `delete`: resolve kind+name (or `--all`/`-f`), call DELETE, handle `--grace-period`, `--force`, `--ignore-not-found`, print quoted-name success line per removed object, exit 1+`NotFound` when target absent (unless `--ignore-not-found`), exit 2 when neither name nor `--all` given.
   - `describe`: GET (or LIST for bulk/selector) and render a multi-section textual view without mutating anything.
   - `get`: LIST or single GET; render table by default, and support `-o json/yaml/name/custom-columns/jsonpath/wide` output modes producing valid, parseable output for json/yaml at minimum.
   - `label`: PATCH `.metadata.labels` (merge patch) for the target, supporting `KEY=VALUE` and `KEY-` (remove) syntax, `--overwrite`.
   - `patch`: apply `--type merge|strategic|json` with `--patch`/`-p <json>` (or `--patch-file`) to the target object via PATCH.
   - `scale`: PATCH `.spec.replicas` for scalable kinds (Deployment, ReplicaSet, StatefulSet) via `--replicas=N`, optionally guarded by `--current-replicas`.
6. **Error normalization**: map apiserver HTTP status codes (404/409/422/400/403/etc.) to the exact substrings tests grep for (`NotFound`, `AlreadyExists`, `Invalid`) and route to exit 1; keep pure CLI-parsing failures on exit 2 with `invalid` in stderr.

## Solution space

Any implementation achieving the same observable contract is valid, including:
- **Language/tooling**: Go, Python (using the official `kubernetes` client or plain `requests`+PyYAML), Node, shell wrapping the real `kubectl` binary if present in the image (as long as it doesn't hardcode endpoints and honors `KUBECONFIG`), etc. Nothing in the task requires a hand-rolled YAML parser — using an existing YAML/JSON library or an existing Kubernetes client SDK is equally correct and arguably lower-risk than reimplementing parsing from scratch (as the reference diff does).
- **Thinnest valid approach**: if the sandbox actually ships a real `kubectl` binary, a trivial wrapper script that execs it with `KUBECONFIG` forwarded and translates exit codes/messages as needed would satisfy the contract; this is a legitimate alternative to a from-scratch client.
- **HTTP layer**: raw REST calls vs. a generated/official client library (e.g., Python `kubernetes` package, `client-go`) are equally valid; the reference's manual HTTP+manual YAML parser is just one route.
- **Apply idempotency check**: comparing manifests field-by-field before deciding created/configured/unchanged, vs. always issuing a server-side apply/PATCH and diffing the returned object's `resourceVersion`/generation to infer "unchanged" — both are acceptable as long as the printed word matches observed behavior (no-op on identical re-apply).
- **Discovery for non-required kinds**: can be done via a static table (as reference does) or by querying the apiserver's `/apis` discovery endpoints dynamically at runtime — both satisfy "handled via discovery API using the same conventions."
- **Output formats**: `-o custom-columns` / `-o jsonpath` need not be pixel-perfect implementations of kubectl's template engines; a reasonable best-effort renderer that doesn't crash and produces something plausible is acceptable since the spec only firmly requires json/yaml to be machine-parseable.

## Known pitfalls

- Conflating exit-code classes: usage/flag errors (exit 2) vs. semantic/API errors (exit 1) are tested precisely per verb; getting `--invalid-flag` to exit 1 instead of 2 (or vice versa) breaks tests.
- Forgetting `--ignore-not-found` short-circuits delete's normal 404→exit 1 behavior into exit 0.
- Treating `create` as idempotent (silently succeeding on duplicate) — must surface `AlreadyExists` and exit 1.
- Not distinguishing message shapes: `apply`/`create` use `<kind>/<name> <verb>`, but `delete` uses `<kind> "<name>" deleted` — mixing these fails string-matching tests.
- Ignoring namespace scoping rules for cluster-scoped kinds (e.g., sending a namespace path segment for `Namespace`/`ClusterRole` objects) causes spurious 404s.
- Case/alias handling: TYPE argument may be singular, plural, or short alias (`po`, `deploy`, `sts`); failing to normalize breaks `get`/`delete`/`describe`/`patch`/`scale`/`label` invocations.
- Silently accepting unknown flags instead of erroring with exit 2 (over-permissive parsing) breaks the negative-path tests just as much as under-permissive parsing.
- Not handling `-f -`/multi-document YAML or comments/quoting edge cases if hand-rolling a YAML parser — safer to use a real YAML library.
- Skipping TLS/auth setup from kubeconfig (assuming plaintext or default cert) will make every API call fail against the kwok apiserver.
- Not re-verifying state after mutating verbs (e.g., delete) — tests explicitly check `list_<kind>` no longer contains the resource and `read_<kind>` 404s afterward.
- Missing support for `create <kind> <name>` typed sub-forms (namespace, configmap/secret generic, deployment, service clusterip, ingress, cronjob) — these are explicitly enumerated argv shapes, not just `-f` forms.
- Mishandling `delete` with neither NAME nor `--all` — must be exit 2, not exit 1 or 0.

## Cheat surface

- Hardcoding fixed output strings for the small set of examples in the spec ("<pod-manifest>", "<resource>" placeholders) instead of implementing generic logic — will fail against the actual 390 hidden test manifests/names.
- Faking `get`/`describe`/`list` output from an in-process store instead of hitting the real apiserver would break the required create→get→patch→scale→delete consistency across independently-invoked subprocess calls (each invocation starts fresh, so no in-memory state persists between test steps — persistence must come from the real cluster).
- Always returning exit 0 / swallowing errors to "pass more tests" — the negative-path exit-code/stderr-substring assertions specifically target this.
- Implementing `apply` as unconditional `create` (ignoring existing resources) — breaks idempotency and the created/configured/unchanged distinction.
- Only supporting the kinds explicitly named in example argv strings while leaving the rest of the 13 required kinds unimplemented — the task explicitly says all 13 kinds must work across all verbs.
- Reporting success text without actually performing the mutation server-side (e.g., printing "created" but not persisting) — subsequent `get` in the same test will fail.

## Success criteria

- For every verb × every one of the 13 kinds (plus generic handling of the extra discovery kinds when referenced in manifests), the CLI produces correct exit codes and stdout/stderr shapes as enumerated in the spec's "Error cases observed" and "Behavior" sections.
- State mutations are durable and visible cross-invocation via the real apiserver: `apply`/`create` → visible in `get`; `delete` → absent from `get`/list and `read` returns 404; `patch`/`scale`/`label` → subsequent `get`/`describe` reflect the change.
- `apply` is idempotent (`unchanged` on identical re-apply, `configured` on changed re-apply, `created` on first apply); `create` is not idempotent (second call errors `AlreadyExists`, exit 1).
- Unknown/invalid flags always yield exit 2 with `invalid` in stderr; not-found/already-exists/invalid-manifest semantic failures yield exit 1 with the documented substring; `--ignore-not-found` overrides the not-found exit to 0.
- Namespace flag handling (`-n`/`--namespace`, default `default`) and cluster-scoped exceptions are respected across all verbs.
- The executable is a single file at `/workspace/submission/kubectl`, executable, and correctly reads `$KUBECONFIG` from the environment rather than any hardcoded endpoint.