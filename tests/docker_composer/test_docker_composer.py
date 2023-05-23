import pytest

from docker_composer import DockerCompose


@pytest.mark.parametrize(
    "root_args, expected",
    [
        (dict(), []),
        (dict(compatibility=True), ["--compatibility"]),
        (dict(compatibility=False), []),
        (dict(file="file.yml"), ["--file", "file.yml"]),
        (
            dict(compatibility=True, file="docker-compose.yml"),
            [
                "--compatibility",
                "--file",
                "docker-compose.yml",
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
        (dict(pull=False), []),
        (dict(pull=True), ["--pull"]),
        (dict(build_arg="Foo"), ["--build-arg", "Foo"]),
        (dict(build_arg="Foo", pull=True), ["--build-arg", "Foo", "--pull"]),
    ],
)
def test_build__call_cmd(cmd_args, expected_cmd):
    res = DockerCompose(compatibility=True).build(**cmd_args)._call_cmd(["bar"])
    assert res == ["docker-compose", "--compatibility", "build"] + expected_cmd + [
        "bar"
    ]
