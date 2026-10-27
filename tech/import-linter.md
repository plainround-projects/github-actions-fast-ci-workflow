# import-linter

## What it is

import-linter is a Python tool that checks which modules import which, and fails when a rule you wrote is broken. A **contract** is one such rule. It is the tool that turns an architecture diagram ("the domain must not know about the database") into a check that fails the build. This repository pins import-linter 2.1.

## Why this repository uses it

The template says the layering of the code must be visible in the folders and enforced by a tool. `mathkit` has four layers, and import-linter makes the dependency rule real: nothing in a lower layer may import from a higher one.

## Where it appears

| Path | What it does with import-linter |
| --- | --- |
| `pyproject.toml` | `[tool.importlinter]` and two `[[tool.importlinter.contracts]]` tables. |
| `Makefile` | `lint` runs `lint-imports`. |
| `src/mathkit/domain`, `application`, `infrastructure`, `interfaces` | The folders the contracts are written about. |

## How it works underneath

`lint-imports` reads the settings, finds the package named in `root_package`, and builds a **graph**: a node per module, an arrow from module A to module B when A imports B. Then it checks each contract against the graph. A **layers** contract says each layer may import only layers listed below it. A **forbidden** contract says modules in one set must not import modules in another, directly or through a chain of imports.

## Walkthrough of this repository's use

```toml
[tool.importlinter]
root_package = "mathkit"
include_external_packages = true
```

`include_external_packages = true` lets contracts mention third-party names such as `pandas`.

```toml
[[tool.importlinter.contracts]]
name = "Layers: interfaces -> infrastructure -> application -> domain, never upward"
type = "layers"
layers = ["mathkit.interfaces", "mathkit.infrastructure", "mathkit.application", "mathkit.domain"]
```

Listed from highest to lowest. `interfaces` may import anything below; `domain` imports none of the others. Adding `from mathkit.interfaces import cli` to a domain file breaks the contract.

```toml
[[tool.importlinter.contracts]]
name = "Domain and application know nothing about pandas or numpy"
type = "forbidden"
source_modules = ["mathkit.domain", "mathkit.application"]
forbidden_modules = ["pandas", "numpy"]
```

Neither layer may reach pandas or numpy, even through another module. Only `infrastructure/pandas_source.py` does.

## Try it yourself

1. `.venv/bin/lint-imports` prints both contracts as `KEPT` and `Contracts: 2 kept, 0 broken.`
2. Break it in a scratch copy of the repository: add `import mathkit.interfaces.cli` to `src/mathkit/domain/arithmetic.py` and run `.venv/bin/lint-imports`; it reports the first contract BROKEN with the import chain. Undo the change.
3. `.venv/bin/lint-imports --verbose` shows more detail.

## Mistakes people make

- Writing contracts that nothing checks in CI. This one runs in `make lint` and the CI lint job.
- Putting the layers in the wrong order.
- Forgetting `include_external_packages` and wondering why `pandas` is not recognized.

## Check yourself

1. What is a contract? *(A rule about imports that the tool checks.)*
2. Which layer may import which? *(Each layer may import only the layers below it in the list.)*
3. What does the forbidden contract protect? *(The domain and application from depending on pandas or numpy.)*
4. Does it catch indirect imports? *(Yes, it follows chains of imports.)*
5. Where does it run? *(`make lint`, therefore the CI lint job.)*

## Further reading

- import-linter 2.1: https://import-linter.readthedocs.io/en/v2.1/
