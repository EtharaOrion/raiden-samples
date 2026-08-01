# TRUTH: 44ea6633-dbad-4c53-8cf4-c788272eaaf6

## Problem

Build a single executable, `/workspace/submission/kubectl`, that implements a verb-first subset of `kubectl` (`apply`, `create`, `delete`, `describe`, `get`, `label`, `patch`, `scale`) against a real (kwok-backed) Kubernetes apiserver reachable via `KUBECONFIG`, covering 13 required kinds (ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet) plus best-effort handling of several bonus kinds via generic REST/discovery. The program is invoked as a subprocess with argv shaped like real kubectl (`kubectl VERB [TYPE] [NAME] [flags...]`), must dispatch on `argv[1]`, and must keep cluster state consistent across a sequence of verb invocations (create → get → patch → scale → delete, etc.) since each invocation is a fresh process with no persistent local state — all state lives in the apiserver.

## Behavioral contract

- Single executable at the exact path, executable bit set; any language/toolchain is fine.
- Must read `KUBECONFIG` from the environment (never hardcode cluster endpoints/certs) and talk to the real apiserver over its REST API (raw HTTP+TLS/client-cert auth, or a generated/vendored client library — both acceptable) since kwok simulates a real control plane.
- Dispatch on the verb; TYPE positional resolves kind either from a manifest's `kind:` field (`apply`/`create -f`) or from the CLI positional (aliases like `cm`, `deploy`, `svc`, `ns`, plural/singular forms must resolve to the correct Kind/group/version/resource-plural for every one of the 13 required kinds, using Kubernetes API conventions — core `v1` for ConfigMap/Namespace/PVC/Secret/Service/ServiceAccount, `apps/v1` for Deployment/DaemonSet/StatefulSet/ReplicaSet, `batch/v1` for Job/CronJob, `networking.k8s.io/v1` for Ingress).
- Exit codes are semantically meaningful and tested directly:
  - `0` success.
  - `1` for runtime/API failures (not found, already exists, invalid manifest content, missing manifest file, no verb given, delete without name/`--all`... wait, that last one is `2`).
  - `2` for CLI/argparse-style usage errors (unknown flags, missing required args like a delete target).
