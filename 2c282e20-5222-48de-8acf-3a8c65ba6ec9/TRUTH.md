# TRUTH: 2c282e20-5222-48de-8acf-3a8c65ba6ec9

## Problem

Build a single executable, `/workspace/submission/kubectl`, that implements a **verb-first** subset of `kubectl` (`apply`, `create`, `delete`, `describe`, `get`, `label`, `patch`, `scale`) against a real kwok-backed Kubernetes apiserver reachable via `KUBECONFIG`. It must correctly dispatch on `argv[1]` as the verb, support 13 required kinds (ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, Pod, ReplicaSet, Secret, ServiceAccount, StatefulSet), gracefully degrade to discovery-driven handling for a handful of "bonus" kinds (Role, RoleBinding, ClusterRole, ClusterRoleBinding, NetworkPolicy, LimitRange, ResourceQuota, PriorityClass, PodDisruptionBudget), and maintain state consistency across a create→get→patch→scale→delete lifecycle. Correctness is judged purely by observable behavior — stdout shape, stderr content, exit codes, and actual apiserver state — not by any particular implementation technology.

## Behavioral contract

- Invocation: `kubectl <verb> [TYPE] [NAME] [flags...]`. No resource-first form exists.
- Talks to the real apiserver at the endpoint from `$KUBECONFIG` (never hard-coded); reads certs/tokens from that kubeconfig.
- **apply**: create-or-patch by manifest, idempotent. First success → `<kind>/<name> created`; unchanged re-apply → `<kind>/<name> unchanged`; changed re-apply → `<kind>/<name> configured`. Missing file / bad YAML / apiserver-rejected manifest → exit 1 stderr `Invalid`; unknown flag → exit 2 stderr `invalid`; no `-f` at all → exit 1.
- **create**: create-only (fails `AlreadyExists`, exit 1, on duplicate), supports `-f <manifest>` and typed sub-forms (`create namespace NAME`, `create configmap/secret ... --from-literal=K=V`, `create deployment/job/cronjob/ingress ...` generators). Success → `<kind>/<name> created`. Same error-code rules as apply for bad/missing file and bad flags.
- **delete**: removes by TYPE+NAME (or `-f`, or `--all`), prints `<kind> "<name>" deleted` per object, subsequent `get`/`read` must 404. Nonexistent target → exit 1 stderr `NotFound`/`not found`, unless `--ignore-not-found` (then exit 0). Missing NAME and no `--all` → exit 2, stderr containing `invalid`/`resource(s) were provided`. Unknown kind → exit 1. Unknown flag → exit 2.
- **describe**: read-only, human-readable multi-section output containing the resource name and (for Namespace) a `Status:` or `Labels:` header; other kinds should include analogous headers where meaningful. Nonexistent resource → exit 1 `NotFound`. Unknown flag → exit 2.
- **get**: list/read table output (or `-o json/yaml/name/custom-columns/jsonpath/wide`), respecting `-n`/`--namespace`/`-A`/`--all-namespaces`/`-l`/`--selector`. Nonexistent object or namespace → exit 1 `NotFound`/`not found`. Unknown flag → exit 2.
- **label / patch / scale**: mutate an existing resource (label add/overwrite/remove with `KEY-`; JSON/strategic/merge patch application; replica-count scaling on scalable kinds) and persist changes visible to a subsequent `get`. Failure modes mirror the others (NotFound → exit 1, bad flags → exit 2).
- Cross-verb state consistency: an object created/applied by one verb invocation must be visible, mutable, and deletable by later invocations in the same test sequence — no local caching that diverges from server state.
- Exit code convention used throughout: **0** success, **1** semantic/API errors (NotFound, AlreadyExists, Invalid, general failure incl. missing manifest or missing verb args), **2** CLI usage/flag-parsing errors (invalid flag, missing required positional per argparse-style behavior).
- stderr message conventions: must contain the substrings named in the spec (case as specified: `NotFound`, `AlreadyExists`, `Invalid`, `invalid`, `not found`) — exact framing beyond that is not pinned.

