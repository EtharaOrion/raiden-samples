# TRUTH: 1d830c1a-fd95-4c1c-9a00-74aa3bbd5463

## Problem

Build a single executable, `/workspace/submission/kubectl`, that implements a verb-first CLI subset (`apply`, `create`, `delete`, `describe`, `get`, `label`, `patch`, `scale`) against a real Kubernetes-compatible apiserver (kwok-backed, reached via `KUBECONFIG` from the environment). The CLI must correctly dispatch on argv[1] as the verb, resolve the target Kubernetes kind either from a manifest's `kind:` field or from a TYPE positional argument, and must correctly handle the 13 required kinds (ConfigMap, CronJob, DaemonSet, Ingress, Job, Namespace, PersistentVolumeClaim, Pod, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet) plus best-effort support for several auxiliary kinds (Role, RoleBinding, ClusterRole, ClusterRoleBinding, NetworkPolicy, LimitRange, ResourceQuota, PriorityClass, PodDisruptionBudget) via generic REST/discovery calls. State must persist across verb invocations (create→get→patch→scale→delete chains must be consistent), matching real kubectl's stdout shapes and exit codes closely enough for behavioral/substring tests.

## Behavioral contract

- Invocation: `kubectl <verb> [TYPE] [NAME] [flags...]`. No resource-first subcommand form is ever accepted.
- Talks to the real apiserver pointed to by `$KUBECONFIG` (never hard-coded endpoints); uses standard REST verbs (GET/POST/PUT/PATCH/DELETE) against the appropriate group/version/plural/namespace paths.
- Exit codes are semantically meaningful and tested:
  - `0`: success.
  - `1`: apiserver-level failures — NotFound, AlreadyExists, Invalid manifest content, generic "error:" conditions.
  - `2`: CLI/argument-parsing failures — unknown flags (`--invalid-flag`, `--bogus`), missing required positional args, argparse-style usage errors. Stderr must contain "invalid" (lowercase) for these.
- Success/failure stdout/stderr shapes must match real kubectl closely:
  - `apply`: `<kind>/<name> created|configured|unchanged`.
  - `create`: `<kind>/<name> created`.
  - `delete`: `<kind> "<name>" deleted` (note differing shape vs. apply/create — quoted name, space not slash).
  - `describe`: multi-section human text containing `Name:`, and for Namespace additionally `Status:` or `Labels:`.
  - `get`: tabular NAME/... columns by default; machine-parseable output for `-o json`/`-o yaml`; must support (at least minimally) `-o name`, `-o wide`, `-o custom-columns=...`, `-o jsonpath=...`.
  - `label`/`patch`/`scale`: analogous `<kind>/<name> labeled|patched|scaled` style confirmations (per full instructions, truncated above but same pattern family).
- Stderr must contain specific substrings the tests grep for: `NotFound`, `AlreadyExists`, `Invalid`/`invalid`, `resource(s) were provided` (for missing-name delete).
- State invariants: after `apply`/`create`, the resource is visible via `get`/`describe`/underlying `read_<kind>`/`list_<kind>`; after `delete`, it is absent (404 on read, absent from list). `apply` is idempotent (unchanged/configured), `create` is not (AlreadyExists on repeat).
- `--ignore-not-found` on delete converts a would-be exit-1 NotFound into exit 0.
- Unknown/invalid kind on delete/describe/get/etc. is a runtime (exit 1) failure, not a parse error, since it's a valid-looking positional that just doesn't match any resource type known to the apiserver/discovery.

## Solution decomposition

