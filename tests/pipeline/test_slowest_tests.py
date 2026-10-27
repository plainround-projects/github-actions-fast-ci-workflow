from pipeline import slowest_tests

REPORT = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" tests="3">
<testcase classname="tests.unit.test_a" name="test_fast" time="0.001"/>
<testcase classname="tests.unit.test_a" name="test_slow" time="1.250"/>
<testcase classname="tests.unit.test_b" name="test_middle" time="0.300"/>
</testsuite></testsuites>
"""


def test_the_slowest_tests_come_first(tmp_path):
    report = tmp_path / "report.xml"
    report.write_text(REPORT, encoding="utf-8")
    assert [name for name, _ in slowest_tests.slowest(report, count=2)] == [
        "tests.unit.test_a::test_slow",
        "tests.unit.test_b::test_middle",
    ]


def test_the_table_is_markdown(tmp_path):
    report = tmp_path / "report.xml"
    report.write_text(REPORT, encoding="utf-8")
    text = slowest_tests.markdown(slowest_tests.slowest(report))
    assert text.startswith("### Slowest tests")
    assert "| `tests.unit.test_a::test_slow` | 1.250 |" in text


def test_main_prints_the_table(tmp_path, capsys):
    report = tmp_path / "report.xml"
    report.write_text(REPORT, encoding="utf-8")
    assert slowest_tests.main([str(report)]) == 0
    assert "Slowest tests" in capsys.readouterr().out


def test_main_without_a_path_is_a_usage_error(capsys):
    assert slowest_tests.main([]) == 2
    assert "usage" in capsys.readouterr().err
