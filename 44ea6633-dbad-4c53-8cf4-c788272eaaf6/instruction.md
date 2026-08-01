# Build a `kubectl` CLI (verbs: apply, create, delete, describe, get, label, patch, scale; covering 13 kinds: ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet)

## Application overview

You are implementing a subset of real kubectl verbs:
`kubectl apply`, `kubectl create`, `kubectl delete`, `kubectl describe`, `kubectl get`, `kubectl label`, `kubectl patch`, `kubectl scale`. Real kubectl is **verb-first** — the invocation shape is
`kubectl VERB [TYPE] [NAME] [flags]`. There is no
`kubectl <resource> <verb>` subcommand form; `kubectl configmaps apply` DOES NOT
EXIST. Your implementation must support every declared verb on every
declared kind: this task exercises the 13 Kubernetes kinds under test (ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet), entering the CLI
either via the manifest's `kind:` field (for `apply`/`create -f`) or as
the TYPE positional after the verb (for
`get`/`delete`/`describe`/`patch`/`scale`/`label`).

The agent is given **no source code**, only this specification. Your
implementation is an executable at `/workspace/submission/kubectl`,
invoked as a subprocess:

```bash
/workspace/submission/kubectl <verb> [TYPE] [NAME] [flags...]
```

Dispatch on argv[1] (the verb: `apply`, `get`, `delete`, `describe`,
`patch`, `scale`, `label`, `create`) so one program handles every verb
above.

Any executable format works — shebang script or compiled binary. The
runtime image ships toolchains for a range of general-purpose
languages; use whichever you prefer, with any client library idiomatic
for that language.

Make sure the file is executable (`chmod +x`). The runtime configures
`KUBECONFIG` in the environment to point at a sandboxed kwok cluster
(lightweight apiserver + etcd-backed storage simulating Kubernetes
control-plane semantics faithfully). Read `KUBECONFIG` from the
environment; do NOT hard-code endpoints. Treat the backend as real
Kubernetes, and keep state consistent across verbs so a sequence like
create -> get -> patch -> scale -> delete behaves correctly end-to-end. Test manifests may also reference other Kubernetes kinds (`Role`, `RoleBinding`, `ClusterRole`, `ClusterRoleBinding`, `NetworkPolicy`, `LimitRange`, `ResourceQuota`, `PriorityClass`, `PodDisruptionBudget`); those are not part of the required kind set but can be handled via the apiserver's discovery API using the same conventions as declared kinds.

## Verbs

### Verb: `kubectl apply` (across 13 kinds: ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet)

**Interface — observed argv patterns:**

- `apply -f <configmap-manifest>`
- `apply -f <configmap-manifest> -n default`
- `apply -f <configmap-manifest> --namespace default`
- `apply -f <deployment-manifest>`
- `apply -f <deployment-manifest> -n default`
- `apply -f <configmap-manifest>`
- `apply -f <configmap-manifest> -n default`
- `apply -f <service-manifest>`
- `apply -f <service-manifest> -n default`
- `apply -f <namespace-manifest>`
- `apply --filename <configmap-manifest>`
- `apply -f <configmap-manifest> -n kube-system`
- `apply -f <deployment-manifest> -n test-ns`
- `apply -f nonexistent-1f6479a0.yaml`
- `apply -f nonexistent-1f6479a0.yaml -n default`
- `apply -f nonexistent-1f6479a0.yml`
- `apply --filename nonexistent-1f6479a0.yaml`
- `apply --invalid-flag`
- `apply`
- `apply -f <configmap-manifest> --invalid-flag`

**Flags (real kubectl v1.31 — support all):**

| Flag | Example value |
|---|---|
| `--filename` | `<configmap-manifest>` |
| `--force` | _(boolean)_ |
| `--invalid-flag` | _(boolean)_ |
| `--namespace` | `default` |
| `--recursive` | _(boolean)_ |
| `-f/--filename` | _(v1.31)_ |
| `-n/--namespace` | _(v1.31)_ |
| `--dry-run=client/server/none` | _(v1.31)_ |
| `--field-manager` | _(v1.31)_ |

**Behavior:**

