import runpy
from pathlib import Path


def test_explicit_driver_does_not_require_a_local_checkout_or_path(monkeypatch, tmp_path):
    driver = str(tmp_path / "venv/bin/pymcu")
    monkeypatch.setenv("PYMCU_BIN", driver)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr("shutil.which", lambda name: None)
    module = runpy.run_path(str(Path(__file__).parent / "corpus/test_corpus.py"))
    assert module["DEFAULT_PYMCU"] == driver


def _load_suite(monkeypatch, tmp_path, *, interpreter, which):
    """Run the corpus module with a chosen interpreter and PATH answer, no PYMCU_BIN."""
    monkeypatch.delenv("PYMCU_BIN", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr("shutil.which", lambda name: which)
    monkeypatch.setattr("sys.executable", str(interpreter))
    return runpy.run_path(str(Path(__file__).parent / "corpus/test_corpus.py"))


def test_default_driver_is_the_one_beside_the_running_interpreter(monkeypatch, tmp_path):
    venv_bin = tmp_path / "active-venv/bin"
    venv_bin.mkdir(parents=True)
    (venv_bin / "python").write_text("")
    (venv_bin / "pymcu").write_text("")
    module = _load_suite(monkeypatch, tmp_path, interpreter=venv_bin / "python", which=None)
    assert module["DEFAULT_PYMCU"] == str(venv_bin / "pymcu")


def test_no_fixed_checkout_is_consulted(monkeypatch, tmp_path):
    """A driver under ~/Repos/PyMCU must not be picked up: the answer comes from the
    running environment, and this test's home has no such checkout to find."""
    checkout_venv = tmp_path / "Repos/PyMCU/.venv/bin"
    checkout_venv.mkdir(parents=True)
    (checkout_venv / "pymcu").write_text("")
    module = _load_suite(monkeypatch, tmp_path, interpreter=tmp_path / "elsewhere/python", which=None)
    assert module["DEFAULT_PYMCU"] is None


def test_a_driver_on_path_is_used_when_the_interpreter_has_none(monkeypatch, tmp_path):
    module = _load_suite(monkeypatch, tmp_path, interpreter=tmp_path / "bare/python",
                         which="/opt/tools/pymcu")
    assert module["DEFAULT_PYMCU"] == "/opt/tools/pymcu"


def test_no_driver_anywhere_leaves_the_default_empty(monkeypatch, tmp_path):
    module = _load_suite(monkeypatch, tmp_path, interpreter=tmp_path / "bare/python", which=None)
    assert module["DEFAULT_PYMCU"] is None
