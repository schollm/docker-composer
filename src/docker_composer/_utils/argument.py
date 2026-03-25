from typing import Iterable, Iterator

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)
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
    "PATH": str,
    "SERVICE": str,
    "SIGNAL": int,
    "TEXT": str,
    "TIMEOUT": int,
    "TLS_KEY_PATH": str,
    "USER": str,
    "bytes": int,
    "docker": bool,
    "filter": str,
    "int": int,
    "list": list,
    "scale": int,
    "str": str,
    "string": str,
    "stringArray": list[str],
    "type": str,
    "volumes": list[str],
    OPTION: bool,
}


@dataclass(frozen=True)
class Argument:
    arg: str
    type_desc: str
    type_: type
    description: str
    default: str = ""

    @property
    def type_str(self) -> str:
        if self.type_ is object:
            raise ValueError(self.type_)
        return self.type_.__name__

    @property
    def is_option(self) -> bool:
        return self.type_desc == OPTION

    @staticmethod
    def from_line(line: str) -> "Argument":
        if "  " in line:
            return _from_line_has_sep(line)
        raise ValueError(line)


def _collect_arguments(arguments: Iterable[str]) -> Iterator[str]:
    """Combine argument lines to obtain one line per argument"""
    res = ""
    for arg in arguments:
        if res and arg[:12].strip().startswith("-"):
            yield res.strip()
            res = ""
        res += f"\n   {arg.strip()}"
    if res:
        yield res.strip()


def parse_dc_argument(lines: list[str]) -> list[Argument]:
    """
    Parse arguments from lines of docker-compose specifications
    :param lines: Lines of the Options sections from `docker-compose --help`.
    :return: List of arguments
    """
    iter_lines = _collect_arguments(lines)
    return [Argument.from_line(line) for line in iter_lines if "--version" not in line]


def _get_type(type_name) -> type:
    res = _TYPE_CONVERSIONS.get(type_name, None)
    if res is None:
        if "=" in type_name:
            res = dict
        else:
            logger.warning("Unknown type %s, use str", type_name)
            res = str
    return res


def _parse_arg(arg: str) -> tuple[str, str, bool]:
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
        raise NotImplementedError(default)


def _from_line_has_sep(line) -> "Argument":
    """
    Get the argument from a docker-compose Options line, assuming there are at least two spaces before the description
    Sample " -f, --foo=[] FILES   Foo of files"

    :param line: a single line with the description separated from the definition by at least two blanks
    :return: Argument
    """
    min_arg_chars = 2  #  Simple argument with single dash (e.g. -x)
    min_full_chars = 4  # Named argument with double-dash (e.g. --xy)
    desc_idx = line[min_arg_chars:].index("  ")
    desc = line[desc_idx + min_full_chars :].strip()
    args = iter(line[: desc_idx + min_full_chars].split())
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
