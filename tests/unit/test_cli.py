import pytest

from mathkit.interfaces.cli import main


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["add", "2", "3"], "5"),
        (["subtract", "2", "3"], "-1"),
        (["multiply", "2", "3"], "6"),
        (["divide", "1", "4"], "0.25"),
    ],
)
def test_an_operation_prints_its_result(argv, expected, capsys):
    assert main(argv) == 0
    assert capsys.readouterr().out.strip() == expected


def test_division_by_zero_exits_1_with_a_message(capsys):
    assert main(["divide", "1", "0"]) == 1
    assert "zero" in capsys.readouterr().err


def test_a_missing_file_exits_1_with_a_message(capsys, tmp_path):
    assert main(["summarize", str(tmp_path / "missing.csv")]) == 1
    assert "cannot read" in capsys.readouterr().err


def test_no_command_is_a_usage_error():
    with pytest.raises(SystemExit) as raised:
        main([])
    assert raised.value.code == 2
