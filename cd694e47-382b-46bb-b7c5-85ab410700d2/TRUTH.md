# TRUTH: cd694e47-382b-46bb-b7c5-85ab410700d2

## Problem

Build a single executable, `/workspace/submission/kubectl`, that implements a verb-first subset of the real `kubectl` CLI against a live kwok-backed Kubernetes apiserver (endpoint/credentials discovered via `KUBECONFIG` from the environment). The program must dispatch on `argv[1]` (the verb: `apply`, `create`, `delete`, `describe`, `get`, `label`, `patch`, `scale`) and support all 14 required kinds (ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, Pod, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet), entering either via a manifest's `kind:` field or via a TYPE positional. State must be genuinely persisted through the real apiserver so that create→get→patch→scale→delete sequences are consistent, and CLI behavior (stdout shape, exit codes, stderr substrings) must match real kubectl closely enough to satisfy substring/exit-code assertions.

## Behavioral contract

- Invocation: `kubectl <verb> [TYPE] [NAME] [flags...]`. No resource-first subcommand form is accepted/expected.
- Exit codes are semantically meaningful and tested precisely:
  - `0`: success (including `--ignore-not-found` on missing resource for `delete`).
  - `1`: semantic/API errors — not found (`NotFound`/`not found`), already exists (`AlreadyExists`), invalid manifest (`Invalid`), missing required file, unrecognized kind, no verb given, missing required positional args for `describe`/`get pod <name>` etc.
  - `2`: CLI/argument parsing errors — unknown flags (`--invalid-flag`, `--bogus`), missing name AND missing `--all` for delete, malformed flag usage. Stderr must contain `invalid` (lowercase) for these argparse-style errors.
