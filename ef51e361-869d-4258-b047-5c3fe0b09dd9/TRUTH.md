# TRUTH: ef51e361-869d-4258-b047-5c3fe0b09dd9

## Problem

Build a single executable, `/workspace/submission/kubectl`, that implements a verb-first CLI mimicking real `kubectl` v1.31 for 8 verbs (`apply`, `create`, `delete`, `describe`, `get`, `label`, `patch`, `scale`) across 13 required Kubernetes kinds (CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, Pod, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet), talking to a real (kwok-backed) apiserver reachable via `KUBECONFIG`. Dispatch is `argv[1]` = verb, never `<resource> <verb>`. The tool must behave like real kubectl closely enough to pass ~386 behavioral tests spanning success paths, error paths, exit codes, stdout/stderr shape, and state consistency across a create→get→patch→scale→delete lifecycle.

## Behavioral contract

- Entry point `/workspace/submission/kubectl` must be executable and accept `<verb> [TYPE] [NAME] [flags...]` as a subprocess (any language/toolchain, any implementation strategy — raw HTTP to apiserver, generated client, kubectl-wrapping, etc., as long as it's built from scratch per the task's constraints).
- Must read `KUBECONFIG` from env, never hardcode cluster endpoints/credentials.
- Every verb must work against every one of the 13 declared kinds; kind is resolved either from a manifest's `kind:` field (apply/create -f) or from the TYPE positional (get/delete/describe/patch/scale/label), including common short aliases (po, svc, deploy, ns, etc.) and plural/singular forms.
- Non-required kinds (Role, RoleBinding, ClusterRole, ClusterRoleBinding, NetworkPolicy, LimitRange, ResourceQuota, PriorityClass, PodDisruptionBudget) must also be dispatchable using the same generic conventions (likely via discovery/dynamic REST rather than hardcoded per-kind logic).
- Exit codes: `0` success; `1` for apiserver-level errors (NotFound, AlreadyExists, Invalid, missing manifest file, etc.) with matching substrings in stderr (`NotFound`, `AlreadyExists`, `Invalid`, or lowercase variants); `2` for CLI/argument-parsing errors (unknown flags, missing required args) with `invalid`/usage text in stderr.
- Stdout success messages must match real kubectl shape: `<kind>/<name> created`, `configured`, `unchanged` (apply); `<kind>/<name> created` (create); `<kind> "<name>" deleted` (delete); table output for `get`; human-readable sectioned output for `describe` (must include `Name:`, and for Namespace additionally `Status:` or `Labels:`).
- State must be consistent and real across verbs: after `create`/`apply`, the object must be visible via `get`/`list`/`read`; after `delete`, it must be gone (404 on read); `apply` must be idempotent (create-or-patch, unchanged on identical re-apply); `create` must NOT be idempotent (second create → `AlreadyExists`).
- `--dry-run`, `-o json/yaml/wide/name/custom-columns/jsonpath`, `-n/--namespace`, `-A/--all-namespaces`, `-l/--selector`, `--field-manager`, `--force`, `--grace-period`, `--ignore-not-found`, `--all`, `--from-literal`, `--show-events`, etc. must be recognized (not necessarily every semantic nuance implemented in full fidelity, but observed argv shapes in the spec must not error out unless explicitly listed as an error case).
- Unknown/invalid flags not in the observed set must produce exit 2 usage errors, not crashes or exit 1.

## Solution decomposition

