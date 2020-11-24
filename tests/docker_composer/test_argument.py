import pytest

from docker_composer._utils.argument import (
    Argument,
    _collect_arguments,
    _from_line_has_sep,
    _get_type,
)


@pytest.mark.parametrize(
    "input, expect",
    [
        ("--foo FILE Foo Bar", ("foo", "FILE", str, "Foo Bar")),
        ("-f, --foo FILE Foo Bar", ("foo", "FILE", str, "Foo Bar")),
        ("-f, --foo=[] FILE Foo Bar", ("foo", "FILE", list, "Foo Bar", "[]")),
        ("-v, --verbose Verbose Flag", ("verbose", "OPTION", bool, "Verbose Flag")),
        ("--verbose Verbose Flag", ("verbose", "OPTION", bool, "Verbose Flag")),
        ("-v Verbose Flag", ("v", "OPTION", bool, "Verbose Flag")),
        ## Tests for _from_line_has_sep
        ("--foo FILE             Foo Bar", ("foo", "FILE", str, "Foo Bar")),
        ("-f, --foo FILE         Foo Bar", ("foo", "FILE", str, "Foo Bar")),
        ("-f, --foo=[] FILE      Foo Bar", ("foo", "FILE", list, "Foo Bar", "[]")),
        (
            "-v, --verbose          Verbose Flag",
            ("verbose", "OPTION", bool, "Verbose Flag"),
        ),
        (
            "--verbose              Verbose Flag",
            ("verbose", "OPTION", bool, "Verbose Flag"),
        ),
        ("-v                     Verbose Flag", ("v", "OPTION", bool, "Verbose Flag")),
    ],
)
def test_Argument_from_line(input, expect):
    res = Argument.from_line(input)
    assert res == Argument(*expect)


@pytest.mark.parametrize(
    "input, expect",
    [
        (Argument("", "INT", int, ""), False),
        (Argument("", "OPTION", bool, ""), True),
    ],
)
def test_Argument_is_option(input, expect):
    assert input.is_option == expect


@pytest.mark.parametrize(
    "type_, expect",
    [
        ("INT", int),
        ("TEXT", str),
        ("FILE", str),
        ("OPTION", bool),
        ("KEY=VAL", dict),
        ("FOO", str),
    ],
)
def test__get_type(type_, expect):
    assert _get_type(type_) == expect


@pytest.mark.parametrize(
    "line,expect",
    [
        ("-foo  Bar", Argument("foo", "OPTION", bool, "Bar")),
        ("-f, --foo  Bar", Argument("foo", "OPTION", bool, "Bar")),
        ("    -f, --foo  Bar", Argument("foo", "OPTION", bool, "Bar")),
        ("    -f, --foo BAR  Bar", Argument("foo", "BAR", str, "Bar")),
        (
            "    -f, --foo=[] BAR  Bar",
            Argument("foo", "BAR", list, "Bar", default="[]"),
        ),
    ],
)
def test__from_line_has_sep(line, expect):
    assert _from_line_has_sep(line) == expect


OPTION1 = "  --foo NUMBER  Foo number"
OPTION2 = "  --verbose     Verbose Plob"
OPTION3 = "  -f, --file    Input file"
OPTION3_2 = "       file 2"


def test_parse_options_collect():
    res = _collect_arguments([OPTION1, OPTION2, OPTION3, OPTION3_2])
    assert next(res) == OPTION1.strip()
    assert next(res) == OPTION2.strip()
    assert next(res) == f"{OPTION3.strip()}\n   {OPTION3_2.strip()}"
    assert list(res) == []
