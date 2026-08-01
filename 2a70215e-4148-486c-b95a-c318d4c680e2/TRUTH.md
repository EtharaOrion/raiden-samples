# TRUTH: 2a70215e-4148-486c-b95a-c318d4c680e2

## Problem

Build a single executable at `/workspace/submission/kubectl` that reimplements a verb-first subset of real `kubectl` (`apply`, `create`, `delete`, `describe`, `get`, `label`, `patch`, `scale`) against a live kwok-backed Kubernetes apiserver, reachable via the `KUBECONFIG` env var. The CLI must dispatch on `argv[1]` as the verb, then accept `[TYPE] [NAME] [flags...]` in whichever shape each verb naturally uses (manifest-driven via `-f` for apply/create, or `TYPE NAME` positional for get/delete/describe/patch/scale/label). It must correctly handle 13 required Kinds (ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, Pod, Secret, Service, ServiceAccount, StatefulSet) plus gracefully route a handful of auxiliary kinds (Role, RoleBinding, ClusterRole, ClusterRoleBinding, NetworkPolicy, LimitRange, ResourceQuota, PriorityClass, PodDisruptionBudget) through generic REST/discovery handling. State must be consistent across a create→get→patch→scale→delete lifecycle against the real cluster (no local caching/faking).

## Behavioral contract

- Invocation: `/workspace/submission/kubectl <verb> [TYPE] [NAME] [flags...]`, executable, no hard-coded API endpoints — must read `KUBECONFIG` from env (or default kubeconfig discovery) to build the REST/client config (host, CA, auth token/cert).
- Verb semantics must match real kubectl v1.31 closely enough for output shape and exit codes to be tested:
  - `apply`: create-if-absent else patch-toward-manifest (idempotent). stdout `<kind>/<name> created|configured|unchanged`. Missing/malformed file or apiserver validation failure → exit 1, stderr contains `Invalid`; unknown flag → exit 2, stderr contains `invalid`; no `-f` at all → exit 1.
  - `create`: create from `-f` manifest OR typed sub-forms (`create namespace NAME`, `create configmap/secret ... --from-literal=K=V` repeated, `create deployment NAME --image=`, `create service clusterip NAME --tcp=`, `create ingress NAME --rule=`, `create job/cronjob ... --image=/--schedule=`). NOT idempotent: existing resource → exit 1, stderr `AlreadyExists`. stdout `<kind>/<name> created`. Secret `--from-literal` values must be base64-encoded in `data`.
  - `delete`: `delete TYPE NAME [-n ns] [--all] [--force] [--grace-period N] [--ignore-not-found]`, or `delete -f manifest`. stdout `<kind> "<name>" deleted` per removed object. Missing target error → exit 1, stderr `NotFound`/`not found` (unless `--ignore-not-found`, then exit 0). Missing name and no `--all` → exit 2, stderr contains `invalid`/similar. Unknown kind → exit 1. Unknown flag → exit 2.
  - `describe`: read-only, multi-section human output containing at minimum the resource name and, for Namespace, a `Status:` or `Labels:` header. Nonexistent resource → exit 1 stderr `NotFound`. Unknown flag → exit 2. Missing type/name → exit 1.
  - `get`: table output by default (`NAME READY STATUS RESTARTS AGE` style for Pods, analogous per kind); `-o json|yaml` must produce parseable structured output; `-o name`, `-o wide`, `-o jsonpath=`, `-o custom-columns=` supported at least superficially. `-n/--namespace`, `-A/--all-namespaces`, `-l/--selector` filter appropriately. Nonexistent single resource → exit 1 stderr `NotFound`.
  - `label`: add/update/remove (`key-`) labels on a resource, `--overwrite` semantics respected; success prints `<kind>/<name> labeled`.
  - `patch`: apply a JSON/strategic-merge/merge patch via `--type` and `-p`/`--patch`, updates the object on the server; stdout `<kind>/<name> patched`.
  - `scale`: `--replicas=N` on Deployment/StatefulSet/ReplicaSet/(and similarly scalable kinds); stdout `<kind>/<name> scaled`.
- Cross-verb state consistency: objects created/applied are visible to subsequent `get`/`describe`/`patch`/`scale`/`delete` calls against the same real apiserver — no in-process-only state.
- Exit code conventions (must hold across verbs): `0` success, `1` runtime/API errors (NotFound, AlreadyExists, Invalid, generic failures), `2` CLI usage errors (unknown flags, missing required args recognized as argparse-style failures).
- Only implement flags actually enumerated per verb; do not invent nonexistent kubectl flags (e.g., no `--wait-for` on apply).

## Solution decomposition

