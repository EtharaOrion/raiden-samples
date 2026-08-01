# TRUTH: 96078a99-3cc6-47bb-b089-12869caa0821

## Problem

Build a single executable, `/workspace/submission/kubectl`, that mimics real `kubectl` v1.31 verb-first CLI semantics against a live sandboxed kwok cluster (a kwok-backed apiserver reachable via `KUBECONFIG` in the environment). The binary must dispatch on `argv[1]` — one of `apply`, `create`, `delete`, `describe`, `get`, `label`, `patch`, `scale` — and support the 13 required kinds (ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, Pod, ReplicaSet, Secret, Service, ServiceAccount), plus best-effort support for several extra kinds (Role, RoleBinding, ClusterRole, ClusterRoleBinding, NetworkPolicy, LimitRange, ResourceQuota, PriorityClass, PodDisruptionBudget) via generic discovery-style REST calls. The program must talk to the real apiserver referenced by `KUBECONFIG` — no faking/mocking of state — and keep cross-verb state consistent (create→get→patch→scale→delete must chain correctly).

## Behavioral contract

- Invocation shape is strictly `kubectl VERB [TYPE] [NAME] [flags...]`. There is no reversed `<resource> <verb>` form.
- Verb dispatch must cover all 8 verbs for all 13 kinds (docs also mention `label`/`patch`/`scale` verbs and typed `create <kind> <name> --flags` shortcuts referenced later in the full spec, truncated here but implied by "covering 13 kinds").
- Manifests are supplied via `-f/--filename` (file path, YAML or JSON); kind is read from the manifest's `kind:` field for `apply`/`create -f`. For `get/delete/describe/patch/scale/label`, kind comes from the TYPE positional (accepting common aliases/plurals: `po`, `pods`, `deploy`, `svc`, etc.), name from the NAME positional.
- Exit codes are meaningful and tested:
  - `0` success.
  - `1` for apiserver-level failures (NotFound, AlreadyExists, Invalid, generic errors) and usage failures like missing required file/manifest, missing verb args.
  - `2` for CLI/argument-parsing errors (unknown flags, missing positional args in argparse style).