- Applies a manifest (`-f <file>`) declaratively: creates the resource if absent, patches it toward the manifest if present (idempotent).
- After success, `kubectl get` on the same name/namespace MUST list the resource; a re-apply of the SAME manifest is a no-op with respect to spec.
- Success stdout is real-kubectl shape: `<kind>/<name> created` on first apply, `<kind>/<name> configured` or `<kind>/<name> unchanged` on re-apply.
- Missing manifest file, malformed YAML, or a manifest that fails apiserver validation FAILS with exit `1` (stderr contains `Invalid`) or exit `2` (stderr contains `invalid` for argparse-style flag errors).
- `kubectl apply` has NO `--wait-for` flag upstream; only `--wait` exists. Do NOT invent flags outside the observed argv shapes.
- State invariant: after `apply -f configmap.yaml`, `read_namespaced_configmap` returns the configmap with `.metadata.name` matching the manifest's `metadata.name`.

**Error cases observed:**

- `apply -f nonexistent-1f6479a0.yaml` -> exit `1`
- `apply -f nonexistent-1f6479a0.yaml -n default` -> exit `1`
- `apply -f nonexistent-1f6479a0.yml` -> exit `1`
- `apply --filename nonexistent-1f6479a0.yaml` -> exit `1`
- `apply --invalid-flag` -> exit `2`
- `apply` -> exit `1`
- `apply -f <configmap-manifest> --invalid-flag` -> exit `2`

### Verb: `kubectl create` (across 13 kinds: ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet)

**Interface — observed argv patterns:**

- `create -f <configmap-manifest>`
- `create -f <configmap-manifest> -n default`
- `create -f <deployment-manifest>`
- `create -f <deployment-manifest> -n default`
- `create -f <namespace-manifest>`
- `create --filename <configmap-manifest>`
- `create --filename <configmap-manifest> -n default`
- `create -f <configmap-manifest> --namespace default`
- `create -f <configmap-manifest> -n test-ns`
- `create -f <deployment-manifest> -n kube-system`
- `create namespace <resource>`
- `create namespace <resource-2>`
- `create -f nonexistent-4971728e.yaml`
- `create -f nonexistent-4971728e.yaml -n default`
- `create --filename nonexistent-4971728e.yaml`
- `create -f nonexistent-4971728e.yml`
- `create --invalid-flag`
- `create`
- `create -f <configmap-manifest> --invalid-flag`
- `create namespace <resource-3>`
- `create deployment <name> --image=<image>`
- `create service clusterip <name> --tcp=<sport>:<tport>`
- `create ingress <name> --rule=<host/path=service:port>`
- `create job <name> --image=<image>`
- `create cronjob <name> --image=<image> --schedule=<cron>`

**Flags (real kubectl v1.31 — support all):**

| Flag | Example value |
|---|---|
| `--dry-run` | _(boolean)_ |
| `--filename` | `<configmap-manifest>` |
| `--invalid-flag` | _(boolean)_ |
| `--namespace` | `default` |
| `-f/--filename` | _(v1.31)_ |
| `-n/--namespace` | _(v1.31)_ |
| `--from-literal` | `KEY=VALUE` |

**Behavior:**

- Creates a resource from a manifest (`-f <file>`) or from typed sub-forms such as `create namespace <name>` / `create configmap <name>`.
- Populates a `ConfigMap` or `Secret` `data` map from `--from-literal=<KEY>=<VALUE>` pairs (repeatable); `Secret` values are base64-encoded automatically.
- Typed sub-forms without `-f` accept `create namespace <name>` and `create configmap`/`create secret generic <name>`; other kinds require `create -f <manifest>`.
- After success, the resource MUST appear in the corresponding `list_<kind>` result; `read_<kind>` returns the created object.
- Success stdout is real-kubectl shape: `<kind>/<name> created`.
- Creating a resource that already exists FAILS with exit `1` and stderr containing `AlreadyExists`.
- `create` is NOT idempotent (unlike `apply`) — a second `create` of the same name errors out with `AlreadyExists`.
- Missing or unparseable `-f` payload FAILS with exit `1` (stderr `Invalid`) or exit `2` (stderr `invalid` for missing-arg errors).

**Error cases observed:**

- `create -f nonexistent-4971728e.yaml` -> exit `1`
- `create -f nonexistent-4971728e.yaml -n default` -> exit `1`
- `create --filename nonexistent-4971728e.yaml` -> exit `1`
- `create -f nonexistent-4971728e.yml` -> exit `1`
- `create --invalid-flag` -> exit `2`
- `create` -> exit `1`
- `create -f <configmap-manifest> --invalid-flag` -> exit `2`

### Verb: `kubectl delete` (across 13 kinds: ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet)

**Interface — observed argv patterns:**

