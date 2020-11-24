from typing import Any, Iterable, Iterator, List, Optional, Tuple, Type

import attr
from loguru import logger

OPTION = "OPTION"

_TYPE_CONVERSIONS = {
    "CA_PATH": str,
    "CLIENT_CERT_PATH": str,
    "CMD": str,
    "DIR": str,
    "FILE": str,
    "HOST": str,
    "INT": int,
    "LEVEL": int,
    "MEM": int,
    "NAME": str,
    OPTION: bool,
    "PATH": str,
    "SERVICE": str,
    "SIGNAL": int,
    "TEXT": str,
    "TIMEOUT": int,
    "TLS_KEY_PATH": str,
    "USER": str,
    "type": str,
    "string": str,
    "int": int,
    "list": list,
    "str": str,
}


@attr.s(auto_attribs=True, frozen=True)
class Argument:
    arg: str
    type_desc: str
    type: Type
    description: str
    default: str = ""

    @property
    def type_str(self) -> str:
        return "Any" if self.type == object else self.type.__name__

    @property
    def is_option(self) -> bool:
        return self.type_desc == OPTION

    @staticmethod
    def from_line(line: str) -> "Argument":
        if "  " in line:
            return _from_line_has_sep(line)

        words = iter(line.split())
        has_more = True
        while has_more:
            arg, default_str, has_more = _parse_arg(next(words))
        type_desc = next(words)
        type_from_default = _get_type_name_from_default(default_str)
        desc = " ".join(words)
        if type_desc[1:].islower() and "=" not in type_desc:
            desc = f"{type_desc} {desc}"
            type_desc = type_from_default

        type_ = _get_type(type_from_default if default_str else type_desc)
        return Argument(arg, type_desc, type_, desc, default_str)


def _collect_arguments(arguments: Iterable[str]) -> Iterator[str]:
    """Combine argument lines to obtain one line per argument"""
    res = ""
    for arg in arguments:
        if res and arg[:6].strip().startswith("-"):
            yield res.strip()
            res = ""
        res += f"\n   {arg.strip()}"
    if res:
        yield res.strip()


def parse_dc_argument(lines: List[str]) -> List[Argument]:
    """
    Parse arguments from lines of docker-compose specifications
    :param lines: Lines of the Options sections from `docker-compose --help`.
    :return: List of arguments
    """
    iter_lines = _collect_arguments(lines)
    return [Argument.from_line(line) for line in iter_lines if "--version" not in line]


def _get_type(type_name) -> Type:
    if (res := _TYPE_CONVERSIONS.get(type_name, None)) is None:
        if "=" in type_name:
            res = dict
        else:
            logger.warning("Unknown type {}, use str", type_name)
            res = str
    return res


def _parse_arg(arg: str) -> Tuple[str, str, bool]:
    while arg.startswith("-"):
        arg = arg[1:]
    # if argument ends with a comma, it is followed by an alias. (usually -f, --foo)
    has_more = arg.endswith(",")
    if has_more:
        arg = arg[:-1]
        default = ""
    else:
        if "=" in arg:
            default = arg[arg.index("=") + 1 :]
            arg = arg[: arg.index("=")]
        else:
            default = ""
    return arg.replace("-", "_").strip(), default, has_more


def _get_type_name_from_default(default: str) -> str:
    """Extract type name from default value"""
    if not default:
        return OPTION
    elif default == "index":
        return "int"
    elif default == "proto":
        return "str"
    else:
        try:
            return eval(default).__class__.__name__
        except NameError:
            logger.warning("Could not get type for value '{}'", default)
            return "str"


def _from_line_has_sep(line) -> "Argument":
    """
    Get the argument from a docker-compose Options line, assuming there are at least two spaces before the description
    Sample " -f, --foo=[] FILES   Foo of files"

    :param line: a single line with the description separated from the definition by at least two blanks
    :return: Argument
    """
    desc_idx = line[4:].index("  ")
    desc = line[desc_idx + 2 + 4 :].strip()
    args = iter(line[: desc_idx + 4].split())
    arg, default, has_more = "", "", True
    while has_more:
        arg, default, has_more = _parse_arg(next(args))
    type_from_default = _get_type_name_from_default(default)
    try:
        type_desc = next(args)
    except StopIteration:
        type_desc = type_from_default

    type_ = _get_type(type_from_default if default else type_desc)
    return Argument(arg, type_desc, type_, desc, default=default)
