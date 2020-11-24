import modulefinder
import os
import subprocess
from pathlib import Path

import loguru
from loguru import logger

import docker_composer
from docker_composer.runner.root import DockerComposeRoot

# b = DockerComposeRoot().ps(quiet=False, all=True).call(capture_output=True)
# print(b.stdout.decode("UTF-8"))
#


def get_packages(package):
    for lib_path in getattr(package, "__path__", None):
        package_name = Path(lib_path).name
        for path_name, _, file_names in os.walk(lib_path):
            super_package_name = path_name[len(lib_path) + 1 :].replace("/", ".")
            for fname in (Path(fn) for fn in file_names if fn.endswith(".py")):
                if fname == Path("__init__.py"):
                    module = ".".join(filter(None, (package_name, super_package_name)))
                else:
                    module = ".".join(
                        filter(
                            None, (package_name, super_package_name, Path(fname).stem)
                        )
                    )
                yield module


if __name__ == "__main__":
    for module in get_packages(docker_composer):
        logger.debug("Import {}", module)
        __import__(module)
