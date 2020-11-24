from docker_composer._utils.generate_class import collect_help_lines

SAMPLE_MESSAGE = """Docker

Usage:
  docker-compose [-f <arg>...] [options] [COMMAND] [ARGS...]
  docker-compose -h|--help

Options:
  -f, --file FILE             Specify an alternate compose file
                              (default: docker-compose.yml)
  -p, --project-name NAME     Specify an alternate project name
                              (default: directory name)
  --verbose                   Show more output
  --log-level LEVEL           Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  --no-ansi                   Do not print ANSI control characters
  -v, --version               Print version and exit

Commands:
  build              Build or rebuild services
  bundle             Generate a Docker bundle from the Compose file
  config             Validate and view the Compose file
"""

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
