# TRUTH: a910a9f1-ccfb-4428-9267-615cbea82ff8

## Problem

Build a single executable, `/workspace/submission/kubectl`, that implements a verb-first subset of `kubectl` (`apply`, `create`, `delete`, `describe`, `get`, `label`, `patch`, `scale`) against a real kwok-backed Kubernetes apiserver reachable via `KUBECONFIG`. The CLI must dispatch on `argv[1]` as the verb, support the TYPE positional or manifest `kind:` field to select among 13 required Kubernetes kinds (plus best-effort discovery-based support for several auxiliary kinds), and preserve consistent state across a create→get→patch→scale→delete lifecycle. The implementation is invoked as a subprocess and judged purely on stdout/stderr/exit-code behavior and on the resulting apiserver state, not on internal structure.

## Behavioral contract

- Invocation shape is strictly `kubectl VERB [TYPE] [NAME] [flags...]` — never `kubectl TYPE VERB`.
- One binary/script handles all 8 verbs; dispatch happens on `argv[1]`.
- Must talk to the real apiserver pointed to by the `KUBECONFIG` env var (read at runtime, never hard-coded).
- Kind resolution happens either from a manifest's `kind:` field (apply/create -f) or from the TYPE positional (get/delete/describe/patch/scale/label), including common short aliases (`po`, `svc`, `cm`, `deploy`, etc.) and both singular/plural forms.
- Success-path stdout must match real kubectl's message shapes:
  - `apply`: `<kind>/<name> created` / `configured` / `unchanged`
  - `create`: `<kind>/<name> created`
  - `delete`: `<kind> "<name>" deleted` (quoted-name form, distinct from the slash form)
  - `label`, `patch`, `scale`: analogous kubectl-style confirmation lines (not specified verbatim above but must convey the resource and the action, matching kubectl idioms)
- Exit codes are meaningful and consistently split:
  - `2` for argument/flag parsing errors (unknown flags, missing required positional args) — argparse-style, stderr contains "invalid"
  - `1` for apiserver-level failures (not found, already exists, validation, malformed manifest, missing file) — stderr contains `NotFound`/`AlreadyExists`/`Invalid` (capitalized) as appropriate
  - `0` on success, including when `--ignore-not-found` suppresses a would-be-404 delete
- State changes must be real and durable: after `create`/`apply`, the object is visible via `get`/`list` and via direct `read_<kind>` equivalents; after `delete`, it is gone (404 on read).
- `apply` is idempotent (safe to repeat with unchanged spec ⇒ `unchanged`); `create` is not (second create of same name ⇒ `AlreadyExists`, exit 1).
- `describe` is read-only — never mutates state — and its output must contain the resource name plus recognizable section headers (`Name:`, `Namespace:`, `Status:`/`Labels:` for Namespace, `Annotations:`, `Events:` where applicable). Exact formatting/whitespace is not pinned.
- `get -o json`/`-o yaml` must produce genuinely parseable JSON/YAML of the underlying object(s); table output for plain `get` should have kubectl-like columns (e.g. pods: `NAME READY STATUS RESTARTS AGE`).
- Flags listed per-verb (namespace via `-n`/`--namespace`, `-f`/`--filename`, `--all`, `--all-namespaces`, `-l`/`--selector`, `--grace-period`, `--force`, `--dry-run`, `-o`, `--from-literal`, etc.) must be accepted; unrecognized/invalid flags must fail with exit 2, not silently ignored or silently accepted.
- No invented flags beyond real kubectl v1.31's surface (e.g., no fictitious `--wait-for` on apply).

## Solution decomposition

