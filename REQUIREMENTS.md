**Pilot RL Environment Creation — AWS CLI (S3)**

This 2-pager describes a pilot task for a data partner to showcase their ability to create high-quality RL training environments for agentic code generation.

**RL Training Environment**

We train agentic code models using RL: the model receives user requirements (or a specification) and must produce a working application from scratch; the RL reward comes from automated test pass rates: tests are ***never shown*** to the model during generation — they validate output post-hoc.

**An RL environment consists of ([Harbor format](https://github.com/harbor-framework/harbor)):**

| Component | Description |
| :---- | :---- |
| instruction.md | Feature specification — commands, inputs, outputs, expected behaviors, error cases |
| Docker image | Containerized runtime with dependencies and service simulation layer |
| test.sh \+ test suite | E2E tests that validate produced code against the spec; return pass/fail counts |
| task.toml | Metadata (app name, language, tags) |

**Workflow:** model generates code → code placed in container → tests execute → pass rate \= reward signal.

**Pilot Task: AWS CLI — S3 Operations**

**Codebase**: [github.com/aws/aws-cli](https://github.com/aws/aws-cli) (public, Python, \~333K LOC / 8,940 files — mostly auto-generated service models; scoped subset is much smaller).

**Scope**: A CLI tool implementing a subset of S3 operations

| Command | Behavior |
| :---- | :---- |
| s3 mb | Make or create a bucket |
| s3 rb | Remove a bucket |
| s3 cp | Upload local→S3, download S3→local, copy S3→S3 |
| s3 ls | List buckets or objects in a bucket |
| s3 mv | Move objects (copy \+ delete source) |
| s3 rm | Remove objects |
| s3 sync | Sync local directory ↔ S3 path |

**Why this task:** Real CLI app requiring argument parsing, service simulation (stateful), output formatting, and state persistence validation. Exercises both CLI UX and back-end (API interactions, state management, error handling).

**Deliverables**

1. **Feature Specification** (instruction.md) — Overall description of the application and intended features (i.e., S3 operations) and structured description of each command: interface, expected I/O, error behavior, cross-command state expectations (e.g., *"after cp uploads a file, ls must show it, cp back must retrieve identical content"*).

2. **Docker image** — Container with:

   1. Language runtime (Python)

   2. A service simulation layer enabling E2E testing without real AWS accounts (example approaches — mock server, intercepted APIs, local service emulation)

   3. All test dependencies

   4. Accepts *any* implementation placed in a designated directory (container is implementation-agnostic)

3. **E2E test suite** — Tests covering:

   1. Individual command happy paths

   2. Error/edge cases (invalid args, non-existent resources)

   3. Cross-command workflows validating state persistence (upload → list → download → content match)

   4. Single test.sh entry point reporting pass/fail counts

**Quality Metrics**

| Metric | Expectation |
| :---- | :---- |
| **Number of E2E tests** | Sufficient to cover all 7 commands \+ their interactions; count should follow from feature coverage |
| **Feature coverage** | Tests exercise all specified commands and their documented behaviors (happy path \+ error cases) |
| **Pass rate on correct implementation** | \~100% — tests must be solvable (validated against original aws-cli or a reference impl) |
| **Pass rate on empty/no-op submission** | \~0% — tests must be discriminative |
| **State persistence coverage** | Tests include cross-command compositions verifying stateful behavior |
| **Container reliability** | Builds and runs cleanly from scratch on a fresh machine |
| **Service simulation fidelity** | Correct status codes, error shapes, consistent state |

We will additionally run a reference model at multiple sample budgets (pass@k) to calibrate difficulty.

**Success Criteria**

1. Working, containerized RL environment delivered for the specified scope

2. Tests are meaningful, discriminative, and pass on a correct implementation

3. Environment integrates into our training pipeline with minimal adaptation

4. Partner demonstrates a credible path to scaling (one → many environments)

**Design Choices**

1. **Dependency scope**: For this initial pilot, the implemented CLI may use botocore (AWS SDK core) as a dependency. This focuses the task on CLI logic — argument parsing, output formatting, transfer orchestration — rather than reimplementing service protocol details.

2. **Mocking vs. real services**: The service simulation approach is open. Some behaviors may be faithfully mocked; others may benefit from real containerized services. What are the trade-offs between fidelity, complexity, and reproducibility? How does this affect test reliability?

3. **Scaling**: If this pilot succeeds, how would you approach generating 10+ similar environments for different CLI tools or service families?