1. **Kubeconfig/client bootstrap**: parse `KUBECONFIG`, extract cluster host + CA + user auth (token/cert/exec), build an HTTP(S) client (or use a generated/official Kubernetes client library) capable of calling the discovery and REST API of the apiserver.
2. **Kind registry / discovery**: map short/plural/singular names and `kind:` field values to (group, version, resource-plural, namespaced?) tuples for the 13 required kinds, and fall back to dynamic discovery (`/apis` , `/apis/<group>/<version>`) for the auxiliary kinds so `Role`, `NetworkPolicy`, etc. still work generically.
3. **Manifest ingestion**: a YAML (and JSON) parser sufficient to read `apiVersion/kind/metadata/spec` etc. from arbitrary test manifests, supporting multi-doc (`---`) files, flow and block collections, quoted scalars, comments.
4. **Verb argument parsing**: per-verb flag parsing that recognizes the documented flags, rejects unknown flags with exit 2, and rejects missing required positionals appropriately (some exit 1, some exit 2 per the tables above — this asymmetry is deliberate and must be preserved).
5. **REST operations layer**: generic `GET/POST/PUT/PATCH/DELETE` against `/api/v1/namespaces/{ns}/{plural}/{name}` or `/apis/{group}/{version}/...` forms, namespaced vs cluster-scoped routing, mapping HTTP status codes (404→NotFound, 409→AlreadyExists, 422/400→Invalid, etc.) to the required exit-code/stderr-substring contract.
6. **apply logic**: GET current object; if 404 → POST (create) → print `created`; if present → compute if manifest's spec differs from live spec (or just always PATCH/merge and compare pre/post) → PATCH and print `configured` or `unchanged` if no diff.
7. **create typed sub-forms**: implement generator functions building minimal valid manifests for `namespace`, `configmap`/`secret generic` (`--from-literal`), `deployment --image=`, `service clusterip --tcp=`, `ingress --rule=`, `job --image=`, `cronjob --image= --schedule=`, then POST them.
8. **get/describe formatting**: table renderer per kind (at least Pod-style columns) and JSON/YAML serialization for `-o` output; describe renderer with section headers.
9. **label/patch/scale**: fetch, mutate (labels map, JSON patch/merge-patch body, `.spec.replicas`), PUT/PATCH back, print confirmation line.
10. **Error/exit-code plumbing**: centralize so every branch that fails maps to the right exit code and stderr substring (`Invalid`, `invalid`, `NotFound`, `not found`, `AlreadyExists`).

## Solution space

Multiple implementation strategies are valid as long as behavior matches:

- **Language/tooling**: Go with hand-rolled YAML parser + net/http (as in reference), or Python using the official `kubernetes` client library (`ApiException.status` gives natural 404/409 mapping), or any other language with an HTTP client and a YAML/JSON library. Using an off-the-shelf YAML library (e.g. `gopkg.in/yaml.v3`, PyYAML) instead of a hand-written parser is equally valid and preferable for robustness.
- **Client transport**: using a generated Kubernetes client-go/python-client vs. raw REST calls constructed from parsed kubeconfig are both acceptable, provided TLS/auth are correctly wired from `KUBECONFIG`.
- **apply "unchanged" detection**: may be implemented via last-applied-config annotation diffing (like real kubectl), via deep-equal on spec fields, or by simply always issuing a merge-patch and detecting whether the server-returned object's resourceVersion changed — any approach that yields `unchanged` for exact re-apply and `configured` for spec changes is acceptable.
- **CLI argument parsing**: could use a real argparse/cobra/flag library configured to error on unknown flags (exit 2) or a custom parser; exact library choice is irrelevant as long as exit codes/stderr substrings match.
- **Discovery for auxiliary kinds**: could hardcode the known GVRs (as the reference does) or perform live discovery via `/apis` — both satisfy the requirement since the auxiliary kinds are not strictly required to be perfect, just handled via "the same conventions."
- **Output rendering**: table columns can be produced via manual string formatting or a tabwriter-style library; JSON/YAML output can reuse the parsed manifest structure or the live object returned by the API — exact field order is not asserted.
- Single monolithic binary vs. thin shell wrapper dispatching to per-verb scripts — both fine, as instructed ("any executable format works").

## Known pitfalls