1. **Argument parsing layer**: a flag parser per verb that recognizes the documented flag set (long and short forms), rejects unrecognized flags with exit 2, and distinguishes "malformed CLI usage" (exit 2) from "well-formed CLI but semantically invalid/missing resource" (exit 1).
2. **Kind resolution**: a table mapping singular/plural/short aliases (pod/pods/po, svc/service/services, etc.) to canonical Kind name + apiVersion group/version + REST plural + namespaced/cluster-scoped flag, covering the 13 required kinds and the auxiliary kinds via discovery or a static extension table.
3. **Manifest ingestion** (`apply`/`create -f`, and `delete -f`): a YAML (and ideally JSON) parser sufficient to decode Kubernetes manifests — mapping/list/scalar nodes, multi-document `---` support, quoted strings, block scalars — used to extract `kind`, `metadata.name`, `metadata.namespace`, and full spec body to PUT/POST.
4. **HTTP/Kubernetes client**: build requests against the apiserver using the kubeconfig's cluster URL + auth (bearer token/client cert per kubeconfig), constructing the correct REST path `/api/v1/...` or `/apis/<group>/<version>/...` with `namespaces/<ns>/` segment when namespaced.
5. **Per-verb semantics**:
   - `apply`: GET existing → if 404 POST (create, print "created"); else compute whether spec differs → PUT/PATCH (print "configured") or no-op (print "unchanged").
   - `create`: typed sub-forms (`create namespace NAME`, `create configmap/secret ... --from-literal`, `create service clusterip`, `create job/cronjob --image=...`, `create ingress --rule=...`) build a manifest object programmatically; `-f` form parses file. POST always; 409 on conflict → AlreadyExists.
   - `delete`: resolve name(s) (positional, `--all`, or from `-f` manifest), DELETE each, print per-object confirmation; handle `--grace-period`, `--force`, `--ignore-not-found`.
   - `describe`: GET (or LIST if bulk/selector), format multi-section text output.
   - `get`: LIST or GET, render table or the requested `-o` format.
   - `label`/`patch`/`scale`: fetch, mutate (merge labels / apply JSON patch or merge-patch body / set replica count), PUT/PATCH back, confirm.
6. **Error mapping**: apiserver HTTP status → CLI exit code + stderr substring (404→NotFound/exit1, 409→AlreadyExists/exit1, 422/400→Invalid/exit1, unknown flag→exit2 with "invalid").

## Solution space

Multiple implementation strategies are equally valid as long as behavior matches:

- **Language/tooling**: any language with an HTTP client and a way to read kubeconfig (Go with client-go, Python with the official `kubernetes` client, Node with `@kubernetes/client-node`, or a hand-rolled HTTP+YAML client in any language, as the reference does in raw Go without client-go). A shell script wrapping the real `kubectl` binary (if present in the image) is also plausible, as long as flag/exit-code shaping matches the spec exactly.
- **YAML parsing**: use an existing library (`gopkg.in/yaml.v3`, PyYAML, `js-yaml`) instead of hand-rolling a parser — simpler and equally correct.
- **Discovery of auxiliary kinds**: either query the apiserver's `/apis` discovery endpoints dynamically to resolve group/version/plural for non-required kinds, or hard-code a static table (as reference does) — both satisfy "same conventions as declared kinds."
- **Apply diffing**: "unchanged" detection can be implemented via deep-equality of spec after normalization, via a dry-run diff against the server, or via generation/resourceVersion comparison — any approach that yields correct created/configured/unchanged semantics is acceptable.
- **Typed create sub-forms**: could be implemented by building a manifest struct in-memory and funneling through the same "apply/create" codepath used for `-f`, or via bespoke logic per sub-form — decomposition is an implementation detail.
- **Patch verb**: strategic-merge-patch, JSON merge-patch, or JSON-patch bodies are all acceptable transport mechanisms provided the resulting resource state and confirmation message are correct.
- **Table rendering for `get`**: any column layout is fine as long as required column headers/values needed by tests (NAME, etc.) are present; exact spacing is not asserted.

## Known pitfalls

