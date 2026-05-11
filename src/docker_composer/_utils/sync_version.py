from __future__ import annotations

import subprocess


def docker_compose_version_short() -> str:
    return subprocess.check_output(
        ["docker", "compose", "version", "--short"],
        text=True,
    ).strip()


def main() -> None:
    version = docker_compose_version_short()
    if not version:
        raise RuntimeError("docker compose version --short returned an empty version")
    subprocess.check_call(["uv", "version", version])


if __name__ == "__main__":
    main()  # pragma: no cover
