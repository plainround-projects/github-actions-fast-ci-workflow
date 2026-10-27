# pandas

## What it is

pandas is a Python library for tables of data. Its main object is the **DataFrame**: rows and named columns, like a spreadsheet in memory. It can read a CSV file ("comma separated values": lines of text with commas between the cells) into a DataFrame in one call. This repository pins pandas 2.2.3.

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **repository**: A project's folder of files together with its complete history of changes. On GitHub, a repository is a page with those files, issues and pull requests.
- **library**: A package of ready-made code that your program calls.
- **dependency**: A package that your project needs in order to work.
- **cache**: A saved copy of something slow to produce (such as downloaded packages), kept so the next run can reuse it.
- **module**: A file, or a folder of files, that other code can load and use. In Terraform, a module is a folder of configuration used like a function.
- **array**: An ordered list of values.
- **string**: A piece of text in a program.
- **port**: A number that names one of the doors of a computer on the network; a server listens on a port.
- **version**: A number such as `1.2.3` that names one release of software (major.minor.patch).
- **test**: A small program that uses your code and checks that the answer is the one you expected.
- **comprehension**: A short way to build a list, set or dictionary from a loop in one expression, such as `[x * 2 for x in items if x > 0]`.
- **exception**: An error raised while a program runs (`raise ValueError("message")`). Code can catch it with `try`/`except`; if nobody catches it the program stops.
- **CSV**: Comma-separated values: a plain-text table, one row per line, cells separated by commas.

</details>

<!-- /words -->

## Why this repository uses it

The lesson wants a heavy dependency so the dependency cache has something to save: installing numpy and pandas takes a long time without a cache. To make pandas do real work, `mathkit` has a feature that reads a CSV and summarizes its numeric columns.

## Where it appears

| Path | What it does with pandas |
| --- | --- |
| `src/mathkit/infrastructure/pandas_source.py` | Parses CSV text and returns the numeric columns. The only module that imports pandas. |
| `tests/integration/test_pandas_source.py` | Tests the adapter against the real library. |
| `pyproject.toml`, `requirements.in`, `requirements.txt` | The pin `pandas==2.2.3`. |
| `pyproject.toml` (mypy override) | Tells mypy to ignore the missing type information of pandas. |
| `.importlinter` contract in `pyproject.toml` | Forbids the domain and application layers from importing pandas. |

## How it works underneath

`pd.read_csv(file_like)` reads text, splits lines and commas, guesses a type for each column (whole numbers become `int64`, decimals `float64`, anything else `object`), and builds a DataFrame. Missing cells become `NaN` ("not a number"). A DataFrame stores each column as a NumPy array (see `numpy.md`).

## Walkthrough of this repository's use

```python
class PandasColumnSource:
    def numeric_columns(self, table_text: str) -> dict[str, tuple[float, ...]]:
        try:
            frame = pd.read_csv(io.StringIO(table_text))
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
            raise InvalidTableError(f"not a CSV table: {error}") from error
        numeric = frame.select_dtypes(include=[np.number])
        return {
            str(name): tuple(float(value) for value in numeric[name].dropna().to_numpy())
            for name in numeric.columns
        }
```

- `io.StringIO(table_text)` wraps a string so it behaves like a file; `read_csv` accepts any file-like object.
- `pd.errors.EmptyDataError` and `ParserError` are what pandas raises for empty or malformed text. The adapter converts them into the repository's own `InvalidTableError`, so callers never see pandas types.
- `raise ... from error` keeps the original error as the cause.
- `frame.select_dtypes(include=[np.number])` keeps only numeric columns, so a `name` text column is dropped.
- `numeric[name].dropna()` removes missing values from that column; `.to_numpy()` gives a NumPy array.
- The dict comprehension builds `{column name: tuple of Python floats}`. Converting to plain `float` means the domain code never touches NumPy types.

The use case `SummarizeTable` receives this adapter through the `ColumnSource` port, and the unit tests give it a fake instead.

## Try it yourself

1. `.venv/bin/python -c "import pandas as pd; print(pd.__version__)"` prints `2.2.3`.
2. `.venv/bin/python -c "import pandas as pd, io; f=pd.read_csv(io.StringIO('a,b\n1,x\n2,y\n')); print(f.dtypes)"` shows `a int64` and `b object`.
3. `printf 'x,y\n1,10\n3,20\n' > /tmp/t.csv && .venv/bin/python -m mathkit summarize /tmp/t.csv` prints one summary line per numeric column.
4. `.venv/bin/lint-imports` reports the contract "Domain and application know nothing about pandas or numpy" as KEPT.

## Mistakes people make

- Importing pandas in business logic so every test needs it.
- Assuming a column of numbers stays numeric when one cell holds text; the column becomes `object`.
- Forgetting missing values (`NaN`) and getting a `NaN` mean.
- Letting library exception types leak out of the adapter.

## Check yourself

1. What is a DataFrame? *(A table with rows and named columns in memory.)*
2. Why wrap the text in `io.StringIO`? *(`read_csv` expects a file-like object.)*
3. What does `select_dtypes(include=[np.number])` do? *(Keeps only the numeric columns.)*
4. Why convert to Python floats? *(So the rest of the code needs neither pandas nor NumPy.)*
5. Which test would fail if the adapter let `ParserError` escape? *(The one that expects `InvalidTableError` for empty text.)*

## Further reading

- pandas 2.2 documentation: https://pandas.pydata.org/pandas-docs/version/2.2.3/
- `read_csv`: https://pandas.pydata.org/pandas-docs/version/2.2.3/reference/api/pandas.read_csv.html
