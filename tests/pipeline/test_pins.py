from pipeline import pins

SHA = "a" * 40


def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_a_full_sha_a_local_path_and_a_digest_are_pinned():
    assert pins.is_pinned(f"actions/checkout@{SHA}")
    assert pins.is_pinned("./.github/actions/setup")
    assert pins.is_pinned("docker://rhysd/actionlint@sha256:" + "b" * 64)


def test_a_tag_a_branch_and_a_short_sha_are_not_pinned():
    assert not pins.is_pinned("actions/checkout@v4")
    assert not pins.is_pinned("actions/checkout@main")
    assert not pins.is_pinned("actions/checkout@abc1234")


def test_violations_name_the_file_and_the_reference(tmp_path):
    write(
        tmp_path,
        ".github/workflows/a.yml",
        f"jobs:\n  j:\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/cache@{SHA}\n",
    )
    assert pins.violations(tmp_path) == [".github/workflows/a.yml: actions/checkout@v4"]


def test_job_level_uses_and_composite_action_steps_are_checked(tmp_path):
    write(tmp_path, ".github/workflows/b.yml", "jobs:\n  call:\n    uses: org/repo/.github/workflows/x.yml@v1\n")
    write(
        tmp_path,
        ".github/actions/t/action.yml",
        "runs:\n  using: composite\n  steps:\n    - uses: actions/setup-python@v5\n",
    )
    assert len(pins.violations(tmp_path)) == 2


def test_main_exits_1_on_a_violation_and_0_when_clean(tmp_path, capsys):
    write(tmp_path, ".github/workflows/a.yml", "jobs:\n  j:\n    steps:\n      - uses: actions/checkout@v4\n")
    assert pins.main([str(tmp_path)]) == 1
    assert "not pinned" in capsys.readouterr().err
    write(tmp_path, ".github/workflows/a.yml", f"jobs:\n  j:\n    steps:\n      - uses: actions/checkout@{SHA}\n")
    assert pins.main([str(tmp_path)]) == 0
