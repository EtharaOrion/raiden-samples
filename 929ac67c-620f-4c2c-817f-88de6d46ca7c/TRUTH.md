# TRUTH: 929ac67c-620f-4c2c-817f-88de6d46ca7c

## Problem

Build a single executable `/workspace/submission/kubectl` that implements a *verb-first* subset of real kubectl (`apply`, `create`, `delete`, `describe`, `get`, `label`, `patch`, `scale`) against a live kwok-backed Kubernetes apiserver reachable via `KUBECONFIG`, covering 13 required kinds (ConfigMap, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, Pod, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet) plus best-effort support for auxiliary kinds (Role, RoleBinding, ClusterRole, ClusterRoleBinding, NetworkPolicy, LimitRange, ResourceQuota, PriorityClass, PodDisruptionBudget) via generic discovery/REST calls. The program is invoked as a subprocess per command; state must persist in the real cluster across invocations so create→get→patch→scale→delete chains behave consistently.

## Behavioral contract

- Dispatch strictly on `argv[1]` = verb; TYPE/NAME are positional after the verb (except `apply`/`create -f` which derive kind from manifest `kind:`).
- Must read `KUBECONFIG` from env, never hardcode cluster endpoints/certs.
- Exit codes are semantically meaningful and tested: `0` success; `1` for API-level failures (NotFound, AlreadyExists, Invalid, generic apiserver errors) and for missing-argument "usage" failures explicitly called out as exit 1 (e.g. bare `apply`, `create`, `delete`, `delete pod` with no name); `2` for argparse-style flag errors (`--invalid-flag`, `--bogus`, missing required positional combined with `--all` absent in delete).
- stderr must contain specific substrings depending on case: `Invalid`/`invalid`, `NotFound`/`not found`, `AlreadyExists`, `resource(s) were provided` for the delete-no-target case.
- stdout success messages must match real kubectl shape: `<kind>/<name> created`, `configured`, `unchanged` (apply), `<kind>/<name> created` (create), `<kind> "<name>" deleted` (delete), table output for `get`, human sections (`Name:`, `Namespace:`, `Status:`, `Labels:`, `Annotations:`, `Events:`) for `describe`.
- `apply` is idempotent (create-if-absent, patch-toward-desired-state if present, no-op diffing on unchanged spec); `create` is NOT idempotent — second create of same name/namespace/kind → exit 1 + `AlreadyExists`.
- All 8 verbs must be functional against all 13 required kinds; kind resolution happens via manifest `kind:` (apply/create -f) or the TYPE positional (get/delete/describe/patch/scale/label), including common short aliases (po, svc, cm, deploy, ds, sts, rs, ns, sa, pvc, ing).
- State consistency: after any mutating verb, subsequent `get`/`describe`/`read_<kind>` must reflect it immediately (no eventual-consistency assumptions beyond what the real apiserver gives); after `delete`, subsequent reads must 404.
- Unknown/invalid kind names must fail (exit 1, e.g. `describe invalidkind ...`, `delete invalidkind ...`) rather than silently succeeding or crashing.
- Namespace flag handling: `-n`/`--namespace` selects namespace; default is `default` when omitted; `-A`/`--all-namespaces` widens `get`/`describe` scope.
- `-o json`/`-o yaml` output for `get` must be genuinely parseable (valid JSON/YAML) reflecting the live object, not a canned string.
- `--dry-run` variants must not persist changes when set to `client`/non-`none` values that imply no mutation (at minimum must not break other tests; real client-side/server-side dry-run semantics apply if exercised).

## Solution decomposition