- stderr must contain specific substrings for the harness to match: `NotFound` (or `not found`), `AlreadyExists`, `Invalid`/`invalid`, `resource(s) were provided` (delete usage error).
- stdout success messages must match real kubectl's shape: `<kind>/<name> created`, `configured`, `unchanged` (apply); `<kind>/<name> created` (create); `<kind> "<name>" deleted` (delete, short or fully-qualified kind name both acceptable).
- State changes must be real and observable: after `apply`/`create`, the object appears in `get`/list and in a direct read by name+namespace; after `delete`, it's gone (404 on read).
- `apply` is idempotent — re-applying an unchanged manifest reports `unchanged`/`configured` and does not error; `create` is NOT idempotent — repeat create of same name/namespace fails with `AlreadyExists`.
- `get -o json`/`-o yaml` must emit real, machine-parseable structured output reflecting apiserver object state (not fabricated/static text).
- `describe` never mutates state; must include `Name:` and, for Namespace specifically, either `Status:` or `Labels:`.
- Namespace flag handling: `-n`/`--namespace` equally supported everywhere; default namespace is `default` when omitted.
- Unknown/invalid flags anywhere → exit `2` with stderr containing `invalid`.
- Unknown kind (`invalidkind`) → exit `1` (not a `2`, since it's resolved at "API resource" level, not argument-parsing level) with appropriate error content.
- `label`, `patch`, `scale` verbs (not covered in the truncated instruction text but declared in metadata) must exist and operate correctly: `label` sets/overwrites labels via a patch call and echoes a `<kind>/<name> labeled` style message; `patch` applies a JSON/strategic-merge patch body; `scale` updates `.spec.replicas` for scalable kinds (Deployment, ReplicaSet, StatefulSet) and reports `<kind>/<name> scaled` — all following the same exit-code/message-shape conventions as the other verbs.

## Solution decomposition

1. **Kubeconfig/transport layer**: parse `KUBECONFIG` YAML, extract server URL, CA data, client cert/key (or token), and build an HTTP(S) client capable of talking to the apiserver's REST API for core and named API groups.
2. **Kind resolution table**: map every alias/plural/singular string a user might type to (Kind, Group, Version, resource-plural, namespaced?) for the 13 required kinds, plus best-effort discovery fallback for extra kinds (Role, RoleBinding, ClusterRole, ClusterRoleBinding, NetworkPolicy, LimitRange, ResourceQuota, PriorityClass, PodDisruptionBudget).
3. **YAML/manifest parsing**: read `-f`/`--filename` file(s), support single or multi-doc (`---`) manifests, extract `kind`, `metadata.name`, `metadata.namespace` and full object for PUT/POST bodies. Must fail gracefully (exit 1, `Invalid`) on malformed YAML or missing file.
4. **Argument parsing per verb**: build a generic flag/positional parser recognizing all documented flags per verb (`-f/--filename`, `-n/--namespace`, `-o`, `-l/--selector`, `-A/--all-namespaces`, `--dry-run`, `--force`, `--grace-period`, `--all`, `--ignore-not-found`, `--from-literal`, `--image`, `--tcp`, `--rule`, `--schedule`, etc.) and rejecting anything not recognized with exit 2.
5. **Verb implementations** built on top of REST CRUD against the resolved GVR+namespace+name:
   - `apply`: GET existing → if 404 POST create ("created"); else PUT/PATCH toward desired spec, diff-detect no-op ("unchanged") vs change ("configured").
   - `create`: from `-f` manifest OR typed generator subcommands (`create namespace NAME`, `create configmap/secret NAME --from-literal=...`, `create deployment NAME --image=...`, `create service clusterip ...`, `create ingress ...`, `create job/cronjob ...`) → POST; 409 on existing.
   - `delete`: resolve kind+name(s) (positional, `--all`, or `-f` manifest) → DELETE; format `<kind> "<name>" deleted`; handle `--ignore-not-found`, `--grace-period`, `--force` (mapped to grace-period=0), usage error if no name/`--all`.
   - `describe`: GET/LIST → human-readable formatted sections (Name/Namespace/Labels/Annotations/kind-specific fields/Events).
   - `get`: LIST or GET → table by default, `-o json/yaml` structured dump, `-A` cross-namespace, `-l` label-selector filtering.
   - `label`: GET → merge/overwrite `metadata.labels` → PATCH → `<kind>/<name> labeled`.
   - `patch`: GET/validate → send provided patch body (`--patch`/`-p` or `--type`) via PATCH → `<kind>/<name> patched`.
   - `scale`: GET → set `spec.replicas` from `--replicas=N` → PATCH/PUT → `<kind>/<name> scaled`; error for non-scalable kinds or missing object.
6. **Error/exit-code mapping**: central place turning HTTP status (404/409/422/400) and CLI parse failures into the exact exit codes and stderr substrings specified.
7. **Output formatting**: consistent success-message strings and table/JSON/YAML serializers.

## Solution space

Multiple implementation strategies are equally valid as long as behavior matches:

- **Raw HTTP REST client** (any language) hand-rolling GVR paths and JSON bodies, as in the reference (Go, no k8s client-go, using a hand-written YAML parser) — valid.
- **Official generated client libraries** (Python `kubernetes` client, Go `client-go`, JS `@kubernetes/client-node`) using their typed CRUD calls (`create_namespaced_config_map`, `list_namespaced_deployment`, etc.) — equally valid and likely simpler; the spec's mention of `read_<kind>`/`list_<kind>`/`ApiException` conventions reflects this style directly.
- **Shelling out to a vendored real `kubectl` binary** if present in the runtime image and just being a thin argv-forwarding wrapper — valid IF it satisfies flag/exit-code/message requirements (note: real kubectl message shapes already match, so this is a legitimate low-risk route provided the binary works against the sandboxed kwok kubeconfig).
- **YAML parsing**: may use a full YAML library (`gopkg.in/yaml.v3`, PyYAML, `js-yaml`) instead of hand-rolling a parser — strongly preferred over reinventing YAML if the language has one; hand-rolling (as reference does) is unnecessary but not wrong.
- **Idempotency detection for `apply`**: may compare desired vs. live spec via deep-equality, JSON diff, or unconditionally PATCH and infer "unchanged" from a no-op response; any approach that yields correct created/configured/unchanged classification is fine.
- **Generator subcommands** (`create deployment --image=`, `create service clusterip --tcp=`, `create ingress --rule=`, `create job/cronjob`) can be built by constructing the equivalent manifest object internally and reusing the same create path, or via direct API payload construction — decomposition choice is free.
- **Kind-to-GVR mapping**: static table (as reference) or dynamic discovery via `/apis` and `/api` endpoints — both fine; discovery is actually required/expected for the non-required bonus kinds.

## Known pitfalls

- Forgetting that `kubectl <resource> <verb>` does NOT exist — must dispatch strictly on `argv[1]` as the verb, not the resource.
- Confusing exit code 1 vs 2: usage/flag-parsing errors (unknown flag, missing positional args) are `2`; runtime/API errors (not found, already exists, bad manifest) are `1`. Mixing these up breaks many tests at once (e.g., `delete invalidkind X` is `1`, not `2`, because kind resolution is a runtime lookup, not a parse error).
- Missing `--ignore-not-found` short-circuit before the NotFound→exit-1 path.
- Not supporting both `-n` and `--namespace`, or both `-f` and `--filename`.
- Case/pluralization mistakes in kind alias resolution (e.g., `configmaps` vs `configmap` vs `cm`) causing GVR lookup failures.
- Namespace defaulting: forgetting `default` when `-n` omitted, especially for `apply -f`/`create -f` where the manifest itself may specify `metadata.namespace` — precedence between flag and manifest field must be handled consistently (flag should generally win, matching real kubectl).
- `apply` re-run producing `configured` when nothing changed (broken idempotency), or crashing on first-apply due to missing "no such object" 404 handling.
- Secrets: forgetting to base64-encode `--from-literal` values for `Secret` (unlike ConfigMap, which stores plain strings).
- `delete` with no name and no `--all` must be a `2` usage error, not silently doing nothing or crashing.
- Table output for `get` needs to be non-empty/parseable enough for substring assertions without over-fitting to exact spacing.
- `-o json`/`-o yaml` must reflect the *live* apiserver object, not a re-serialization of the input manifest — tests may check server-populated fields.
- TLS/auth setup bugs (not reading client-cert/CA data correctly from kubeconfig) causing all requests to fail — must be handled generically for whatever auth method the kwok sandbox kubeconfig uses.
- Race/consistency: since each verb call is a new process, must not cache resourceVersion assumptions between calls in ways that break repeat operations (e.g., PATCH failures due to stale resourceVersion mismatches should be retried or avoided).

## Cheat surface

- Hardcoding fixed output strings (`"configmap/foo created"`) without actually calling the apiserver — would fail get/read-back state-invariant checks and cross-verb sequences.
- Faking `get -o json` by echoing back the input manifest instead of the live object — detectable since tests read server state after mutations (labels/patches/scale).
- Ignoring `KUBECONFIG` and hardcoding an endpoint — breaks entirely in the sandboxed grading environment.
- Returning exit 0 always / swallowing errors to dodge negative test cases — directly tested via explicit exit-code assertions on `nonexistent-*` names and invalid flags.
- Implementing only `apply -f`/`create -f` manifest paths and skipping typed generators (`create namespace NAME`, `create deployment --image=`) — explicitly listed as observed argv patterns and tested.
- Only handling a couple of the 13 kinds and silently no-op'ing/erroring generically on the rest — the task explicitly requires full verb×kind coverage.
- Using `--force`/`--grace-period` as no-ops without actually affecting delete semantics where tested behaviorally (should at least not break the basic delete success path).

## Success criteria

- For every verb × every one of the 13 required kinds, the corresponding argv shapes in the instruction (positive and error cases) produce the documented exit code and stdout/stderr content.
- State consistency across a create→get→patch→scale→delete sequence, verified via successive independent process invocations reading real apiserver state (no in-memory-only state).
- All ~384 shipped tests pass, covering: verb dispatch, flag parsing (valid/invalid), namespace handling (`-n`/`--namespace`/default), output formats (`-o json/yaml`), idempotency of `apply` vs non-idempotency of `create`, correct error substrings/exit codes for not-found/already-exists/invalid/usage errors, and `describe`'s required section headers.
- Binary is present, executable, and runs standalone as `/workspace/submission/kubectl <verb> ...` with no other setup.