- Stderr must contain specific substrings for graders to grep: `NotFound`/`not found`, `AlreadyExists`, `Invalid`/`invalid`, `resource(s) were provided` for missing-name-and-no---all delete.
- Stdout success messages follow real kubectl phrasing: `<kind>/<name> created`, `configured`, `unchanged` (apply); `<kind>/<name> created` (create); `<kind> "<name>" deleted` (delete, short or qualified kind fragment both acceptable).
- `apply` is idempotent (create-if-absent, patch-if-present, no-op if spec unchanged); `create` is NOT idempotent and fails with AlreadyExists on duplicate.
- `get -o json` / `-o yaml` must emit machine-parseable output; default output is a human table with kind-appropriate columns (e.g., pods: NAME READY STATUS RESTARTS AGE).
- `describe` never mutates state; output must contain the resource name and stable section headers (`Name:`, `Namespace:`, `Status:`/`Labels:` for namespaces, `Annotations:`, `Events:` where relevant).
- State must be truly persisted in the backend: after `create`/`apply`, a subsequent `get`/`describe`/`read_<kind>` call (via any tool, not just this same binary invocation) must see the object; after `delete`, it must be gone (404).
- `--namespace`/`-n` selects namespace; default is `default` namespace when omitted (except for cluster-scoped kinds like Namespace, ClusterRole, ClusterRoleBinding, PriorityClass).
- Unknown/invalid kind strings for `get/delete/describe` etc. cause failure (exit 1 per the spec's observed cases, since it manifests as a lookup/API failure rather than a pure flag-parse failure — note: spec explicitly lists `delete invalidkind ... -> exit 1` and `describe invalidkind ... -> exit 1`).
- Unknown flags (`--invalid-flag`, `--bogus`) must be rejected with exit `2`, not silently ignored.

## Solution decomposition

1. **CLI/argument parsing layer**: split argv into verb, optional TYPE, optional NAME, and flags (both `--flag value`, `--flag=value`, and boolean flags). Recognize a fixed allow-list of flags per verb; reject unrecognized flags with exit 2. Distinguish positional-missing errors (exit 2) from resource-not-found errors (exit 1).
2. **Manifest ingestion**: a YAML (and ideally JSON) parser capable enough to read Kubernetes manifests — nested maps/lists, scalars, multi-doc `---` separated files, flow-style `{}`/`[]`, block scalars `|`/`>`. Extract `apiVersion`, `kind`, `metadata.name`, `metadata.namespace`, and full body for PUT/POST payloads.
3. **Kind resolution table**: map kind name / alias / plural CLI token → canonical Kind, apiVersion group, plural REST resource name, and namespaced/cluster-scoped flag, for all 13 required kinds plus the extra permitted kinds.
4. **HTTP client to the apiserver**: read `KUBECONFIG` env var, parse kubeconfig (server URL, CA cert, client cert/key or token) to build a TLS HTTP client, and issue REST calls (GET/POST/PUT/PATCH/DELETE) against `/api/v1/...` or `/apis/<group>/<version>/...` (namespaced vs cluster-scoped paths), mirroring `list_<kind>`, `read_<kind>`, `create_<kind>`, `patch_<kind>`, `delete_<kind>` semantics referenced by the spec.
5. **Verb implementations**:
   - `apply`: read manifest → try GET existing → if 404 POST create ("created"); else compute diff/PUT or strategic-merge PATCH ("configured" or "unchanged" if no-op).
   - `create`: manifest-based POST, or typed shortcuts (`create namespace NAME`, `create configmap/secret NAME --from-literal=K=V`, `create deployment NAME --image=IMG`, `create service clusterip ...`, `create ingress ...`, `create job ...`, `create cronjob ...`) that synthesize a minimal valid manifest client-side then POST. Must fail AlreadyExists on duplicate.
   - `get`: LIST or single GET, render table or `-o json/yaml` (and best-effort `-o name/wide/custom-columns/jsonpath`).
   - `delete`: single DELETE or bulk (`--all`, `--all-namespaces`), honor `--ignore-not-found`, `--grace-period`, `--force`.
   - `describe`: GET/LIST then format human-readable sections; read-only.
   - `patch`: apply a JSON/strategic-merge patch body (`-p`/`--patch` or `--type`) via PATCH verb.
   - `scale`: PATCH `spec.replicas` (Deployment/ReplicaSet/StatefulSet/etc.) via `--replicas=N`.
   - `label`: PATCH `metadata.labels` (add/overwrite/remove with `-`) via `--overwrite` semantics.
6. **Error/exit-code mapping**: translate HTTP status codes (404→NotFound/exit1, 409→AlreadyExists/exit1, 422/400→Invalid/exit1) into the exact stderr substrings required, and keep pure CLI-usage failures (bad flags, missing positional) as exit 2 with `invalid`/`resource(s) were provided` substrings.

## Solution space

Any language/toolchain available in the image is acceptable provided it produces a single executable at the fixed path. Valid alternative approaches include:

- **Python** using the official `kubernetes` client library (`client.CoreV1Api`, `AppsV1Api`, etc.) with `config.load_kube_config()` reading `KUBECONFIG`, and `argparse`/manual arg parsing for verb dispatch. This is likely the most idiomatic route given the spec's explicit mention of `read_<kind>`/`list_<kind>`/`ApiException.status` semantics (these are literal `kubernetes` Python client names).
- **Go** using `client-go` (`k8s.io/client-go/kubernetes`, dynamic client for generic kinds) instead of hand-rolled YAML parsing and raw HTTP/TLS — heavier dependency but far less error-prone than reimplementing a YAML parser and kubeconfig/TLS stack from scratch (as the reference diff did).
- **Shell wrapper** that shells out to a vendored/prebuilt real `kubectl` binary if present in the image, translating only the flags/verbs the spec cares about — acceptable since "any executable format works."
- **Node.js** with `@kubernetes/client-node` and `js-yaml`.
- Hand-rolled REST client (as in the reference) directly against the apiserver using the kubeconfig's server/CA/cert data, without any Kubernetes SDK — valid but requires careful reimplementation of YAML parsing, TLS client-cert auth, and REST path construction (as seen in the diff). This is the highest-effort/highest-risk route and is not preferred over using a client library, but is not disallowed.

All of these are equally valid as long as they satisfy the observable behavioral contract (exit codes, stdout phrasing, stderr substrings, state consistency across verbs).

## Known pitfalls

- **Reinventing YAML parsing from scratch** (as the reference diff does) is extremely bug-prone — flow collections, block scalars, quoting, comments-inside-strings, multi-document separators all have edge cases. Using a real YAML library (`gopkg.in/yaml.v3`, PyYAML, js-yaml) is far safer than a hand-rolled parser.
- **Confusing exit-code buckets**: usage/flag errors must be 2, resource/API errors must be 1 — mixing these up breaks many test assertions (e.g., unknown flag `--invalid-flag` → 2, unknown kind → 1, missing positional with no `--all` → 2).
- **Kind alias table incompleteness**: forgetting plural/singular/short forms (`po`, `deploy`, `cm`, `sa`, `pvc`, `ns`, `ds`, `rs`, `cj`, `ing`) causes valid TYPE tokens to be misrouted or rejected.
- **Group/version routing**: apps resources live under `/apis/apps/v1`, batch under `/apis/batch/v1`, networking under `/apis/networking.k8s.io/v1`, core resources under `/api/v1` (no group segment) — getting this wrong 404s everything for a whole kind.
- **Namespace defaulting**: forgetting that Namespace (and other cluster-scoped kinds) must NOT be namespaced in the REST path, while everything else defaults to `default` namespace when `-n` is omitted.
- **`create` idempotency confusion**: treating `create` like `apply` (silently succeeding on duplicate) fails the explicit `AlreadyExists`/exit-1 requirement.
- **`apply` no-op detection**: always PUTting/PATCHing on every apply changes `resourceVersion`/timestamps and can cause spurious "configured" instead of "unchanged" — need a meaningful spec-diff check (or rely on server-side apply / strategic merge patch producing no diff).
- **Secret base64 encoding**: `create secret ... --from-literal` values must be base64-encoded into `.data`, not left as plaintext under `.stringData` only (or if using stringData, must still round-trip correctly with `get -o json` expectations).
- **Delete of Namespace vs. namespaced resources**: `--all`/`--all-namespaces` bulk delete needs a LIST-then-DELETE loop with per-object stdout lines, not a single message.
- **KUBECONFIG must be read at runtime**, not hard-coded; TLS/cert-based auth for kwok apiserver must be handled correctly if not using a client library that already does this.
- **Stdout phrasing exactness**: `<kind>/<name> created|configured|unchanged` and `<kind> "<name>" deleted` are substring-matched — deviating punctuation/casing (e.g., lowercase kind vs. Kind) may fail graders that check exact kind naming conventions (kubectl typically lowercases the kind in these messages, e.g. `pod/foo created`, `pod "foo" deleted`).
- **Flag allow-listing**: must explicitly reject truly unknown flags (`--invalid-flag`, `--bogus`) rather than accepting all flags permissively, since permissive parsing breaks the exit-2 cases.

## Cheat surface

- Hard-coding fixed manifests/objects in memory instead of hitting the real apiserver would pass naive `get`-after-`create` checks in isolation but fail any check that inspects state via an independent tool/process reading the same kwok cluster, or persistence across multiple CLI invocations sharing state through etcd.
- Faking `AlreadyExists`/`NotFound` purely from a local name-cache instead of real server responses would break under `--all-namespaces`, bulk deletes, or when other tooling (test harness) creates/deletes objects directly against the apiserver between CLI invocations.
- Returning exit 0 always and hoping graders only check stdout substrings — the spec explicitly enumerates exit-code expectations per error case, so exit codes are checked, not just message text.
- Ignoring `--dry-run` entirely and always mutating state — for `--dry-run=server/client` (mentioned for apply) a compliant implementation shouldn't necessarily persist; a shortcut of always creating regardless of dry-run could fail related dry-run assertions if present in the hidden suite.
- Printing a plausible-looking `describe` output without actually calling the apiserver (i.e., fabricating fields) — would fail on real data-dependent assertions (labels, replica counts, etc. reflecting actual object state).
- Treating all kinds identically with one generic REST path guess without a real discovery/kind table — works for the 13 required kinds if the table is correct, but silently mishandling group/version for even one kind will fail its entire kind-specific test block.

## Success criteria

- The binary at `/workspace/submission/kubectl` is executable and dispatches correctly on all 8 verbs for all 13 required kinds (plus graceful handling of the 9 extra "not required but may appear" kinds via generic REST calls).
- All documented argv shapes (flags, positional combos, error cases) produce the exact exit codes (0, 1, or 2) specified, with stderr containing the required substrings (`NotFound`, `AlreadyExists`, `Invalid`/`invalid`, `resource(s) were provided`) and stdout containing the required phrasing (`created`/`configured`/`unchanged`/`deleted`) where applicable.
- Cross-verb state consistency holds against the real kwok-backed apiserver: `create`/`apply` → visible via `get`/`describe`/direct API read; `patch`/`scale`/`label` → visible mutation of the same object; `delete` → object subsequently 404s via any client.
- `apply` is idempotent (same manifest reapplied is a no-op on spec, reports `unchanged`); `create` is strictly non-idempotent (second call errors `AlreadyExists`).
- `get -o json`/`-o yaml` output is parseable by a standard JSON/YAML parser and contains the expected `kind`/`metadata.name`/`spec` fields.
- No hard-coded cluster endpoints — `KUBECONFIG` env var is honored at runtime for connecting to whatever sandboxed kwok cluster the test harness provisions.
- Passes the shipped test suite (387 tests) covering the cross product of verbs, kinds, flags, and error conditions described above.