## Solution decomposition

1. **Kubeconfig/client bootstrap**: parse `$KUBECONFIG` (cluster CA/server URL, user cert/token), build an HTTP(S) client (or use a Kubernetes client library) capable of REST calls against the discovered apiserver.
2. **Kind registry**: map friendly type names/aliases (`po`, `pods`, `deploy`, …) to canonical Kind, apiVersion/group, and REST plural, for all 13 required kinds plus the bonus discovery-only kinds. Namespaced vs cluster-scoped must be tracked (e.g., Namespace, ClusterRole are cluster-scoped).
3. **Argument parser**: verb-first dispatch on `argv[1]`; per-verb flag sets including short/long aliases (`-f/--filename`, `-n/--namespace`, `-o/--output`, `-l/--selector`, `-A/--all-namespaces`); unknown-flag detection must yield exit 2; missing-required-positional detection must yield exit 2 for delete's no-name/no-all case, but exit 1 for bare `apply`/`create`/`describe`/`get` with no args (per stated cases).
4. **Manifest loader**: YAML (and effectively JSON, since JSON is valid YAML) parser producing a generic document tree; must support multi-doc separated by `---`, comments, flow and block collections, quoted scalars — good enough to round-trip real k8s manifests. Malformed input must be detected and reported as an error path (exit 1 `Invalid` or exit 2 depending on cause).
5. **CRUD operations** per verb, translating to REST verbs against `/api/v1/namespaces/{ns}/{plural}/{name}` or `/apis/{group}/{version}/...` — GET/LIST, POST (create), PUT or PATCH (apply update / patch / scale / label), DELETE. Apply semantics require a read-then-diff-then-create-or-patch flow (or server-side apply if supported) to get created/configured/unchanged right.
6. **Typed generators** for `create namespace/configmap/secret/deployment/job/cronjob/ingress ...` building the appropriate object body without a manifest file.
7. **Output formatters**: default table view per kind for `get`, JSON/YAML/name/custom-columns/jsonpath serialization, and the section-based `describe` renderer.
8. **Error normalization**: map apiserver HTTP status → the exit code + substring conventions above.

## Solution space

Many implementation choices are equally valid as long as behavior matches:

- **Language/tooling**: any language with a shebang script or compiled binary is fine — Go with hand-rolled YAML parsing and raw HTTP (as in the reference) is only one route. Using Python + the official `kubernetes` client library, or a Go/Rust k8s client-go binding, or shelling out to a vendored real `kubectl`/`client-go` binary, are all acceptable if final behavior matches.
- **YAML parsing**: using a full third-party YAML library (`gopkg.in/yaml.v3`, PyYAML, `js-yaml`, etc.) instead of a hand-rolled parser is preferred/simpler and equally correct.
- **Apply implementation**: could use server-side apply (`PATCH` with `application/apply-patch+yaml` and `field-manager`), or client-side get+create/replace, or read+merge-patch — any strategy that yields correct created/configured/unchanged semantics and idempotency is acceptable.
- **Kind/alias table**: could be generated dynamically from the apiserver's discovery API (`/api`, `/apis`) instead of a hard-coded table — this is actually required/expected for the "bonus" kinds (Role, RoleBinding, etc.) per the instructions, and is an equally valid (arguably more robust) approach for the 13 required kinds too.
- **Output**: table formatting logic can be minimal (just enough columns to look like kubectl) — exact column layout isn't graded, only presence of name/status-ish info and machine-parseability of `-o json/yaml`.
- **Wrapping real kubectl**: since the task says "any executable/idiomatic client library," a solution that is a thin wrapper script invoking a vendored real `kubectl` binary configured via `$KUBECONFIG` would also satisfy the contract, provided flag/exit-code shaping matches spec where real kubectl might differ (e.g., custom argparse-error codes).

## Known pitfalls