- Stdout success-message shapes (must be matched by substring, not exact byte match beyond what's specified):
  - `apply`: `<kind>/<name> created` | `configured` | `unchanged`.
  - `create`: `<kind>/<name> created`.
  - `delete`: `<kind> "<name>" deleted` (note: space + quoted name, NOT slash form). `<kind>` fragment may be short or dotted-group-qualified; both acceptable.
  - `get`: tabular output with header row per kind (e.g. `NAME  READY  STATUS  RESTARTS  AGE` for pods) OR machine-parseable `-o json`/`-o yaml`/`-o jsonpath`/`-o custom-columns` output.
  - `describe`: multi-section human-readable text containing the resource name and stable section headers (`Name:`, `Namespace:`, `Status:`/`Labels:` for Namespace, `Annotations:`, `Events:` where semantically applicable).
- State invariants across verbs: after create/apply, the object is visible via list/read on that kind+namespace+name; after delete, it is absent and reads 404.
- `apply` is idempotent (create-or-patch, unchanged on repeat); `create` is NOT idempotent (second create → `AlreadyExists`, exit 1).
- Flags must be read from environment `KUBECONFIG`; no hardcoded cluster endpoints.
- All 14 kinds must work end to end for every verb that's meaningful for that kind (get/delete/describe/patch/scale/label operate via TYPE positional dispatch; apply/create operate primarily via manifest `kind:` field, plus a few typed short-forms like `create namespace <name>`, `create deployment ... --image=`, `create service clusterip ...`, `create ingress ...`, `create job ...`, `create cronjob ...`).
- Non-required-but-referenced kinds (Role, RoleBinding, ClusterRole, ClusterRoleBinding, NetworkPolicy, LimitRange, ResourceQuota, PriorityClass, PodDisruptionBudget) must not crash the CLI — they should be routable via the apiserver discovery/generic-REST path using the same conventions.

## Solution decomposition

1. **Argument parsing / dispatch layer**: parse `argv[1]` as verb; branch to per-verb handler. Within each verb, parse remaining positionals (TYPE, NAME) and flags (`-f/--filename`, `-n/--namespace`, `-o/--output`, `-l/--selector`, `-A/--all-namespaces`, `--force`, `--grace-period`, `--all`, `--ignore-not-found`, `--from-literal`, `--image`, `--tcp`, `--rule`, `--schedule`, `--dry-run`, `--field-manager`, `--show-events`, etc.). Unknown flags not in the observed set → exit 2 with `invalid` in stderr.
2. **YAML/manifest parsing**: read `-f` file, parse into a generic object (map[string]any or dict), extract `kind`, `apiVersion`, `metadata.name`, `metadata.namespace`, and `spec`/`data`. Must handle multi-doc YAML (`---`) at least tolerably, though not stress-tested per the shown patterns. Missing file → exit 1 stderr `Invalid`/error message; malformed YAML → exit 1.
3. **Kind resolution / API routing table**: map short names, plurals, and kind names (case variants) to the correct REST resource: group, version, plural, namespaced-or-cluster-scoped. This table must cover the 14 required kinds plus the auxiliary kinds referenced in manifests, ideally driven through discovery for extensibility.
4. **HTTP/REST client against the apiserver**: construct requests using the kubeconfig (cluster URL, CA cert, client cert/token) pointed to by `KUBECONFIG` — either hand-rolled HTTP client or an idiomatic Kubernetes client library (e.g., Python `kubernetes` package, Go `client-go`, JS `@kubernetes/client-node`). Perform GET/LIST/POST/PATCH/PUT/DELETE against `/api/v1/...` or `/apis/<group>/<version>/...` (namespaced vs cluster paths).
5. **Per-verb semantics**:
   - `apply`: GET current object; if 404 → POST create, print `created`; if found → compute whether spec differs (server-side or client-side merge/patch) → PATCH, print `configured`; if patch results in no diff → print `unchanged`.
   - `create`: from `-f` → POST; from typed shorthand (`create namespace NAME`, `create configmap NAME --from-literal=...`, `create secret generic NAME --from-literal=...` with base64 encoding, `create deployment/service/ingress/job/cronjob ...` generator forms) → build manifest object then POST. On 409 conflict from apiserver → surface `AlreadyExists`, exit 1.
   - `delete`: resolve TYPE+NAME (or `-f` manifest, or `--all`) → DELETE; print one `<kind> "<name>" deleted` line per object; handle `--ignore-not-found`, `--grace-period`, `--force`; missing name and missing `--all` → exit 2.
   - `describe`: GET/LIST object(s), format human-readable sections; never mutate.
   - `get`: LIST/GET, render table by default or structured output per `-o`.
   - `label`: fetch object, merge/overwrite labels map (supporting `key=value` add and `key-` remove semantics as in real kubectl, if exercised), PATCH/PUT back.
   - `patch`: apply JSON/strategic-merge patch body (`--type`, `-p`) to the named object via PATCH verb.
   - `scale`: update `spec.replicas` (Deployment/ReplicaSet/StatefulSet) via PATCH/subresource, given `--replicas=N`.
6. **Error normalization**: map apiserver HTTP status codes to expected reason strings/exit codes (404→NotFound/exit1, 409→AlreadyExists/exit1, 422/400→Invalid/exit1, generic argparse issues→exit2 with `invalid`).
7. **Build/packaging**: produce a single executable at the exact path, `chmod +x`, no reliance on network resources beyond the sandboxed cluster.

## Solution space

Any language/toolchain available in the runtime image is acceptable, not just Go:

- **Go** compiled binary (as in the reference) using either hand-written HTTP+kubeconfig parsing or `client-go`/`k8s.io/apimachinery`.
- **Python** script (shebang `#!/usr/bin/env python3`) using the official `kubernetes` client library, which handles kubeconfig loading, TLS, and typed API calls (`CoreV1Api`, `AppsV1Api`, `BatchV1Api`, `NetworkingV1Api`, etc.) — likely the most idiomatic route given the spec's repeated references to `read_<kind>`/`list_<kind>`/`ApiException`.
- **Node.js/TypeScript** using `@kubernetes/client-node`.
- A thin wrapper that shells out to a vendored real `kubectl` binary if present in the image, translating/validating flags — acceptable as long as output/exit-code contracts are met and no hardcoded endpoints are used (kubeconfig env var must still be respected, which real kubectl does natively).
- A hand-rolled YAML parser (as the reference does) vs. using a YAML library — either is fine; using a library (`gopkg.in/yaml.v3`, PyYAML, `js-yaml`) is strictly simpler and equally valid, since the reference's custom parser is only one path.
- Server-side apply (`PATCH` with `application/apply-patch+yaml` + fieldManager) vs. client-side GET-then-diff-then-PATCH/PUT for `apply` idempotency — both satisfy the "created/configured/unchanged" contract as long as behavior is correct.
- Discovery-driven kind→REST-path resolution (querying `/apis` at runtime) vs. a static table of known group/version/plural mappings — both valid; discovery is more robust for the non-required auxiliary kinds but a reasonably complete static table (as shown) is sufficient since the auxiliary kind list is finite and given in the spec.
- Typed sub-form generators (`create deployment --image=`, `create service clusterip --tcp=`, `create ingress --rule=`, `create job --image=`, `create cronjob --schedule=`) can be implemented as direct object construction rather than shelling to any generator logic.

## Known pitfalls

- Using resource-first dispatch (`kubectl pods apply`) instead of verb-first — explicitly stated as not supported; must not build that shape.
- Conflating `apply`'s `<kind>/<name> created` output shape with `delete`'s `<kind> "<name>" deleted` shape — these are different formats and both are asserted.
- Making `create` idempotent like `apply` (silently succeeding on duplicate) — must instead surface `AlreadyExists` and exit 1.
- Missing the `--ignore-not-found` short-circuit on `delete`, which is the one case where deleting a nonexistent resource must exit `0` rather than `1`.
- Incorrect exit-code categorization: confusing "unknown/invalid flag" (exit 2) with "resource not found" or "no manifest" (exit 1). The spec is explicit and tested per-case.
- Not lowercasing the "NotFound"/"AlreadyExists"/"Invalid" reason substrings consistently — stderr matching is substring-based but case matters per verb (`describe`/`get`/`create` expect capitalized `NotFound`; `delete` accepts either `NotFound` or lowercase `not found`).
- Forgetting cluster-scoped vs. namespaced resource routing (e.g., `Namespace`, `ClusterRole`, `ClusterRoleBinding`, `PriorityClass` have no namespace) — sending a namespaced request for these breaks apply/create/delete.
- Hardcoding the apiserver URL/certs instead of reading `KUBECONFIG` — breaks portability to the sandboxed kwok cluster.
- Treating `--invalid-flag`/`--bogus` as ignorable no-ops instead of failing — tests specifically assert exit 2 for unrecognized flags.
- Not handling `-f`/`--filename` file-not-found distinctly from malformed-YAML distinctly from apiserver-rejected-manifest — all must land on exit 1 with appropriate `Invalid` messaging (or exit 2 only for missing required arguments, not missing files).
- Only implementing a subset of the 14 kinds (e.g., skipping CronJob/DaemonSet/Ingress/StatefulSet) — task explicitly requires full coverage across all 14 for every applicable verb.
- Poor handling of the missing-positional case (`delete pod`, `describe pod`, `get pod <name>` variants) — must fail predictably (exit 1 or 2 as specified per verb) rather than panicking or reading a nonsensical arg as the name.
- Not tracking `--grace-period`/`--force` distinctly — semantically these affect deletion timing but tests likely only check exit codes/success message, so gross mishandling (crashing on unknown numeric flag) is the real risk, not deep grace-period simulation.

## Cheat surface

- A solution that merely prints plausible-looking success text without ever calling the real apiserver would fail the state-invariant checks (subsequent `get`/`read_<kind>` must reflect the mutation), so faking output alone is not viable — but a shim that keeps its own local JSON file as "state" instead of talking to the sandboxed kwok cluster could pass output-shape assertions while failing any external verification that inspects the actual cluster; graders should confirm objects are visible via independent apiserver queries, not just via the CLI's own subsequent invocations.
- Risk of overfitting to the literal example flag values/placeholders shown in argv patterns (e.g., only handling the exact `-n default` string) rather than genuinely parsing `-n <namespace>` generically — would pass the shown cases but fail equivalent variations.
- Risk of hardcoding expected exit codes per literal command string rather than implementing the underlying rule (e.g., pattern-matching on `nonexistent-*` substrings in the name) — a naive "if name contains 'nonexistent' return 1" implementation could pass example-derived tests without real NotFound-detection logic; this must be checked against genuinely-created-then-deleted resources too.
- Declaring support for all 14 kinds in a routing table but only wiring real CRUD logic for Pod/Deployment/Service and stubbing the rest to always return canned success — would fail get/describe roundtrip checks for the other 11 kinds.
- Skipping real idempotency logic in `apply` (always printing "configured" or always "created") — must genuinely differ behavior based on prior existence and diff status.

## Success criteria

- Binary exists at `/workspace/submission/kubectl`, is executable, and dispatches correctly on all 8 verbs via `argv[1]`.
- For each of the 14 required kinds, `create`/`apply` followed by `get`/`describe` returns the created object with matching name/namespace; `patch`, `scale` (where applicable), and `label` correctly mutate the persisted object as observed by a subsequent `get`; `delete` removes it and a subsequent `get`/`describe` returns exit 1 NotFound.
- Exit codes match the specified table exactly for all documented error cases (invalid flags → 2, not-found/already-exists/invalid-manifest/missing-verb → 1, `--ignore-not-found` on missing → 0).
- stdout messages match the required substrings/shapes (`created`/`configured`/`unchanged` for apply, `created` for create, `<kind> "<name>" deleted` for delete, table/JSON/YAML for get, section headers for describe).
- `apply` re-run on an unchanged manifest is a no-op (`unchanged`) and does not error; re-run after a spec change reports `configured` and the new spec is visible via get.
- `create` on a pre-existing resource fails with `AlreadyExists`/exit 1, never silently succeeds.
- No hardcoded cluster endpoints; `KUBECONFIG` env var is respected, so the same binary works against the sandboxed kwok cluster provided at test time.
- Auxiliary (non-required) kinds referenced in manifests do not crash the tool even if not fully exercised by the required-verb matrix.