import runpy
from pathlib import Path


def test_explicit_driver_does_not_require_a_local_checkout_or_path(monkeypatch, tmp_path):
    driver = str(tmp_path / "venv/bin/pymcu")
    monkeypatch.setenv("PYMCU_BIN", driver)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr("shutil.which", lambda name: None)
    module = runpy.run_path(str(Path(__file__).parent / "corpus/test_corpus.py"))
    assert module["DEFAULT_PYMCU"] == driver