1. **Argv/flag parsing layer**: recognize verb, extract TYPE/NAME positionals vs. flags, distinguish long/short flag forms (`-f`/`--filename`, `-n`/`--namespace`, `-l`/`--selector`, `-A`/`--all-namespaces`, `-o`), and reject unrecognized flags with exit 2 while allowing declared-but-unused flags (e.g. `--force`, `--recursive`, `--wait`, `--show-events`) to be accepted as no-ops if not behaviorally required.
2. **Manifest ingestion**: read and parse YAML (or JSON) files given via `-f`/`--filename`; support multi-doc YAML if needed; extract `kind`, `metadata.name`, `metadata.namespace`, and full spec. Missing file / parse failure → exit 1 with `Invalid` in stderr (or exit 2 for pure flag-shape errors).
3. **Kind→REST mapping (discovery)**: map kind name/alias to API group/version/plural/namespaced-ness for all 13 required kinds plus auxiliary kinds, either via a static table or a runtime discovery-API call to the apiserver (either is valid, discovery must ultimately resolve group/version/resource path correctly).
4. **HTTP/client-go (or SDK) integration**: build a REST/K8s client that reads kubeconfig (cluster URL, CA, auth) and performs GET/LIST/POST/PUT/PATCH/DELETE against `/api/v1/...` or `/apis/<group>/<version>/...` namespaced or cluster-scoped paths.
5. **Per-verb logic**:
   - apply: read-if-exists → create or merge/patch → print created/configured/unchanged.
   - create: typed sub-forms (`create namespace NAME`, `create deployment NAME --image=`, `create service clusterip ...`, `create ingress ...`, `create job ...`, `create configmap/secret --from-literal=`) plus generic `-f` path; POST; 409 on conflict.
   - delete: single name, `--all`, `--all-namespaces`, `--ignore-not-found`, `--grace-period`, `-f` manifest-driven deletion; DELETE call(s); print one line per deleted object.
   - describe: read/list + human-readable renderer with required section headers per kind.
   - get: list/read + table renderer, plus `-o json/yaml/wide/name/custom-columns/jsonpath` output formats.
   - label: patch `.metadata.labels` (add/overwrite, `key-` to remove) via strategic-merge or JSON-merge patch.
   - patch: apply JSON/strategic-merge/JSON-merge patch body (`--type`, `-p`) to a named resource.
   - scale: PATCH `.spec.replicas` for scalable kinds (Deployment, StatefulSet, ReplicaSet — real kubectl also errors sensibly for non-scalable kinds like Pod).
6. **Output/error formatting layer**: centralize exit-code/stderr conventions so every verb's error paths match the substring/exit-code contract.

## Solution space

Many implementation strategies are equally valid:
- **Language/tooling**: Go with client-go, Go with a hand-rolled REST+YAML layer (as in the reference), Python with the official `kubernetes` client library, or any other language with an HTTP client — all acceptable as long as behavior matches.
- **YAML parsing**: use a real YAML library (`gopkg.in/yaml.v3`, PyYAML, `ruamel.yaml`) instead of a hand-rolled parser — strictly simpler and preferred over reference's custom parser, as long as it handles the manifest shapes used in tests (multi-doc, block/flow, literals).
- **Kind resolution**: static alias/kind table (as reference does) OR live discovery via `/apis` and `/apis/<group>/<version>` — both valid; discovery is more robust for the auxiliary "not required but nice" kinds.
- **Apply semantics**: could be implemented via server-side apply (`PATCH` with `Content-Type: application/apply-patch+yaml`, field manager) instead of read-then-diff-then-PUT/merge-patch — both are legitimate as long as create/configure/unchanged output and idempotency hold.
- **CLI framework**: could shell out to a vendored real `kubectl` binary if present in the runtime image (not prohibited by the spec, though the spec implies "from scratch"); could also delegate to `client-go`'s dynamic client instead of typed clients for uniform handling across all kinds.
- **Typed create sub-forms**: could be implemented as templated manifest construction feeding the same apply/create path, rather than separate code paths, as long as output/behavior matches.
- **Output formatting for get -o json/yaml**: can pass through the raw apiserver JSON/YAML representation directly (simplest, always spec-correct) rather than reconstructing objects manually.

## Known pitfalls