- Implementing a resource-first CLI (`kubectl pods apply`) instead of verb-first — explicitly disallowed.
- Conflating exit codes 1 vs 2: argument/flag parsing errors (unknown flags, missing required positional with no `--all`) must be 2 with "invalid" in stderr; apiserver/domain errors must be 1 with capitalized reason words (`NotFound`, `AlreadyExists`, `Invalid`).
- Making `create` idempotent like `apply` (must error AlreadyExists on repeat).
- Making `apply` non-idempotent (must be a no-op / "unchanged" on identical re-apply, not error).
- Wrong stdout shape: using `<kind>/<name> deleted` instead of the quoted `<kind> "<name>" deleted` form for delete; or missing the required `Name:`/`Status:`/`Labels:` section headers for describe.
- Forgetting `--ignore-not-found` short-circuit (must yield exit 0 instead of 1 on delete of missing resource).
- Hard-coding the apiserver endpoint instead of reading `KUBECONFIG` from env — breaks portability to the sandboxed kwok cluster.
- Not handling both short and long flag forms (`-f`/`--filename`, `-n`/`--namespace`, `-l`/`--selector`, `-A`/`--all-namespaces`, `-o`).
- Failing to accept both short and qualified kind fragments in delete confirmation (`pod` vs `pod.core`) if tests probe that, and not covering all 13 declared kinds uniformly for every verb (e.g., forgetting `describe`/`scale`/`label`/`patch` support for CronJob, DaemonSet, Ingress, etc.).
- Mis-parsing YAML edge cases (multi-doc `---`, block scalars, quoted strings, flow mappings/lists) causing valid manifests to be rejected as malformed, or malformed manifests to be silently accepted.
- Not surfacing missing-file / malformed-YAML as exit 1 with "Invalid" (or exit 2 "invalid" only for missing required argparse args), i.e. conflating "no -f given at all" (exit 2, arg error) vs "file given but doesn't exist/parses badly" (exit 1).
- Treating "unknown kind" as an exit-2 parse failure rather than exit-1 runtime failure — spec explicitly places `delete invalidkind ...` and `describe invalidkind ...` at exit 1.
- Scale/patch/label logic that doesn't persist through the apiserver (i.e., mutating a local copy without a subsequent PUT/PATCH round-trip), breaking the create→get→patch→scale→delete state-consistency requirement.

## Cheat surface

- Hard-coding fixed/expected stdout strings for a fixed set of test resource names without genuinely calling the apiserver — would fail on the hidden test manifests with different names/namespaces since correctness is checked via actual API state (get/read after apply, 404 after delete), not just captured text.
- Special-casing on filenames or literal manifest content matching sample fixtures rather than truly parsing arbitrary YAML — fails on any manifest whose formatting differs from the samples yet is semantically equivalent.
- Faking `get -o json`/`yaml` output as static text instead of real object serialization — fails machine-parseability checks.
- Ignoring the required idempotency distinction between `apply` and `create` and just always creating/overwriting — fails re-apply/AlreadyExists checks.
- Bypassing the real cluster entirely (an in-process fake store) — violates "keep state consistent across verbs" against the *actual* kwok apiserver that the test harness also inspects directly, and would fail any check that reads state independently of this CLI.
- Returning exit 0 unconditionally and printing plausible messages regardless of actual server response — fails the extensive exit-code/stderr-substring matrix.

## Success criteria

- The binary is present, executable, and correctly dispatches on argv[1] for all 8 verbs across all 13 required kinds (plus reasonable handling of the 9 auxiliary kinds via generic discovery/convention).
- All documented argv shapes and flags (short and long forms) parse correctly; unrecognized flags always yield exit 2 with `invalid` in stderr; missing required positionals without `--all` yield exit 2.
- Apiserver-level failures (missing resource, duplicate resource, invalid manifest) yield exit 1 with `NotFound`/`AlreadyExists`/`Invalid` (or lowercase equivalents) in stderr, per case.
- Stdout success messages match the real-kubectl shapes noted per verb (`created`/`configured`/`unchanged`, `<kind> "<name>" deleted`, describe section headers, get table/`-o` formats).
- End-to-end state consistency holds: `create`/`apply` → visible in `get`/`describe`/list+read; `patch`/`label`/`scale` → mutation persists and is observable afterward; `delete` → resource vanishes from list and read returns 404.
- `apply` is idempotent (no-op on identical re-apply); `create` is not (errors on duplicate).
- Solution reads `KUBECONFIG` from the environment and performs real network calls to the sandboxed kwok cluster rather than emulating state locally.