- `delete configmap <resource> -n default`
- `delete configmap <resource> --namespace default`
- `delete deployment <resource> -n default`
- `delete service <resource> -n default`
- `delete configmap <resource> -n default`
- `delete namespace <resource>`
- `delete configmap <resource> --force -n default`
- `delete configmap <resource> --grace-period 0 -n default`
- `delete configmap <resource> --grace-period 30 -n default`
- `delete configmap <resource> --force --grace-period 0 -n default`
- `delete configmap <resource> -n kube-system`
- `delete deployment <resource> -n kube-system`
- `delete configmap nonexistent-b952fd17 -n default`
- `delete deployment nonexistent-b952fd17 -n default`
- `delete namespace nonexistent-b952fd17`
- `delete configmap nonexistent-b952fd17 -n default`
- `delete configmap <resource> --invalid-flag -n default`
- `delete`
- `delete configmap`
- `delete invalidkind <resource> -n default`
- `delete -f <manifest>`
- `delete -f <manifest> -n default`

**Flags (real kubectl v1.31 — support all):**

| Flag | Example value |
|---|---|
| `--all` | _(boolean)_ |
| `--filename` | _(boolean)_ |
| `--force` | `-n` |
| `--grace-period` | `0` |
| `--invalid-flag` | `-n` |
| `--namespace` | `default` |
| `-n/--namespace` | _(v1.31)_ |
| `--wait` | _(v1.31)_ |
| `--ignore-not-found` | _(boolean)_ |
| `--filename` | `<manifest>` |

**Behavior:**

- Removes one or more resources from the apiserver via `delete_<kind>` and prints `<kind> "<name>" deleted` on stdout, once per removed object. The `<kind>` fragment may be short or qualified (`deployment.apps`); both are accepted by the tests.
- After success, the resource MUST NOT appear in the corresponding `list_<kind>` result; a follow-up `read_<kind>` raises `ApiException` with `.status == 404`.
- Deleting a non-existent resource FAILS with exit `1` and stderr containing `NotFound` (or lowercase `not found`).
- Bulk shapes such as `--all` (all objects in ns) or `--all-namespaces` remove the corresponding set atomically per kind.
- `--namespace <ns>` (or `-n`) selects the namespace; without it the default namespace is used.
- With `--ignore-not-found`, deleting a nonexistent resource returns exit `0` instead of exit `1`.
- A missing positional name AND missing `--all` MUST fail with exit `2` and stderr containing `invalid` / `resource(s) were provided`.

**Error cases observed:**

- `delete configmap nonexistent-b952fd17 -n default` -> exit `1`
- `delete deployment nonexistent-b952fd17 -n default` -> exit `1`
- `delete namespace nonexistent-b952fd17` -> exit `1`
- `delete configmap nonexistent-b952fd17 -n default` -> exit `1`
- `delete configmap <resource> --invalid-flag -n default` -> exit `2`
- `delete` -> exit `1`
- `delete configmap` -> exit `1`
- `delete invalidkind <resource> -n default` -> exit `1`

### Verb: `kubectl describe` (across 13 kinds: ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet)

**Interface — observed argv patterns:**

- `describe configmap <resource> -n default`
- `describe configmap <resource> --namespace default`
- `describe deployment <resource> -n default`
- `describe namespace <resource>`
- `describe configmap <resource>`
- `describe deployment <resource>`
- `describe configmap <resource> -n kube-system`
- `describe deployment <resource> -n kube-system`
- `describe configmap <resource> -n test-ns`
- `describe deployment <resource> -n test-ns`
- `describe configmap nonexistent-95c57d61 -n default`
- `describe deployment nonexistent-95c57d61 -n default`
- `describe namespace nonexistent-95c57d61`
- `describe configmap nonexistent-95c57d61`
- `describe deployment nonexistent-95c57d61`
- `describe configmaps <resource> --invalid-flag`
- `describe configmap <resource> --bogus`
- `describe`
- `describe configmap`
- `describe invalidkind <resource> -n default`
- `describe deployment <resource> --show-events=true -n default`

**Flags (real kubectl v1.31 — support all):**

| Flag | Example value |
|---|---|
| `--bogus` | _(boolean)_ |
| `--filename` | _(boolean)_ |
| `--invalid-flag` | _(boolean)_ |
| `--namespace` | `default` |
| `--selector` | _(boolean)_ |
| `-n/--namespace` | _(v1.31)_ |
| `-A/--all-namespaces` | _(v1.31)_ |
| `--show-events` | _(boolean)_ |
| `-l/--selector` | _(v1.31)_ |

