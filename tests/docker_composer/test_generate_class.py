import pytest

from textwrap import dedent

from docker_composer._utils.generate_class import collect_help_lines

GEN1 = " General 1"
GEN2 = " general 2"
DETAIL1 = " Detail 1"
OPTION1 = "  --foo NUMBER  Foo number"
OPTION2 = "  --verbose     Verbose Plob"
OPTION3 = "  -f, --file    Input file"
OPTION3_2 = "       file 2"
SAMPLE_OUTPUT = "\n".join(
    (GEN1, GEN2, "Detail:", DETAIL1, "Options:", OPTION1, OPTION2, OPTION3, OPTION3_2)
)


def test_parse_help_lines():
    res = collect_help_lines(SAMPLE_OUTPUT)
    assert set(res.keys()) == {"general", "detail", "options"}
    assert res["general"] == [GEN1, GEN2]
    assert res["detail"] == [DETAIL1]
    assert res["options"] == [OPTION1, OPTION2, OPTION3, OPTION3_2]


def test_parse_help_lines_full_msg():
    res = collect_help_lines(
        dedent(
            """

        Usage:  docker build [OPTIONS] PATH | URL | -

        Build an image from a Dockerfile

        Options:
              --add-host list           Add a custom host-to-IP mapping (host:ip)
              --build-arg list          Set build-time variables
              --cache-from strings      Images to consider as cache sources
              --disable-content-trust   Skip image verification (default true)
        """
        )
    )
    assert set(res.keys()) == {"general", "options"}


class TestParseHelpLinesIgnoreRunHelpMsg:
    @pytest.fixture()
    def res(self):
        return collect_help_lines(
            dedent(
                """
            Usage:  docker compose [OPTIONS] COMMAND

            Docker Compose

            Options:
                  --ansi string                Control when to print ANSI control characters ("never"|"always"|"auto") (default "auto")

            Commands:
              build       Build or rebuild services
              config      Parse, resolve and render compose file in canonical format

            Run 'docker compose COMMAND --help' for more information on a command.
            """
            )
        )

    def test_keys(self, res):
        assert set(res.keys()) == {"general", "options", "commands"}

    def test_run_docker_help_not_in_commands(self, res):
        assert "Run 'docker" not in "\n".join(res["commands"])

    def test_run_docker_help_in_general(self, res):
        assert "Run 'docker" in "\n".join(res["general"])


def test_options():
    res = collect_help_lines(
        dedent(
            """
    Usage:  docker compose version [OPTIONS]

    Show the Docker Compose version information

    Options:
      -f, --format string   Format the output. Values: [pretty | json]. (Default: pretty)
          --short           Shows only Compose's version number.
      """
        )
    )
    assert set(res.keys()) == {"general", "options"}
    assert res["options"] == [
        "  -f, --format string   Format the output. Values: [pretty | json]. (Default: pretty)",
        "      --short           Shows only Compose's version number.",
    ]
