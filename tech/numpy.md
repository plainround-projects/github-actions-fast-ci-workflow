# NumPy

## What it is

NumPy is a Python library for fast arrays of numbers. An **array** is a block of memory holding many numbers of one type, with operations that work on the whole block at once. pandas is built on it. This repository pins NumPy 2.1.3.

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **repository**: A project's folder of files together with its complete history of changes. On GitHub, a repository is a page with those files, issues and pull requests.
- **package**: In Python, a folder with an `__init__.py` file that can be imported as a unit; also a bundle of code installed with pip.
- **dependency**: A package that your project needs in order to work.
- **lock file**: A file that records the exact version, and a checksum, of every package that was installed, so that everyone installs exactly the same thing.
- **cache**: A saved copy of something slow to produce (such as downloaded packages), kept so the next run can reuse it.

</details>

<!-- /words -->

## Why this repository uses it

NumPy is a dependency of pandas, so it is always installed with it. It is also imported directly, in one place: to say which columns count as numeric. It stays in the lock file as a deliberately heavy package for the cache to save.

## Where it appears

| Path | What it does with NumPy |
| --- | --- |
| `src/mathkit/infrastructure/pandas_source.py` | `import numpy as np`, then `np.number` and `.to_numpy()`. |
| `pyproject.toml`, `requirements*.txt` | The pin `numpy==2.1.3`. |
| import-linter contract | Domain and application may not import it. |

## How it works underneath

A NumPy array is stored as one contiguous piece of memory plus a description of the element type (`int64`, `float64`). Operations run in compiled C code over the whole piece, which is much faster than a Python loop. `np.number` is not an array but a **type group**: the parent of every numeric type (ints, floats, complex), which is how code asks "is this column numeric?".

## Walkthrough of this repository's use

```python
numeric = frame.select_dtypes(include=[np.number])
```

Asks pandas for the columns whose type is any NumPy numeric type.

```python
tuple(float(value) for value in numeric[name].dropna().to_numpy())
```

`.to_numpy()` turns a pandas column into a NumPy array. Looping over it yields NumPy numbers (`numpy.float64`); `float(value)` converts each to a plain Python float so callers never see NumPy types.

## Try it yourself

1. `.venv/bin/python -c "import numpy as np; print(np.__version__)"` prints `2.1.3`.
2. `.venv/bin/python -c "import numpy as np; a=np.array([1,2,3]); print(a.dtype, a*2)"` prints `int64 [2 4 6]`.
3. `.venv/bin/python -c "import numpy as np; print(issubclass(np.float64, np.number), issubclass(str, np.number))"` prints `True False`.

## Mistakes people make

- Mixing NumPy numbers and Python numbers and being surprised by overflow or by `repr` differences.
- Using Python loops over big arrays instead of whole-array operations.
- Importing it in code that does not need it.

## Check yourself

1. What is an array? *(A block of numbers of one type with whole-block operations.)*
2. What is `np.number`? *(The parent type of all numeric NumPy types.)*
3. Why `float(value)`? *(To hand plain Python floats to the domain.)*
4. Which library is built on NumPy? *(pandas.)*
5. Which layers may not import it? *(Domain and application.)*

## Further reading

- NumPy 2.1 documentation: https://numpy.org/doc/2.1/