**Behavior:**

- Prints a multi-section, human-readable view of one or more resources on stdout. The resource `<name>` MUST appear in the output; `describe namespace` MUST additionally include a `Status:` or `Labels:` section header. Standard section headers (`Name:`, `Namespace:`, `Annotations:`, `Events:`) SHOULD be emitted per kind semantics.
- Reads via `read_<kind>` (single object) or `list_<kind>` (bulk) and formats the result; NEVER mutates state.
- Describing a resource that does not exist FAILS with exit `1` and stderr containing `NotFound`.
- Section output is stable enough to substring-match on section headers (`Name:`, `Namespace:`, `Status:`) but tests should NOT pin on exact whitespace or full-line format.
- `--namespace <ns>` restricts the lookup; without it the default namespace is used.

**Error cases observed:**

- `describe configmap nonexistent-95c57d61 -n default` -> exit `1`
- `describe deployment nonexistent-95c57d61 -n default` -> exit `1`
- `describe namespace nonexistent-95c57d61` -> exit `1`
- `describe configmap nonexistent-95c57d61` -> exit `1`
- `describe deployment nonexistent-95c57d61` -> exit `1`
- `describe configmaps <resource> --invalid-flag` -> exit `2`
- `describe configmap <resource> --bogus` -> exit `2`
- `describe` -> exit `1`
- `describe configmap` -> exit `1`
- `describe invalidkind <resource> -n default` -> exit `1`

### Verb: `kubectl get` (across 13 kinds: ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet)

**Interface — observed argv patterns:**

- `get configmaps`
- `get configmaps -n default`
- `get configmaps --namespace default`
- `get configmaps -o json`
- `get configmaps -o yaml`
- `get configmaps -o json -n default`
- `get configmap <resource> -n default`
- `get configmap <resource> -o json -n default`
- `get configmap <resource> -o yaml -n default`
- `get deployments -n default`
- `get services -n default`
- `get configmaps -n default`
- `get configmap nonexistent-8507b33b -n default`
- `get deployment nonexistent-8507b33b -n default`
- `get configmap nonexistent-8507b33b -n default`
- `get configmaps --invalid-flag`
- `get`
- `get --namespace default`
- `get namespaces`
- `get configmaps -n kube-system`

**Flags (real kubectl v1.31 — support all):**

| Flag | Example value |
|---|---|
| `--all-namespaces` | _(boolean)_ |
| `--invalid-flag` | _(boolean)_ |
| `--namespace` | `default` |
| `--output` | _(boolean)_ |
| `--selector` | _(boolean)_ |
| `--watch` | _(boolean)_ |
| `-o json/yaml/wide/name/custom-columns/jsonpath` | _(v1.31)_ |
| `-n/--namespace` | _(v1.31)_ |
| `-A/--all-namespaces` | _(v1.31)_ |
| `-l/--selector` | _(v1.31)_ |

**Behavior:**

- Reads one or more resources from the apiserver via the corresponding `list_<kind>` / `read_<kind>` call and writes a human-readable table to stdout (`NAME  READY  STATUS  RESTARTS  AGE` for configmaps; analogous columns per kind).
- `-o json` / `-o yaml` MUST emit a machine-parseable object; keys are stable but ordering is not asserted.
- `--namespace <ns>` (or `-n`) restricts the list to that namespace. Without it, the default namespace is used; `--all-namespaces` widens the scope.
- Getting a resource that does not exist FAILS with exit `1` and stderr containing `NotFound` (or lowercase `not found`).
- Getting from a namespace that does not exist FAILS with exit `1` and stderr containing `NotFound`.
- `get` never mutates cluster state; a second `get` over an unchanged cluster MUST return the same set of names (order-independent).

**Error cases observed:**

- `get configmap nonexistent-8507b33b -n default` -> exit `1`
- `get deployment nonexistent-8507b33b -n default` -> exit `1`
- `get configmap nonexistent-8507b33b -n default` -> exit `1`
- `get configmaps --invalid-flag` -> exit `2`
- `get` -> exit `1`
- `get --namespace default` -> exit `1`

### Verb: `kubectl label` (across 13 kinds: ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet)

**Interface — observed argv patterns:**

