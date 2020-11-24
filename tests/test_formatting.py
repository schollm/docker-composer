import pytest

from pathlib import Path
from subprocess import run


@pytest.fixture
def base_dir(request):
    # adjust base_dir if test file is moved.
    res = Path(request.fspath.dirname).parent
    files = res.iterdir()
    assert "pyproject.toml" in (p.name for p in files), "base_dir is no root"
    return res


@pytest.mark.parametrize("dir_name", ("src", "tests"))
def test_black(base_dir: Path, dir_name: str):
    proc = run(("black", "--check", base_dir / dir_name))
    assert proc.returncode == 0, ("black is not happy with", dir_name)


@pytest.mark.parametrize("dir_name", ("src", "tests"))
def test_isort(base_dir: str, dir_name: str):
    proc = run(("isort", "--diff", "--check", base_dir / dir_name))
    assert proc.returncode == 0
