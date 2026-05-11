import pytest

from docker_composer._utils import sync_version


def test_docker_compose_version_short(monkeypatch) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_check_output(args: list[str], *, text: bool) -> str:
        calls.append((args, text))
        return "v5.1.3\n"

    monkeypatch.setattr(sync_version.subprocess, "check_output", fake_check_output)

    assert sync_version.docker_compose_version_short() == "v5.1.3"
    assert calls == [(["docker", "compose", "version", "--short"], True)]


def test_main_calls_uv_version(monkeypatch) -> None:
    calls: list[list[str]] = []

    monkeypatch.setattr(
        sync_version,
        "docker_compose_version_short",
        lambda: "v5.1.3",
    )

    def fake_check_call(args: list[str]) -> int:
        calls.append(args)
        return 0

    monkeypatch.setattr(sync_version.subprocess, "check_call", fake_check_call)

    sync_version.main()

    assert calls == [["uv", "version", "v5.1.3"]]


def test_main_raises_for_empty_version(monkeypatch) -> None:
    monkeypatch.setattr(sync_version, "docker_compose_version_short", lambda: "")

    with pytest.raises(RuntimeError, match="empty version"):
        sync_version.main()