- `label configmap <resource> env=prod -n default`
- `label configmap <resource> app=web -n default`
- `label configmap <resource> team=frontend -n default`
- `label configmap <resource> env=prod --namespace default`
- `label deployment <resource> env=prod -n default`
- `label deployment <resource> app=web -n default`
- `label configmap <resource> env- -n default`
- `label configmap <resource> env=prod app=web -n default`
- `label deployment <resource> env=prod app=web -n default`
- `label configmap <resource> env=dev --overwrite -n default`
- `label deployment <resource> env=dev --overwrite -n default`
- `label configmap <resource> env=prod -n kube-system`
- `label configmap nonexistent-924b02d5 env=prod -n default`
- `label deployment nonexistent-924b02d5 env=prod -n default`
- `label configmap nonexistent-924b02d5 env=prod`
- `label configmap <resource> env=prod --invalid-flag -n default`
- `label configmap <resource> -n default`
- `label`
- `label configmap`
- `label configmap <resource> not-a-valid-label-format -n default`

**Flags (real kubectl v1.31 — support all):**

| Flag | Example value |
|---|---|
| `--all` | _(boolean)_ |
| `--invalid-flag` | `-n` |
| `--namespace` | `default` |
| `--overwrite` | `-n` |
| `-n/--namespace` | _(v1.31)_ |
| `-l/--selector` | _(v1.31)_ |

**Behavior:**

- Adds, updates, or removes labels on an existing resource via a PATCH to `.metadata.labels`.
- `kubectl label <kind>/<name> key=value` sets the label; `kubectl label <kind>/<name> key-` (trailing hyphen) removes it.
- After success, `read_<kind>` MUST return the object with the mutated `.metadata.labels` map reflecting the change.
- Success stdout is real-kubectl shape: `<kind>/<name> labeled`.
- Setting a label that already exists WITHOUT `--overwrite` FAILS with exit `1` and stderr containing `already has a value` / `Invalid`.
- Labeling a non-existent resource FAILS with exit `1` and stderr containing `NotFound`.

**Error cases observed:**

- `label configmap nonexistent-924b02d5 env=prod -n default` -> exit `1`
- `label deployment nonexistent-924b02d5 env=prod -n default` -> exit `1`
- `label configmap nonexistent-924b02d5 env=prod` -> exit `1`
- `label configmap <resource> env=prod --invalid-flag -n default` -> exit `2`
- `label configmap <resource> -n default` -> exit `1`
- `label` -> exit `1`
- `label configmap` -> exit `1`
- `label configmap <resource> not-a-valid-label-format -n default` -> exit `1`

### Verb: `kubectl patch` (across 13 kinds: ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet)

**Interface — observed argv patterns:**

- `patch configmap <resource> -p {"metadata":{"labels":{"env":"prod"}}} -n default`
- `patch configmap <resource> --patch {"metadata":{"labels":{"env":"prod"}}} -n default`
- `patch deployment <resource> -p {"spec":{"replicas":2}} -n default`
- `patch deployment <resource> -p {"spec":{"replicas":3}} -n default`
- `patch configmap <resource> --type strategic -p {} -n default`
- `patch configmap <resource> --type merge -p {} -n default`
- `patch configmap <resource> --type json -p [] -n default`
- `patch deployment <resource> --type strategic -p {} -n default`
- `patch deployment <resource> --type merge -p {} -n default`
- `patch deployment <resource> --type json -p [] -n default`
- `patch configmap <resource> -p {} -n kube-system`
- `patch deployment <resource> -p {} --namespace default`
- `patch configmap nonexistent-43b014ad -p {} -n default`
- `patch deployment nonexistent-43b014ad -p {} -n default`
- `patch configmap nonexistent-43b014ad -p {}`
- `patch configmap <resource> --invalid-flag`
- `patch configmap <resource> -n default`
- `patch`
- `patch configmap`
- `patch invalidkind <resource> -p {} -n default`

**Flags (real kubectl v1.31 — support all):**

| Flag | Example value |
|---|---|
| `--invalid-flag` | _(boolean)_ |
| `--namespace` | `default` |
| `--patch` | `{"metadata":{"labels":{"env":"prod"}}}` |
| `--type` | `strategic` |
| `-p/--patch` | _(v1.31)_ |
| `-n/--namespace` | _(v1.31)_ |
| `--dry-run` | `client` |

**Behavior:**

