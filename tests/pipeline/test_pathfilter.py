import pytest

from pipeline.pathfilter import matches, starts_workflow

IGNORE = ["docs/**", "**.md"]


@pytest.mark.parametrize(
    ("path", "pattern", "expected"),
    [
        ("docs/index.md", "docs/**", True),
        ("docs/adr/0001-x.md", "docs/**", True),
        ("src/docs/index.md", "docs/**", False),
        ("README.md", "**.md", True),
        ("src/notes/a.md", "**.md", True),
        ("src/mathkit/__init__.py", "**.md", False),
        ("src/mathkit/a.py", "src/*.py", False),
        ("src/a.py", "src/*.py", True),
        ("a.yml", "*.y?ml", True),
        ("a.ml", "*.y?ml", True),
        ("a.yaml", "*.y?ml", False),
        ("a.py", "[ab].py", True),
        ("c.py", "[ab].py", False),
    ],
)
def test_glob_patterns_follow_the_documented_syntax(path, pattern, expected):
    assert matches(path, [pattern]) is expected


def test_a_documentation_only_change_starts_nothing():
    assert starts_workflow(["docs/index.md", "README.md"], paths_ignore=IGNORE) is False


def test_a_change_under_the_source_starts_the_workflow():
    assert starts_workflow(["src/mathkit/domain/arithmetic.py"], paths_ignore=IGNORE) is True


def test_a_mixed_change_starts_the_workflow():
    assert starts_workflow(["docs/index.md", "src/mathkit/__init__.py"], paths_ignore=IGNORE) is True


def test_paths_starts_the_workflow_when_one_file_matches():
    assert starts_workflow(["docs/a.md", "x.py"], paths=["docs/**"]) is True
    assert starts_workflow(["x.py"], paths=["docs/**"]) is False


def test_no_filter_always_starts():
    assert starts_workflow(["anything"]) is True


def test_both_filters_on_one_event_are_rejected():
    with pytest.raises(ValueError, match="together"):
        starts_workflow(["a"], paths=["a"], paths_ignore=["b"])