- Confusing exit code 1 vs 2: usage/flag errors (`--invalid-flag`, `--bogus`, unknown flags) must be 2; missing manifest/API errors must be 1; missing required positional combined with `--all` absent in `delete` must be 2 specifically.
- Treating `apply`/`create` verb-first dispatch as resource-first (`kubectl pods apply`) — explicitly disallowed by the spec.
- Making `create` idempotent like `apply` — must fail with `AlreadyExists` on duplicate.
- Missing the `<kind>/<name> unchanged` distinction on re-apply of identical spec (only checking created/configured).
- Forgetting to default namespace to `default` when `-n`/`--namespace` omitted, or mishandling cluster-scoped kinds (Namespace, ClusterRole, ClusterRoleBinding, PriorityClass) which must NOT be namespace-qualified.
- Not handling both `nonexistent-x.yaml` and `.yml` extensions and file-not-found vs malformed-YAML as distinct-but-both-exit-1 cases.
- Silently swallowing unknown kinds instead of erroring (`describe invalidkind`, `delete invalidkind` must exit 1).
- Hardcoding cluster endpoint/token instead of reading `KUBECONFIG` — breaks portability to the sandboxed kwok cluster.
- Case-sensitivity/alias gaps: not supporting short names (`po`, `svc`, `cm`, `ns`, `deploy`, etc.) that tests may use as TYPE.
- `describe namespace` omitting both `Status:` and `Labels:` headers — spec requires at least one.
- Not making `delete` idempotent-friendly with `--ignore-not-found` (must turn a would-be exit-1 NotFound into exit-0).
- Only partially implementing `scale`/`label`/`patch` for a subset of the 13 kinds — tests exercise all declared verb×kind combinations.
- Losing state between invocations by caching locally instead of hitting the real apiserver each time — verification is via server-side list/read calls (`list_<kind>`, `read_<kind>`), not by trusting local echoes.

## Cheat surface

- Printing hardcoded "created"/"deleted" strings without actually performing the mutating apiserver call — will fail state-invariant checks that call `list_<kind>`/`read_<kind>` afterward, and fail cross-verb sequences (create→get→patch→scale→delete).
- Faking `get -o json`/`-o yaml` output from static templates instead of returning the live object — will fail field-matching checks (names, replica counts after scale, labels after label/patch).
- Hardcoding exit codes per literal argv string rather than deriving them from real parse/API outcomes — likely to pass only the exact enumerated example commands and fail equivalent variants (different names/namespaces) the graders substitute in.
- Ignoring `-f`/manifest content and only supporting typed create sub-forms (or vice versa) — spec requires both paths to work across kinds.
- Skipping actual namespace-scoping and always operating in `default` — would break `-n kube-system`/`-n test-ns` test variants.
- Treating all auxiliary kinds (Role, NetworkPolicy, etc.) as unsupported/erroring — acceptable to be less polished but should not crash if a manifest of that kind is applied.

## Success criteria

- Binary exists at `/workspace/submission/kubectl`, executable, dispatches on `argv[1]` verb, works for all 8 verbs × 13 required kinds.
- Exit codes and stderr substrings match the contract for every enumerated error case (NotFound, AlreadyExists, Invalid/invalid, argparse-style invalid flag, missing resource args).
- Round-trip correctness: `apply`/`create` → resource visible via `get`/`describe`/list-equivalent; `patch`/`label` mutate correctly and are visible afterward; `scale` changes replica count and is reflected in `get`; `delete` removes the resource and subsequent reads 404.
- `apply` is idempotent (create/configured/unchanged transitions correct); `create` errors on duplicate.
- `get -o json`/`-o yaml` produce valid, parseable output reflecting real server state; table output for plain `get` includes expected columns.
- `describe` output contains required section headers and the resource name; never mutates state.
- Namespace flag (`-n`/`--namespace`/`-A`) and selector flags behave correctly across kinds.
- No hardcoded endpoints; correctly reads `KUBECONFIG` from environment and communicates with the sandboxed kwok apiserver for every operation.