- Applies a strategic-merge or JSON patch (`--patch <body>` or `-p <body>`) to an existing resource via `patch_<kind>`; only the fields named in the patch are changed, others are preserved.
- After success, `read_<kind>` MUST return the object with the patched fields reflecting the patch body; unmodified fields keep their prior value.
- Success stdout is real-kubectl shape: `<kind>/<name> patched`.
- Patching a non-existent resource FAILS with exit `1` and stderr containing `NotFound`.
- A malformed patch body (invalid JSON, unknown field, illegal value) FAILS with exit `1` and stderr containing `Invalid`.
- `--type strategic|merge|json` selects the patch semantics; the default is `strategic` for built-in kinds.

**Error cases observed:**

- `patch configmap nonexistent-43b014ad -p {} -n default` -> exit `1`
- `patch deployment nonexistent-43b014ad -p {} -n default` -> exit `1`
- `patch configmap nonexistent-43b014ad -p {}` -> exit `1`
- `patch configmap <resource> --invalid-flag` -> exit `2`
- `patch configmap <resource> -n default` -> exit `1`
- `patch` -> exit `1`
- `patch configmap` -> exit `1`
- `patch invalidkind <resource> -p {} -n default` -> exit `1`

### Verb: `kubectl scale` (across 13 kinds: ConfigMap, CronJob, DaemonSet, Deployment, Ingress, Job, Namespace, PersistentVolumeClaim, ReplicaSet, Secret, Service, ServiceAccount, StatefulSet)

**Interface — observed argv patterns:**

- `scale deployment <resource> --replicas=3 -n default`
- `scale deployment <resource> --replicas=1 -n default`
- `scale deployment <resource> --replicas=0 -n default`
- `scale deployment <resource> --replicas=5 -n default`
- `scale deployment <resource> --replicas=10 -n default`
- `scale deployment <resource> --replicas=2 --namespace default`
- `scale deployment <resource> --replicas=2 -n kube-system`
- `scale deployment <resource> --replicas=2`
- `scale statefulset <resource> --replicas=2 -n default`
- `scale statefulset <resource> --replicas=3 -n default`
- `scale statefulset <resource> --replicas=0 -n default`
- `scale statefulset <resource> --replicas=1`
- `scale deployment nonexistent-f258efe4 --replicas=2 -n default`
- `scale statefulset nonexistent-f258efe4 --replicas=2 -n default`
- `scale deployment nonexistent-f258efe4 --replicas=3`
- `scale deployment <resource> --invalid-flag`
- `scale deployment <resource> -n default`
- `scale`
- `scale deployment`
- `scale configmap <resource> --replicas=2 -n default`

**Flags (real kubectl v1.31 — support all):**

| Flag | Example value |
|---|---|
| `--current-replicas` | _(boolean)_ |
| `--invalid-flag` | _(boolean)_ |
| `--namespace` | `default` |
| `--replicas` | `3` |
| `--resource-version` | _(boolean)_ |
| `-n/--namespace` | _(v1.31)_ |

**Behavior:**

- Sets the replica count of a scalable workload (Deployment, StatefulSet, ReplicaSet) via `patch_<kind>_scale` or an equivalent PATCH to `/scale`.
- After `scale deployment <name> --replicas=N`, `read_namespaced_deployment` MUST return `.spec.replicas == N`.
- Success stdout is real-kubectl shape: `deployment.apps/<name> scaled`.
- `--replicas <n>` is REQUIRED; a missing or malformed replica count FAILS with exit `1` or `2` (per the exit-code table) and stderr containing `invalid` / `required`.
- Scaling a non-existent workload FAILS with exit `1` and stderr containing `NotFound`.
- Scaling to `0` is legal and MUST succeed; the deployment's spec-replica count reads back as `0`.
- Scale operates only on workload kinds (Deployment, StatefulSet, ReplicaSet); scaling any other kind FAILS with exit `1` and stderr containing `NotFound` or `unsupported`.

**Error cases observed:**

- `scale deployment nonexistent-f258efe4 --replicas=2 -n default` -> exit `1`
- `scale statefulset nonexistent-f258efe4 --replicas=2 -n default` -> exit `1`
- `scale deployment nonexistent-f258efe4 --replicas=3` -> exit `1`
- `scale deployment <resource> --invalid-flag` -> exit `2`
- `scale deployment <resource> -n default` -> exit `1`
- `scale` -> exit `1`
- `scale deployment` -> exit `1`
- `scale configmap <resource> --replicas=2 -n default` -> exit `1`

## Cross-command behaviour (state must stay consistent)

Kubernetes API state persists across kubectl commands within a task session.