- Confusing exit code 1 vs 2: usage/flag errors (unknown flag, delete with no name/no `--all`) must be 2; semantic/API errors and "verb called with no args at all" must be 1 — mixing these up fails many test cases at once.
- Not distinguishing `create` (fails on duplicate) from `apply` (idempotent) — reusing one code path for both without an existence check breaks `create`'s `AlreadyExists` requirement.
- Getting the apply tri-state wrong: must correctly report `unchanged` when the resource already matches (not always `configured`), which requires a real diff, not just always PATCH+"configured".
- Cluster-scoped vs namespaced kind confusion (e.g., applying `-n` to Namespace/ClusterRole resources) causing wrong REST paths.
- Case/alias handling: TYPE positionals may arrive as singular, plural, or short alias (`po`, `pods`, `Pod`) and must all resolve to the same kind.
- YAML edge cases: multi-document files, flow-style maps/lists, literal/folded block scalars, comments — a naive line-splitter can silently mis-parse manifests and produce false "Invalid" errors or wrong object bodies.
- Not surfacing the required substrings in stderr exactly as specified (`NotFound`, `AlreadyExists`, `Invalid`, `not found`) — tests substring-match these, so paraphrasing breaks them.
- Treating `--from-literal` values for `Secret` as plaintext instead of base64-encoding them (apiserver requires base64 for Secret data).
- Ignoring `--dry-run` variants, causing side effects when a dry-run was requested (if exercised) — though spec's error-case list focuses more on file/flag handling.
- State-caching bugs: printing success without actually persisting via the apiserver (or reading from a stale local cache) breaks the get-after-apply / read-after-create invariants explicitly required.
- Hard-coding the apiserver endpoint instead of reading `KUBECONFIG` from env — breaks portability across sandboxed clusters.
- Forgetting `chmod +x` on the produced executable.

## Cheat surface

- A solution that only prints canned success messages ("<kind>/<name> created") without ever calling the apiserver would fail the explicit follow-up `get`/`read_<kind>` state checks — graders chain verbs, so faking output alone is insufficient.
- A solution that always exits 0 or always uses one exit code for all failures would fail the many explicit exit-code assertions (0/1/2 distinctions) baked into the error-case tables.
- Hard-coding responses for the specific example resource names shown in the spec (`<resource>`, `nonexistent-...`) rather than genuinely parsing argv/manifests would fail on the hidden test suite's different names/namespaces.
- Implementing only a subset of the 13 kinds (e.g., just Pod/Deployment) and stubbing the rest would fail dedicated per-kind tests; the kind table/dispatch must be exhaustive.
- Skipping real YAML parsing in favor of regex/string-matching on manifest files might pass trivial examples but fail on nested specs, multi-doc files, or flow-style collections used by hidden tests.
- Ignoring `--namespace`/`-n` and always operating on `default` would silently break multi-namespace test sequences even though single-namespace tests might pass.

## Success criteria

- For every declared verb × required kind combination, the CLI produces the specified stdout message shape, correct exit code, and correct stderr substring for both success and documented error cases.
- State mutations are durable and visible across separate CLI invocations against the same live apiserver: create/apply → get finds it; patch/label/scale → get reflects the change; delete → get/read 404s afterward.
- `apply` is idempotent (repeat run on unchanged manifest reports `unchanged`, not `created`/`configured`), while `create` is strictly create-once and errors with `AlreadyExists` on repeats.
- `-o json`/`-o yaml` output is valid, parseable JSON/YAML representing the actual resource.
- Flag handling matches the exit-code contract: unknown flags → 2; missing required args per verb rules → 1 or 2 as specified; nonexistent resources → 1 with correct substring.
- The binary is executable at `/workspace/submission/kubectl`, reads `KUBECONFIG` from the environment, and requires no other files/services beyond that endpoint.
- Namespace scoping (`-n`/`--namespace`/`-A`) is honored consistently across all verbs that declare it.