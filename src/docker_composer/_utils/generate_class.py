import os
import subprocess
from collections import defaultdict
from functools import lru_cache, reduce
from operator import add
from pathlib import Path
from typing import Iterable, Iterator, List, Mapping, Optional, Set, Tuple, Union

import black
import isort
from isort.exceptions import ISortError
from loguru import logger

from docker_composer._utils.argument import Argument, parse_dc_argument


@lru_cache()
def project_root():
    for path in Path(__file__).parents:
        if "pyproject.toml" in (p.name for p in path.iterdir()):
            logger.debug("Project Path root: {}", path)
            return path
    raise EnvironmentError("No pyproject.toml found in path hierarchy")


@lru_cache(None)
def _version(prog: str) -> str:
    return (
        subprocess.run((prog, "--version"), capture_output=True)
        .stdout.strip()
        .decode("UTF-8")
    )


@lru_cache()
def get_help_message(subcommand: str = "") -> str:
    """Obtain the help message for subcommand from docker-compose."""
    args = [arg for arg in ["docker-compose", subcommand, "--help"] if arg]
    process = subprocess.run(args, capture_output=True, text=True)
    if process.returncode:
        logger.error(process.returncode)
        logger.error(process.stderr)
    return process.stdout


def collect_help_lines(msg: str) -> Mapping[str, List[str]]:
    """Collect help messages into sections.
    :param msg: Output from docker-compose <cmd> --help
    :returns Mapping from section header to lines as lists. First (unnamed) section gets name "general"
    """
    parts: Mapping[str, List[str]] = defaultdict(list)
    part = "general"
    for line in msg.split("\n"):
        if line and line[0] != " " and line.endswith(":") and " " not in line:
            part = line[:-1].lower()
        else:
            parts[part].append(line)
    return parts


def parse_help(msg: str) -> Tuple[Mapping[str, List[str]], List[Argument]]:
    """Helper function, get sections and arguments from docker-compose <cmd> --help text"""
    sections = collect_help_lines(msg)
    arguments = parse_dc_argument(sections["options"])
    return sections, arguments


def _flatten(lists: Iterable[list]):
    """Flatten an iterable of lists"""
    return reduce(add, lists, [])


def indent(lines: Union[str, List[str]], level: int = 4) -> str:
    """Indent lines by `level`.
    :param lines: List of strings or a single string. A single string is splt up into individual lines.
    :param level: number of spaces to indent
    :return indented code as a single string
    """
    if isinstance(lines, str):
        lines = lines.split("\n")
    lines = _flatten([l.split("\n") for l in lines])
    prefix = " " * level
    if lines:
        return prefix + f"\n{prefix}".join(lines)
    else:
        return ""


def get_docstring(sections: Mapping[str, List[str]]) -> List[str]:
    """Get (unindeted) docstring from docker-compose <cmd> --help. Use general and usage section.
    :param sections: Output from `collect_help_lines`
    """
    lines = sections["general"]
    if usages := sections.get("usage", []):
        lines += ["Usage:"] + usages
    return lines


def type_arg(arg: Argument) -> Tuple[str, str]:
    """Generate the argument for docker-compose as a string, together with the doc-string"""
    type_str = f"Optional[{arg.type_str}]"
    return f"{arg.arg}: {type_str} = None", f'"""{arg.description}"""'


def get_def_commands(
    sections: Mapping[str, List[str]], level: int = 0
) -> Iterator[Tuple[str, List[str]]]:
    """Generate command functions as string"""
    if not (commands := sections.get("commands", None)):
        return
    for line in commands:
        if not line.strip():
            continue
        cmd = line.split()[0]
        logger.debug("Generate run for {}", cmd)
        docker_lines = get_help_message(cmd)
        nl = level + 4
        sections, arguments = parse_help(docker_lines)
        args = ",".join(type_arg(arg)[0] for arg in arguments)
        arg_docs = "\n".join(
            f":param {arg.arg}: {arg.description}" for arg in arguments
        )

        class_name = f"docker_composer.runner.cmd.{cmd}.DockerCompose{cmd.capitalize()}"
        new_imports = [
            f"import docker_composer.runner.cmd.{cmd}",
        ]
        yield f'''
def {cmd}(self, {args}) -> {class_name}:
    """
{indent(sections["general"], nl)}
{indent(sections.get("usage", ""), nl)}
{indent(arg_docs, nl)}
    """
    runner = {class_name}(**{{k: v for k, v in locals().items() if k != "self"}})
    runner._parent_cmd = self._call_cmd()
    return runner
''', new_imports


def generate_class(class_name: str, cmd: str, level=0) -> str:
    docker_lines = get_help_message(cmd)
    nl = level + 4
    sections, arguments = parse_help(docker_lines)
    cmd_fns = ""
    add_imports: Set[str] = set()
    if "commands" in sections:
        logger.info("Found commands in section {}", cmd)
        for cmd_fn, add_import in get_def_commands(sections):
            cmd_fns += cmd_fn
            add_imports = add_imports.union(add_import)
    args: List[str] = _flatten(list(type_arg(arg)) for arg in arguments)

    # List of argument that are options only
    options = ", ".join([f'"{arg.arg}"' for arg in arguments if arg.is_option])
    if options:
        options = options + ","
    new_line = "\n"
    res = indent(
        f'''
# DO NOT EDIT: Autogenerated by {__file__}
# for {_version("docker-compose")}

import attr
from typing import Optional, List
from docker_composer.base import DockerBaseRunner
{new_line.join(add_imports)}

@attr.s(auto_attribs=True)
class {class_name}(DockerBaseRunner):
    """
{indent(get_docstring(sections), level=nl)}
    """
{indent(args, level=nl)}
    _cmd: str = "{cmd or ""}"
    _options: List[str] = [{options}]
{indent(cmd_fns, level=nl)}
''',
        level=level,
    )
    try:
        res = isort.code(res, config=isort.Config(settings_path=project_root()))
    except ISortError as exc:
        logger.exception(exc)
    try:
        return black.format_str(res, mode=black.Mode())
    except Exception as exc:
        logger.exception(exc)
        return res


def write_class(cmd: str, file_name: Optional[str] = None) -> None:
    """
    Generate a class for `cmd` and write it to `file_name`

    :param cmd: docker-compose command to create or an empty string for root.
    :param file_name: Name of output file (empty/None for auto-generation)
    :return:
    """
    if not file_name:
        file_name = os.path.join(
            os.path.dirname(__file__),
            "..",
            "runner",
            "cmd" if cmd else "",
            f"{cmd or 'root'}.py",
        )
    class_str = generate_class(f"DockerCompose{(cmd or 'root').capitalize()}", cmd)
    logger.info("Write {:<8s} -> {}", cmd or "root", file_name)
    with open(file_name, "w") as f:
        f.write(class_str)


def main() -> None:
    write_class("")
    docker_lines = get_help_message("")
    sections, _ = parse_help(docker_lines)
    for cmd_line in sections["commands"]:
        if not cmd_line:
            continue
        cmd = cmd_line.split()[0]
        write_class(cmd)


if __name__ == "__main__":
    main()
