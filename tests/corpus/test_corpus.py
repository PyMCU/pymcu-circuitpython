import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CORPUS = Path(__file__).resolve().parent
PROGRAMS = CORPUS / "programs"
TEMPLATE = CORPUS / "_template"
SIZES = CORPUS / "sizes.json"


def _default_pymcu() -> str:
    """Locate the `pymcu` driver without hardcoding a path into one developer's own
    project. A user project (like the old cp-hcsr04 wheel checkout this used to point
    at) must never be a test dependency: it can be renamed, moved or deleted by its
    owner without anyone touching this suite noticing why builds started failing.

    Resolution order: PyMCU's own repo checkout venv first (this suite's compiler of
    record: it editable-installs pymcu-stdlib and pymcu-circuitpython from their
    working trees, so a source change is what this suite measures), then whatever
    `pymcu` PATH finds otherwise, which is where a released/pipx install can be
    older than the repo checkout and would silently measure the wrong compiler if
    tried first. PYMCU_BIN overrides both, for CI or a different layout.
    """
    repo_venv = Path.home() / "Repos" / "PyMCU" / ".venv" / "bin" / "pymcu"
    if repo_venv.is_file():
        return str(repo_venv)
    on_path = shutil.which("pymcu")
    if on_path:
        return on_path
    raise RuntimeError(
        "no `pymcu` driver found at ~/Repos/PyMCU/.venv/bin/pymcu or on PATH; "
        "set PYMCU_BIN to the driver you want the corpus suite to build with."
    )


DEFAULT_PYMCU = os.environ.get("PYMCU_BIN") or _default_pymcu()

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
EXPECT_RE = re.compile(r"^# expect: (build|refuse)(?: (.*))?$")

_MEASURED_SIZES = {}


def _programs():
    return sorted(PROGRAMS.glob("*.py"))


def _expectation(program):
    lines = program.read_text(encoding="utf-8").splitlines()
    if len(lines) < 2:
        raise AssertionError(f"{program.name} needs expect and source headers")
    match = EXPECT_RE.match(lines[0])
    if not match:
        raise AssertionError(f"{program.name} has no '# expect:' header")
    if not lines[1].startswith("# source: "):
        raise AssertionError(f"{program.name} has no '# source:' header")
    return match.group(1), match.group(2) or ""


def _clean(output):
    return ANSI_RE.sub("", output).replace("\r", "\n")


def _diagnostic_line(output):
    cleaned = _clean(output)
    fallback = ""
    for raw in cleaned.splitlines():
        line = raw.strip()
        if not line:
            continue
        if not fallback and not line.startswith(("Done!", "Flash:", "Build successful!")):
            fallback = line
        if any(marker in line for marker in ("Error", "CompileError", "Traceback", "Exception")):
            return line
    return fallback


def _flash_bytes(hex_file):
    total = 0
    for line in hex_file.read_text(encoding="ascii").splitlines():
        if not line.startswith(":"):
            continue
        count = int(line[1:3], 16)
        record_type = int(line[7:9], 16)
        if record_type == 0:
            total += count
    return total


def _build(tmp_path, program):
    project = tmp_path / program.stem
    shutil.copytree(TEMPLATE, project)
    (project / "src").mkdir(exist_ok=True)   # git does not keep the empty src/ of the template
    shutil.copy2(program, project / "src" / "main.py")

    env = os.environ.copy()
    env["PYTHONPATH"] = (
        str(ROOT / "src")
        + os.pathsep
        + env.get("PYTHONPATH", "")
    ).rstrip(os.pathsep)

    pymcu = env.get("PYMCU_BIN", DEFAULT_PYMCU)
    result = subprocess.run(
        [pymcu, "build"],
        cwd=project,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60,
        check=False,
    )
    hex_file = project / "dist" / "firmware.hex"
    bytes_used = _flash_bytes(hex_file) if result.returncode == 0 and hex_file.exists() else None
    return result.returncode == 0, bytes_used, _diagnostic_line(result.stdout), _clean(result.stdout)


@pytest.mark.parametrize("program", _programs(), ids=lambda p: p.name)
def test_corpus_program(program, tmp_path, request):
    expected, substring = _expectation(program)
    ok, bytes_used, diagnostic, output = _build(tmp_path, program)

    if expected == "build":
        assert ok, f"{program.name} was refused: {diagnostic}\n\n{output}"
        assert bytes_used is not None
        _MEASURED_SIZES[program.name] = bytes_used

        if request.config.getoption("--update-sizes"):
            SIZES.write_text(
                json.dumps(dict(sorted(_MEASURED_SIZES.items())), indent=2) + "\n",
                encoding="utf-8",
            )
            return

        baseline = json.loads(SIZES.read_text(encoding="utf-8"))
        assert program.name in baseline, f"{program.name} has no size baseline"
        assert bytes_used <= baseline[program.name] * 1.10, (
            f"{program.name} grew from {baseline[program.name]} to {bytes_used} flash bytes"
        )
        return

    assert not ok, f"{program.name} unexpectedly built in {bytes_used} flash bytes"
    assert substring in output, (
        f"{program.name} diagnostic did not contain {substring!r}; got {diagnostic!r}"
    )