State must remain consistent across the verb set:

- The kwok apiserver persists every mutation to etcd via kine, so the
  effect of any successful mutation MUST be immediately observable via
  the corresponding read verb (`get`, `describe`) or client method
  (`read_<kind>`, `list_<kind>`).
- After `create <kind> <name>` (or `apply -f manifest.yaml`), a follow-up
  `get <kind> <name>` returns the resource; `read_<kind>` on the same
  name succeeds. `apply` is idempotent — re-applying the same manifest
  is a no-op with respect to spec fields.
- After `delete <kind> <name>`, the resource disappears from
  `list_<kind>` and `read_<kind>` raises `ApiException` with
  `.status == 404`. Deleting the same name a second time FAILS with
  `NotFound` (unlike some AWS delete APIs, kubectl delete is NOT
  idempotent by default).
- After `patch <kind>/<name>` or `label <kind>/<name>`, `read_<kind>`
  reflects the mutated fields; unmodified fields keep their prior value
  (strategic-merge semantics for built-in kinds).
- After `scale <workload>/<name> --replicas=N`, `read_<workload>(name)` returns
  `.spec.replicas == N`.
- Read verbs (`get`, `describe`) never mutate state; two consecutive
  reads over an unchanged cluster return the same set of names
  (order-independent).

## Implementation constraints

- Your submission may be written in any language available in the image.
  Use only what the image already provides; no additional packages may be
  fetched.
- Do NOT shell out to the real `kubectl` binary from inside your program.
- The kwok cluster exposes a standard Kubernetes REST API on the endpoint
  configured in `$KUBECONFIG`. Use any client library idiomatic for your
  language, or speak the Kubernetes REST API directly.
- Read `KUBECONFIG` from the environment; the runtime configures it to point
  at a sandboxed kwok cluster. Do NOT override the apiserver endpoint,
  credentials, or context in code.
- Success messages go to **stdout**; errors go to **stderr**. Do NOT mix them.
- Exit codes are STRICT and must match real kubectl semantics. The
  test-enforced set is `{0, 1, 2}`; signal codes `{130, 137, 143}`
  are runtime-inherited and MUST NOT be produced deliberately:
  - `0` on success.
  - `1` on any apiserver-shaped API error (404 `NotFound`,
    409 `Conflict`, 409 `AlreadyExists`, 422 `Invalid`,
    401 `Unauthorized`, 403 `Forbidden`, 405 `MethodNotAllowed`,
    410 `Gone`, 413 `RequestEntityTooLarge`, 415
    `UnsupportedMediaType`, 429 `TooManyRequests`, 500
    `InternalError`, 503 `ServiceUnavailable`, `Timeout`,
    `ServerTimeout`), on TCP-level cluster-unreachable failures
    (DNS, connection refused, TLS mismatch, read timeout), and on
    kubeconfig / configuration errors (unreadable `KUBECONFIG`,
    missing current-context, unresolvable cluster server URL).
  - `2` on cobra / argparse usage errors: unknown flag, missing
    required positional, extra positional, malformed flag value,
    invalid subcommand, mutually-exclusive flag combination,
    invalid `-o` / `--output` format selector, invalid
    `--replicas` / `--port` numeric value, invalid `--patch-type`
    selector, missing required `--all` when no name is given,
    invalid label syntax that fails client-side parsing.
  - `130` on `SIGINT` (`Ctrl+C`); `137` on `SIGKILL` (typically
    OOM); `143` on `SIGTERM`. Runtime-inherited only.
  Tests enforce the SPECIFIC code — `returncode == 1` for
  apiserver / configuration errors and `returncode == 2` for
  usage errors. Returning the wrong non-zero code will fail
  verification.
- Do NOT surface raw runtime tracebacks or internal error dumps; print a
  brief user-facing error string that names the failure class instead
  (for example, `NotFound (404)` or `Invalid: ...`).
- Do NOT fabricate flags that don't exist upstream. In particular,
  `kubectl apply` has NO `--wait-for` flag (only `--wait`).
- Do NOT validate resource names client-side; the apiserver rejects
  DNS-1123-invalid names with `Invalid`. Defer to the server.
- Do NOT implement or delegate to the unsupported verbs `logs`, `exec`,
  `port-forward`, `attach`, `top`, `cp` — kwok returns synthetic data for
  these and no test will exercise them.
