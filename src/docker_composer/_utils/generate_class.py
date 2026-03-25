import subprocess
from collections import defaultdict
from functools import lru_cache, reduce
from operator import add
from pathlib import Path
from typing import Iterator, Mapping, Union

import black
import isort
from isort.exceptions import ISortError


from docker_composer._utils.argument import Argument, parse_dc_argument
import logging

logger = logging.getLogger(__name__)


@lru_cache()
def project_root():
    for path in Path(__file__).parents:
        if "pyproject.toml" in (p.name for p in path.iterdir()):
            logger.debug("Project Path root: %s", path)
            return path
    raise EnvironmentError("No pyproject.toml found in path hierarchy")


@lru_cache()
def _version(prog: str) -> str:
    return subprocess.run(
        (prog, "--version"), capture_output=True, text=True
    ).stdout.strip()


@lru_cache()
def get_help_message(subcommand: str = "") -> str:
    """Obtain the help message for subcommand from docker-compose."""
    args = [arg for arg in ["docker", "compose", subcommand, "--help"] if arg]
    try:
        process = subprocess.run(args, capture_output=True, text=True)
    except Exception:
        logger.error("FAILED to run %s.", args)
        raise
    if process.returncode:
        logger.error(
            "docker-compose %s --help exited with %s:", subcommand, process.returncode
        )
        raise RuntimeError(process.stderr)

    return process.stdout


def collect_help_lines(msg: str) -> Mapping[str, list[str]]:
    """Collect help messages into sections.
    :param msg: Output from docker-compose <cmd> --help
    :returns Mapping from section header to lines as lists. First (unnamed) section gets name "general"
    """
    parts: Mapping[str, list[str]] = defaultdict(list)
    part = "general"
    for line in msg.split("\n"):
        if not line:
            part = "general"
        elif " " not in line and line.endswith(":"):
            part = line[:-1].lower()
        else:
            parts[part].append(line)
    return parts


def parse_help(msg: str) -> tuple[Mapping[str, list[str]], list[Argument]]:
    """Helper function, get sections and arguments from docker-compose <cmd> --help text"""
    sections = collect_help_lines(msg)
    arguments = parse_dc_argument(sections["options"])
    return sections, arguments


def indent(lines: Union[str, list[str]], level: int = 4) -> str:
    """Indent lines by `level`.
    :param lines: List of strings or a single string. A single string is splt up into individual lines.
    :param level: number of spaces to indent
    :return indented code as a single string
    """
    if isinstance(lines, str):
        lines = lines.split("\n")
    lines = reduce(add, (line.split("\n") for line in lines), [])
    prefix = " " * level
    if lines:
        return prefix + f"\n{prefix}".join(lines)
    else:
        return ""


def get_docstring(sections: Mapping[str, list[str]]) -> list[str]:
    """Get (unindeted) docstring from docker-compose <cmd> --help. Use general and usage section.
    :param sections: Output from `collect_help_lines`
    """
    lines = sections["general"]
    usages = sections.get("usage", [])
    if usages:
        lines += ["Usage:"] + usages
    return lines


def type_arg(arg: Argument) -> tuple[str, str]:
    """Generate the argument for docker-compose as a string, together with the doc-string"""
    type_str = f"Optional[{arg.type_str}]"
    return f"{arg.arg}: {type_str} = None", f'"""{arg.description}"""'


def get_def_commands(
    sections: Mapping[str, list[str]], level: int = 0
) -> Iterator[tuple[str, list[str]]]:
    """Generate command functions as string"""
    commands = sections.get("commands", None)
    if not commands:
        return
    for line in commands:
        if not line.strip():
            continue
        cmd = line.split()[0]
        logger.debug("Generate run for %s", cmd)
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
        yield (
            f'''
def {cmd}(self, {args}) -> {class_name}:
    """
{indent(sections["general"], nl)}
{indent(sections.get("usage", ""), nl)}
{indent(arg_docs, nl)}
    """
    runner = {class_name}(**{{k: v for k, v in locals().items() if k != "self"}})
    runner._parent_cmd = self._call_cmd()
    return runner
''',
            new_imports,
        )


def generate_class(cmd: str, level: int = 0) -> str:
    class_name = f"DockerCompose{(cmd or 'Root').capitalize()}"
    docker_lines = get_help_message(cmd)
    nl = level + 4
    sections, arguments = parse_help(docker_lines)
    _add_custom_arguments(cmd, arguments)
    cmd_fns = ""
    add_imports: set[str] = set()
    if "commands" in sections:
        logger.info("Found commands in section %s", cmd)
        for cmd_fn, add_import in get_def_commands(sections):
            cmd_fns += cmd_fn
            add_imports = add_imports.union(add_import)
    args: list[str] = reduce(add, (list(type_arg(arg)) for arg in arguments), [])

    # List of argument that are options only
    options = ", ".join([f'"{arg.arg}"' for arg in arguments if arg.is_option])
    if options:
        options = options + ","
    new_line = "\n"  # Python 3.9 does not support backslashes in format-strings.
    res = indent(
        f'''
# DO NOT EDIT: Autogenerated by {"/".join(Path(__file__).parts[-3:])}
# for {_version("docker-compose")}

import attr
from typing import Optional
from docker_composer.base import DockerBaseRunner
{new_line.join(add_imports)}

@attr.s(auto_attribs=True)
class {class_name}(DockerBaseRunner):
    """
{indent(get_docstring(sections), level=nl)}
    """
{indent(args, level=nl)}
    _cmd: str = "{cmd or ""}"
    _options: list[str] = [{options}]
{indent(cmd_fns, level=nl)}
''',
        level=level,
    )
    try:
        res = isort.code(
            res, config=isort.Config(settings_path=project_root().as_posix())
        )
    except ISortError as exc:
        logger.exception(exc)
    try:
        return black.format_str(res, mode=black.Mode())
    except Exception as exc:
        logger.exception(exc)
        return res


def write_class(cmd: str = "") -> None:
    """
    Generate a class for `cmd` and write it to `file_name`

    :param cmd: docker-compose command to create or an empty string for root.
    :param file_name: Name of output file (empty/None for auto-generation)
    :return:
    """
    base_path = Path(__file__).parents[1] / "runner"
    file_name = (base_path / "cmd" / f"{cmd}.py") if cmd else (base_path / "root.py")
    class_str = generate_class(cmd)
    logger.info("Write %s -> %s", cmd, file_name)
    file_name.write_text(class_str, encoding="utf-8")


def _add_custom_arguments(cmd: str, arguments: list[Argument]) -> None:
    """Add the verbose option to arguments."""
    if cmd == "":
        verbose = Argument("verbose", "OPTION", bool, "Use verbose output")
        if verbose not in arguments:
            arguments.append(verbose)


def main() -> None:
    write_class()
    docker_lines = get_help_message()
    sections, _ = parse_help(docker_lines)
    for cmd_line in sections["commands"]:
        if not cmd_line:
            continue
        cmd = cmd_line.split()[0]
        write_class(cmd)


if __name__ == "__main__":
    main()
