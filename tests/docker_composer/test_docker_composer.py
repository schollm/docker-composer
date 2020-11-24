import pytest

from docker_composer import DockerCompose


@pytest.mark.parametrize(
    "root_args, expected",
    [
        (dict(), []),
        (dict(verbose=True), ["--verbose"]),
        (dict(verbose=False), []),
        (dict(file="file.yml"), ["--file", "file.yml"]),
        (
            dict(verbose=True, file="docker-compose.yml"),
            [
                "--file",
                "docker-compose.yml",
                "--verbose",
            ],
        ),
    ],
)
def test_root__call_cmd(root_args, expected):
    res = DockerCompose(**root_args)._call_cmd(["bar"])
    assert res == ["docker-compose"] + expected + ["bar"]


@pytest.mark.parametrize(
    "cmd_args, expected_cmd",
    [
        (dict(), []),
        (dict(compress=False), []),
        (dict(compress=True), ["--compress"]),
        (dict(build_arg="Foo"), ["--build-arg", "Foo"]),
        (dict(build_arg="Foo", force_rm=True), ["--build-arg", "Foo", "--force-rm"]),
    ],
)
def test_build__call_cmd(cmd_args, expected_cmd):
    res = DockerCompose(verbose=True).build(**cmd_args)._call_cmd(["bar"])
    assert res == ["docker-compose", "--verbose", "build"] + expected_cmd + ["bar"]
