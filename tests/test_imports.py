import pytest

import importlib
import os
import types
from pathlib import Path
from typing import Iterable

import docker_composer


def get_module_names(package: types.ModuleType) -> Iterable[str]:
    for lib_path in getattr(package, "__path__", []):
        package_name = Path(lib_path).name
        for path_name, _, file_names in os.walk(lib_path):
            super_package_name = path_name[len(lib_path) + 1 :].replace("/", ".")
            for fname in (Path(fn) for fn in file_names if fn.endswith(".py")):
                if fname == Path("__init__.py"):
                    fname = Path("")
                yield ".".join(
                    filter(None, (package_name, super_package_name, fname.stem))
                )


@pytest.mark.parametrize("import_name", get_module_names(docker_composer))
def test_import(import_name: str):
    importlib.import_module(import_name)


def test_import_DockerComposer():
    assert "DockerCompose" in dir(docker_composer)