1. **Argument parsing / dispatch**: parse `argv[1]` as verb; branch to a per-verb handler. Each handler must independently parse its own flags (shared helpers for `-n/--namespace`, `-f/--filename`, `-o/--output`, `-l/--selector`, generic boolean flags) and reject unknown flags with exit 2.
2. **Kind/resource resolution**: a table mapping kind names & aliases (singular, plural, short forms) to their REST resource (group/version/plural/namespaced-ness), covering the 13 required kinds plus optional discovery-driven support for Role/RoleBinding/ClusterRole/ClusterRoleBinding/NetworkPolicy/LimitRange/ResourceQuota/PriorityClass/PodDisruptionBudget.
3. **Kubeconfig/client bootstrap**: read `KUBECONFIG`, build an HTTP client (with TLS/auth as configured) capable of issuing REST verbs (GET/POST/PUT/PATCH/DELETE) against `/api/v1/...` and `/apis/<group>/<version>/...` for namespaced and cluster-scoped resources.
4. **Manifest ingestion**: a YAML (and JSON) parser sufficient to read Kubernetes manifests (multi-document via `---`, block/flow mappings & sequences, scalars, quoting, literal/folded blocks) — doesn't need to be a full YAML spec implementation, just enough to round-trip typical k8s manifests.
5. **Verb implementations**:
   - `apply`: read manifest(s), GET current object; if missing POST/create → `created`; if present, compute whether spec differs — PATCH (merge or replace) → `configured`, or no-op → `unchanged`.
   - `create`: from `-f` manifest or typed sub-forms (`create namespace NAME`, `create configmap/secret --from-literal=...`, `create deployment --image=`, `create service clusterip --tcp=`, `create ingress --rule=`, `create job --image=`, `create cronjob --image= --schedule=`); POST; surface 409 as `AlreadyExists`.
   - `delete`: resolve kind+name (or `--all`/`-f`), DELETE; print quoted-name confirmation per deleted object; surface 404 as `NotFound`; honor `--ignore-not-found`, `--grace-period`, `--force`.
   - `describe`: GET/LIST and format human-readable sections; read-only.
   - `get`: LIST/GET and render table or `-o json/yaml` (custom-columns/jsonpath best-effort, not required to be pixel-perfect).
   - `label`: PATCH `metadata.labels` on named or selected resources.
   - `patch`: apply a JSON/strategic-merge/JSON-merge patch body (`--type` variants) to a named resource.
   - `scale`: PATCH `spec.replicas` for scalable kinds (Deployment, ReplicaSet, StatefulSet, etc.) via `--replicas=N`.
6. **Error mapping**: apiserver HTTP status → CLI exit code + stderr text (404→1/NotFound, 409→1/AlreadyExists, 422/400→1/Invalid, argparse failures→2/invalid).

## Solution space

Many implementation choices are equally valid as long as observable behavior matches:

- **Language/tooling**: Go (as in reference), Python (using the official `kubernetes` client or raw `requests` + a kubeconfig loader), Node, Rust, or even a shell script wrapping the real `kubectl`/`curl` binaries if available in the runtime image — the task explicitly allows "any idiomatic client library."
- **Wrapping real kubectl binary**: if a genuine `kubectl` binary is present in the runtime image, a thin shim script that rewrites/forwards argv to it and adjusts exit codes/output where needed is a legitimate approach, provided verb dispatch and flag surface match the spec.
- **YAML parsing**: using a full third-party YAML library (e.g., `gopkg.in/yaml.v3`, PyYAML, `js-yaml`) instead of a hand-rolled parser is equally valid and lower-risk.
- **Kubernetes client**: using an official generated client (client-go, python `kubernetes` package) that loads `KUBECONFIG` natively is a fully valid — arguably safer — alternative to hand-rolled REST calls.
- **Apply diffing strategy**: "unchanged" detection can be done via full deep-equal of desired vs. live spec, via a stored last-applied-configuration annotation (kubectl's real strategy), or via generation/resourceVersion comparison — any approach that yields correct `created`/`configured`/`unchanged` semantics is acceptable.
- **Patch mechanics**: strategic merge patch, JSON merge patch, or read-modify-PUT are all acceptable for `apply`/`patch`/`label`/`scale` as long as end state and stdout messages are correct.
- **Discovery for auxiliary kinds**: can be hard-coded (as in the reference) or dynamically resolved via the apiserver's `/apis` discovery documents — both satisfy the "same conventions as declared kinds" requirement.
- **Output formatting**: `-o custom-columns`/`-o jsonpath` can be implemented fully, partially (best-effort field extraction), or even fall back to `-o json` internally as long as basic cases don't crash and exit codes stay correct — spec explicitly says tests shouldn't pin on exact formatting beyond required substrings.

## Known pitfalls

- Implementing `kubectl <resource> <verb>` ordering instead of verb-first dispatch — instruction explicitly says this shape does not exist and would fail every test.
- Conflating `apply`'s `created`/`configured`/`unchanged` message logic with `create`'s always-`created` message — tests check idempotency semantics differ between the two verbs.
- Returning generic exit code 1 for flag-parsing errors (should be 2) or vice versa — the split between "usage error" (2) and "apiserver/business error" (1) is load-bearing across nearly every verb's error-case table.
- Wrong delete message shape: using `<kind>/<name> deleted` (slash form) instead of the required `<kind> "<name>" deleted` (quoted form) — these are explicitly called out as different shapes.
- Not handling both short (`pod`) and qualified (`pod.core`) kind fragments in delete confirmation matching.
- Missing `--ignore-not-found` handling causing exit 1 when a 0 is required.
- Not supporting both `-f file` and typed sub-form creation (`create namespace NAME`, `create configmap --from-literal=`) — tests exercise both entry paths.
- Base64-encoding forgotten for `Secret --from-literal` data (ConfigMap must NOT be base64-encoded, Secret must).
- Failing to make `delete` require either a NAME or `--all` (missing both should be exit 2, not silently deleting nothing or crashing).
- Case-sensitivity/alias gaps in kind resolution (e.g., not accepting `pods` plural, `po` short alias, or manifest `kind: Pod` vs CLI `pod`).
- YAML edge cases: multi-document manifests (`---` separated), quoted strings, block scalars (`|`, `>`), flow collections (`{}`, `[]`) — a naive line-splitter can silently mis-parse legitimate manifests, causing spurious "Invalid" failures.
- Treating `--namespace`/`-n` inconsistently across verbs (must default to `default` namespace everywhere it's applicable).
- Not making `describe` genuinely read-only (accidentally triggering side effects via GET-then-PUT patterns).
- Hard-coding cluster endpoints instead of reading `KUBECONFIG` — breaks portability to the sandboxed kwok cluster.
- Forgetting `chmod +x` on the final executable.

## Cheat surface

- **Stdout-pattern-matching without real backend calls**: printing a plausible `"pod/foo created"` string without actually creating anything in the apiserver would pass a naive stdout-substring check but fail the state-invariant checks (`get` after `apply`, 404 after `delete`, etc.) — tests are explicit that these lifecycle chains must hold, so this is a detectable and disallowed shortcut.
- **Ignoring flags and always exiting 0/1 by pattern-matching argv text**: e.g., special-casing literal strings like `"nonexistent-"` in the test fixtures instead of doing real existence checks — would break on any name not containing that literal substring and is not a general solution.
- **Only implementing pods and stubbing all other kinds**: satisfies few tests but the task explicitly enumerates 13 required kinds with cross-verb coverage; partial kind support is directly gradable by the "391 tests shipped" breadth.
- **Skipping proper idempotency logic in `apply`** by always printing `created` or always printing `configured`: breaks the explicit created→configured/unchanged transition tests.
- **Not distinguishing exit 1 vs exit 2**: a solution that always exits 1 (or always 2) on any error will fail roughly half the observed error-case rows, which are enumerated per-verb precisely to catch this.
- **Faking `describe`/`get` output as static text**: since output must reflect real object fields (name, namespace, status) fetched from the live cluster, static/templated text divorced from actual API responses fails immediately on differently-named fixtures.

## Success criteria

- The compiled/scripted artifact exists at `/workspace/submission/kubectl`, is executable, and dispatches correctly on all 8 verbs for all 13 required kinds (plus reasonable handling of the auxiliary kinds via discovery-like conventions).
- For each verb, the argv shapes and flags enumerated in the spec are accepted; unrecognized flags and missing required positionals produce exit 2 with `invalid`-containing stderr.
- Apiserver-level failures (not found, already exists, invalid manifest) produce exit 1 with stderr containing the appropriate reason keyword (`NotFound`, `AlreadyExists`, `Invalid`), and `--ignore-not-found` downgrades a delete-not-found to exit 0.
- End-to-end lifecycle consistency holds: `create`/`apply` → visible in `get`/`list`; `patch`/`label`/`scale` → visibly mutate the object's fields; `delete` → object subsequently absent/404.
- `apply` reapplication of an unchanged manifest yields `unchanged`; a modified manifest yields `configured`; first application yields `created`. `create` is never idempotent.
- stdout success messages match the required shapes per verb (`kind/name created|configured|unchanged` for apply/create; `kind "name" deleted` for delete; readable table/JSON/YAML for get; structured sections with required headers for describe).
- No hard-coded cluster endpoints; `KUBECONFIG` is honored so the same binary works against the sandboxed kwok cluster used at grading time.