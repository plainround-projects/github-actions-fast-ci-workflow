import hashlib

from pipeline import cache_key


def test_the_hash_is_a_sha256_of_the_file_digest_like_hashfiles(tmp_path):
    lock = tmp_path / "requirements.txt"
    lock.write_bytes(b"numpy==2.1.3\n")
    inner = hashlib.sha256(b"numpy==2.1.3\n").digest()
    assert cache_key.hash_files([lock]) == hashlib.sha256(inner).hexdigest()


def test_the_key_names_the_os_architecture_python_and_hash(tmp_path):
    lock = tmp_path / "requirements.txt"
    lock.write_text("pandas==2.2.3\n", encoding="utf-8")
    key = cache_key.setup_python_key("Linux", "x64", "3.12.7", lock)
    assert key.startswith("setup-python-Linux-x64-python-3.12.7-pip-")
    assert key.endswith(cache_key.hash_files([lock]))


def test_changing_one_pinned_version_changes_the_key_so_the_cache_misses(tmp_path):
    lock = tmp_path / "requirements.txt"
    lock.write_text("pandas==2.2.3\n", encoding="utf-8")
    before = cache_key.setup_python_key("Linux", "x64", "3.12.7", lock)
    lock.write_text("pandas==2.2.2\n", encoding="utf-8")
    assert cache_key.setup_python_key("Linux", "x64", "3.12.7", lock) != before


def test_the_same_file_gives_the_same_key_so_the_second_run_hits(tmp_path):
    lock = tmp_path / "requirements.txt"
    lock.write_text("pandas==2.2.3\n", encoding="utf-8")
    assert cache_key.setup_python_key("Linux", "x64", "3.12.7", lock) == cache_key.setup_python_key(
        "Linux", "x64", "3.12.7", lock
    )


def test_the_command_prints_the_key(tmp_path, capsys):
    lock = tmp_path / "requirements.txt"
    lock.write_text("x\n", encoding="utf-8")
    assert cache_key.main(["--file", str(lock), "--os", "Windows"]) == 0
    assert capsys.readouterr().out.startswith("setup-python-Windows-x64-python-3.12.7-pip-")