- Treating this as resource-first (`kubectl pods apply`) instead of verb-first — spec explicitly says that shape does not exist and must not be relied upon or produced.
- Conflating exit codes 1 vs 2: usage/flag errors (unknown flag, missing required positional recognized by argparse) must be 2, not 1; runtime/API errors (NotFound, AlreadyExists, Invalid) must be 1, not 2. Several "missing argument" cases are deliberately 1 (e.g., `apply` alone, `create` alone, `delete pod` alone, `describe` alone) while others are 2 (e.g., `delete` with no name AND no `--all`) — this must be reproduced exactly as enumerated, not by a single blanket rule.
- Making `create` idempotent (must fail with `AlreadyExists` on duplicate, unlike `apply`).
- Forgetting to base64-encode `Secret` data values while leaving `ConfigMap` data as plain strings.
- Hard-coding the apiserver endpoint or bypassing `KUBECONFIG`, breaking portability across sandboxes.
- Not distinguishing namespaced vs cluster-scoped resources (e.g., `Namespace`, `ClusterRole`, `ClusterRoleBinding`, `PriorityClass`) — sending a namespace path segment for cluster-scoped kinds will 404/produce wrong routing.
- Fragile/incorrect hand-written YAML parsing that breaks on flow collections, multi-doc separators, comments, block scalars (`|`, `>`), or quoted strings — since arbitrary test manifests are supplied. If hand-rolling a parser (as reference does), it's easy to introduce edge-case bugs; using a real YAML library sidesteps this risk entirely.
- Wrong stdout shape: `apply`/`create`/`patch`/`scale`/`label` use `<kind>/<name> <verb-past-tense>`, but `delete` uses `<kind> "<name>" deleted` (quoted name, no slash) — mixing these up will fail string-matching tests.
- Not accepting both short (`pod`) and qualified (`pod.core`) kind fragments in delete output matching.
- Missing support for `--ignore-not-found` on delete (must convert a would-be exit-1 NotFound into exit-0).
- Case sensitivity/pluralization bugs in kind resolution (e.g., not accepting both `pod` and `pods`, `deploy`/`deployment`/`deployments`).
- Not keeping state consistent across verbs — e.g., caching objects in-process instead of always hitting the real apiserver, which breaks cross-process test sequences (create in one invocation, get in a subsequent invocation).
- Inventing flags not in spec (e.g. `--wait-for` on apply) — while harmless if unused, don't let their absence break argument parsing of documented flags.

## Cheat surface

- A submission that stores state only in a local file/in-memory instead of talking to the real kwok apiserver would pass single-process tests but fail any test that invokes the CLI as multiple separate subprocess calls expecting server-side persistence (create then get in a fresh process) — this is the primary "fake it" temptation to guard against; TRUTH requires real API calls via `KUBECONFIG`.
- Hardcoding output strings for specific test resource names instead of general logic (e.g., special-casing `nonexistent-*` names to return 404) would be a giveaway of pattern matching against fixture generation rather than genuine NotFound handling — genuine implementations derive 404 behavior from real absence on the server.
- Blanket `sys.exit(1)`/`sys.exit(2)` without regard to whether the failure was a usage error vs an API error would spuriously pass some cases and fail others; a solution should not special-case per literal test string but implement the general rule (usage parsing failures → 2, API/runtime failures → 1).
- Always printing `created` regardless of prior existence (skipping the actual GET-before-write check) for `apply` would fail the idempotency/`unchanged`/`configured` requirements.
- Ignoring `--namespace`/`-n` and always operating on `default` would pass single-namespace tests but fail multi-namespace ones (`kube-system`, `test-ns`).

## Success criteria

- Binary exists at `/workspace/submission/kubectl`, is executable, and dispatches correctly on all 8 verbs for all 13 required kinds (plus reasonable handling of the 9 auxiliary kinds).
- For each verb, argv shapes listed in the spec's "observed argv patterns" produce the documented exit code and, where specified, stderr substring (`Invalid`, `invalid`, `NotFound`, `not found`, `AlreadyExists`) or stdout shape (`<kind>/<name> created|configured|unchanged|patched|scaled|labeled`, `<kind> "<name>" deleted`).
- End-to-end lifecycle works against the real kwok cluster: `create`/`apply` → visible via `get`/`describe` → mutable via `patch`/`scale`/`label` → removable via `delete`, with `read_<kind>` after delete raising 404, all persisting correctly across separate process invocations since state lives server-side.
- Re-applying an identical manifest is a no-op (`unchanged`); applying a modified manifest updates the live object's spec and reports `configured`.
- `-o json`/`-o yaml` output on `get` is valid, parseable JSON/YAML reflecting the live object.
- Namespace scoping (`-n`, `--namespace`, `-A/--all-namespaces`) works correctly, including cluster-scoped kinds bypassing namespace routing.
- No hard-coded cluster endpoint; the program only obtains connection info via `KUBECONFIG` (env-driven), so it functions against whatever sandboxed kwok endpoint is configured at test time.