1. **Argument parsing / verb dispatch** — top-level switch on argv[1]; per-verb flag parser distinguishing known flags (accept) vs unknown (`--invalid-flag`/`--bogus` → exit 2) vs missing positionals (exit 1 or 2 per spec table).
2. **Kind resolution table** — map of kind name/alias → {group, version, plural resource name, namespaced bool} for all 13 required kinds plus the 9 auxiliary kinds, used to build REST paths generically (`/api/v1/namespaces/{ns}/{plural}` or `/apis/{group}/{version}/...`).
3. **Kubeconfig/HTTP client** — parse KUBECONFIG (cluster server URL, CA cert, client cert/key or token) and build an authenticated HTTP client (TLS certs, or bearer token) to reach the apiserver directly, OR wrap a generated/off-the-shelf Kubernetes client library configured from KUBECONFIG.
4. **Manifest parsing (YAML/JSON)** — for `-f`/`--filename`, load and parse into a generic object tree, extract `kind`, `metadata.name`, `metadata.namespace`, and body for PUT/POST.
5. **Verb implementations:**
   - `apply`: GET existing → if 404 POST create ("created"); else compare/PATCH (merge or JSON-merge-patch) → "configured" or "unchanged" if PATCH is no-op.
   - `create`: POST only; 409 on conflict; typed sub-forms (`create namespace NAME`, `create deployment NAME --image=`, `create service clusterip`, `create secret ... --from-literal`, `create job`, `create cronjob`, `create ingress`) synthesize a manifest object then POST.
   - `delete`: DELETE by name (or list+delete-all for `--all`), print per-object confirmation, handle `--grace-period`, `--force`, `--ignore-not-found`.
   - `describe`: GET (or LIST for bulk/selector) → format human-readable sections.
   - `get`: LIST or GET → render table or `-o` structured output.
   - `label`: GET → merge/remove labels via `metadata.labels` → PATCH/PUT.
   - `patch`: apply JSON/strategic merge patch body via PATCH.
   - `scale`: GET → set `spec.replicas` → PATCH/PUT the scale subresource or full object.
6. **Error mapping** — apiserver HTTP status → stderr reason string + exit code, per the table (404→NotFound/1, 409→AlreadyExists/1, 422/400→Invalid/1, argparse failures→invalid/2).
7. **Output formatting** — table renderer (NAME, READY/STATUS-ish columns per kind), JSON/YAML serializer, describe section formatter.

## Solution space

Multiple valid implementation routes exist; none should be penalized relative to others:

- **Language/toolchain**: Go (as in reference), Python (using `kubernetes` client lib configured via `KUBECONFIG`), Node, Rust, shell wrapping `curl` + `jq`, etc. — anything executable at the given path.
- **Kubernetes access layer**: hand-rolled REST/HTTP calls against the apiserver (parsing kubeconfig manually), an official generated client library (client-go, python-kubernetes, client-node), or even shelling out to a vendored real `kubectl` binary if present in the runtime image and reconfigured to use `KUBECONFIG` — as long as behavior/output/exit codes match the contract and no endpoint is hardcoded.
- **YAML parsing**: hand-written recursive-descent YAML subset parser (as reference does), or a full YAML library if available in the chosen language's toolchain.
- **Apply idempotency strategy**: client-side diff-and-PATCH, strategic merge patch, JSON merge patch, or server-side apply (`--dry-run=server`/field-manager semantics) — any approach that yields `created`/`configured`/`unchanged` correctly.
- **Dynamic/generic dispatch vs. hardcoded per-kind branches**: either a fully generic kind table + dynamic REST client (reference's approach) or explicit per-kind functions duplicated 13× — both acceptable as long as all kinds work uniformly.
- **Typed `create` sub-forms** (`create deployment --image=`, `create service clusterip`, etc.) can be implemented via manual manifest construction or by delegating to shared "build object" helpers; exact JSON produced isn't pinned, only that the resulting object is retrievable and correct.
- **Output formatting** for `-o custom-columns=`/`-o jsonpath=` need only be plausible/parseable — tests substring-match rather than pin exact table formatting.

## Known pitfalls

- Implementing verb-first dispatch incorrectly as resource-first (`kubectl pods apply`) — explicitly disallowed.
- Conflating exit code 1 (apiserver/domain errors) with exit code 2 (CLI usage errors) — tests assert exact codes per case (e.g., missing manifest file = 1, unknown flag = 2, missing positional name+no `--all` on delete = 2).
- Missing `NotFound`/`AlreadyExists`/`Invalid`/`invalid` substrings in stderr — tests substring-match on these exact tokens (case matters for some, case-insensitive fallback allowed for NotFound/"not found").
- Making `create` idempotent (should fail with AlreadyExists on repeat) vs. `apply` which must be idempotent — swapping these semantics is a common bug.
- Not supporting all kind aliases/plurals/short names (`po`, `deploy`, `ns`, `svc`, etc.) — TYPE positional resolution must be alias-aware.
- Hardcoding the apiserver URL instead of reading `KUBECONFIG` — breaks portability to the sandboxed kwok cluster.
- Only handling the 13 required kinds and erroring on Role/RoleBinding/etc. — these auxiliary kinds must still route through generic discovery-based logic.
- YAML edge cases: multi-document files (`---`), block scalars (`|`, `>`), flow-style maps/lists (`{}`/`[]`), quoted strings, comments — a naive line-splitter can silently corrupt manifests especially for Secret `data`/multiline configs.
- Forgetting `chmod +x` on the produced artifact.
- `describe namespace` specifically must include `Status:` or `Labels:` header — a generic describe formatter that only handles workload kinds may miss this.
- Not handling `--dry-run=server` vs `client` vs `none` distinctly enough to avoid mutating state when `client`/`server` is requested (server dry-run should still validate via apiserver but not persist).
- Secret `--from-literal` values must be base64-encoded before being placed into `data`.
- Scale must target `spec.replicas` consistently for Deployment/StatefulSet/ReplicaSet (kinds without a meaningful replicas field, like Pod/Service, should fail sensibly rather than crash).

## Cheat surface

- A solution that only implements a handful of the 13 kinds (e.g., just Pod/Deployment) and stubs/errors on the rest would fail the broad kind-coverage tests — this must not be rewarded as "mostly working."
- A solution that hardcodes fixed stdout strings without actually calling the apiserver (i.e., faking `created`/`deleted` without real state mutation) would fail the get-after-create / read-after-delete state-invariant checks — mere string-matching on stdout without real backend calls is not sufficient and should be caught by lifecycle sequence tests.
- A solution that always exits 0 or always exits 1 regardless of case would fail the exit-code matrix; graders must check exact codes per scenario, not just "some failure occurred."
- A solution that shells out to a genuine pre-installed `kubectl` binary already present in the image is a gray area: since the task says "no source code, only this specification" and asks to build the CLI, delegating entirely to a real kubectl already on PATH substantially bypasses the intended build effort. If a real kubectl is available and simply invoked with KUBECONFIG passed through, it may still be judged by the grader purely on behavior — this is only acceptable if the task environment doesn't clearly prohibit it; treat heavy reliance on an already-present full kubectl as a risk area to flag, not necessarily disqualifying by itself, but a solution reimplementing the logic is unambiguously safe.
- Claiming success without exercising `--dry-run` correctly (e.g., persisting despite `--dry-run=client`) would be caught by tests checking the resource does NOT appear after a client-side dry-run apply/create.

## Success criteria

- Binary exists at `/workspace/submission/kubectl`, is executable, and dispatches on `argv[1]` as the verb for all 8 verbs.
- All 13 required kinds (plus the 9 auxiliary kinds via generic handling) are reachable through every verb's TYPE positional or manifest `kind:` field.
- Exit codes and stderr substrings match the documented per-scenario table for apply/create/delete/describe/get (and analogous patterns for label/patch/scale/truncated sections) across success and error cases.
- State transitions are real and observable: create/apply → visible in get/list/read; delete → absent from get/list, 404 on read; apply is idempotent (created→configured→unchanged sequence); create is not idempotent (AlreadyExists on repeat).
- stdout formats match kubectl conventions closely enough for substring assertions (`<kind>/<name> created|configured|unchanged`, `<kind> "<name>" deleted`, describe section headers, get table headers).
- `-o json`/`-o yaml` outputs are valid, parseable, and contain the expected object data.
- No hardcoded cluster endpoints; `KUBECONFIG` env var is honored for all apiserver communication.