- Your submission must be an executable at `/workspace/submission/kubectl`
  (any language — shebang script or compiled binary). The image provides
  `/workspace/submission/` first on `$PATH`, so the executable shadows the
  real `/usr/local/bin/kubectl` for the test harness.

## Output contract

A correct implementation produces output in the *shape* described below,
names the *class* of any error reported, uses the documented exit-code set,
and never surfaces a runtime stack trace. Specific verbs, error codes, and
the exact wording of any message are deliberately not enumerated here:
derive them from the underlying Kubernetes API semantics and standard
`kubectl` conventions.

### stdout (success path)

- A successful mutation writes one line per affected resource. `create`,
  `apply`, `patch`, `scale`, `label`, `annotate`, `rollout` use the shape
  `<kind>/<name> <verb-past-tense>` (for example, `configmap/foo created`,
  `deployment.apps/bar scaled`). `delete` uses a DIFFERENT shape:
  `<kind> "<name>" deleted` (for example, `namespace "baz" deleted`,
  `configmap "foo" deleted`). The `<kind>` fragment may be short (`configmap`) or
  qualified (`deployment.apps`); both are acceptable to the tests.
- `kubectl get` (default output) writes a human-readable table with a header
  row and one line per resource. `-o json` / `-o yaml` write a
  machine-parseable document.
- `kubectl describe` writes a multi-section report (section headers end
  with `:` — `Name:`, `Namespace:`, `Labels:`, `Annotations:`, `Status:`,
  `Events:`).
- Implementations MAY emit informational progress lines BEFORE the success
  line (for example, `Waiting for deployment "foo" rollout to finish...`).
  Conformance is checked by looking for the success line anywhere in stdout,
  not as the first line.
- stderr is empty on success.

### stderr (failure path)

- stdout is empty on failure.
- A human-readable error line is written to stderr that identifies the
  failure *class*. Any of the following shapes is acceptable:
  - the underlying apiserver error envelope surfaced as
    `<reason> (<status>)` (for example, `NotFound (404)`,
    `AlreadyExists (409)`, `Invalid (422)`)
  - a bare `<reason>: <message>` line naming the apiserver error reason
    (`NotFound`, `AlreadyExists`, `Invalid`, `Forbidden`, `Conflict`,
    `Timeout`)
  - a client-side usage-error line whose prefix names the failure class
    (for example, `Error: unknown flag: --nope`, `error: resource(s) were
    not provided`, `invalid argument "..."`)
- Tests match the failure *class* against one of these shapes — not
  verbatim wording — so any spec-compliant phrasing is accepted.
- No runtime stack trace is emitted under any condition.

### Exit codes

The test-enforced exit-code set is `{0, 1, 2}`; process signals may
surface as `{130, 137, 143}` and MUST NOT be produced deliberately:

- `0` — success.
- `1` — apiserver / API error surfaced from an `ApiException` or the
  underlying REST client. All of the following apiserver reasons map
  to exit `1`: `NotFound`, `AlreadyExists`, `Invalid`, `Forbidden`,
  `Unauthorized`, `Conflict`, `Timeout`, `ServerTimeout`,
  `TooManyRequests`, `InternalError`, `ServiceUnavailable`,
  `MethodNotAllowed`, `UnsupportedMediaType`, `Gone`,
  `RequestEntityTooLarge`. TCP-level cluster-unreachable failures
  (DNS, connection refused, TLS mismatch, read timeout) also exit
  `1`. Kubeconfig / configuration errors (unreadable `KUBECONFIG`,
  missing current-context, unresolvable cluster server URL) also
  exit `1`.
- `2` — cobra / argparse usage error: unknown flag, missing or extra
  positional argument, malformed flag value, invalid subcommand,
  mutually-exclusive flag combination, invalid `-o` / `--output`
  format selector, invalid `--replicas` / `--port` numeric value,
  invalid `--patch-type` selector, missing required `--all` when no
  name is given, invalid label syntax that fails client-side parsing.
- `130` — process interrupted by `SIGINT` (`Ctrl+C`); inherited from
  the runtime, do NOT emit deliberately.
- `137` — process killed by `SIGKILL` (typically OOM); inherited from
  the runtime, do NOT emit deliberately.
- `143` — process terminated by `SIGTERM`; inherited from the runtime,
  do NOT emit deliberately.

Tests must produce the SPECIFIC exit code for each modeled error class —
`returncode == 1` for apiserver / configuration errors and
`returncode == 2` for usage errors. Returning the wrong non-zero code
fails verification.

