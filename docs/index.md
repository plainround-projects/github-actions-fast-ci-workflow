# mathkit documentation

mathkit is the small library the fast CI workflow tests. This folder is on purpose the thing the workflow ignores:
a change that touches only `docs/` or a `.md` file starts no test jobs.

- [Architecture decisions](adr/0001-one-gate-job-and-a-companion-for-docs-only-changes.md)
- [The measurement workflows](adr/0003-measure-each-stage-with-its-own-workflow.md)
- [How the dependency lock is made](adr/0002-hash-pinned-universal-lock-files.md)

## Using the library

```python
import mathkit

mathkit.add(2, 3)      # 5
mathkit.mean([1, 2, 3])  # 2.0
```

```text
python -m mathkit add 2 3
python -m mathkit summarize data.csv
```
