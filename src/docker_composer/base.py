import subprocess
from functools import reduce
from operator import add
from typing import Iterable, Iterator, List, Optional

import attr
from loguru import logger


def _flatten(lists: Iterator[list]):
    """Flatten an iterable of lists"""
    return reduce(add, lists, [])


@attr.s
class DockerBaseRunner:
    _cmd: Optional[str] = None
    _options: List[str] = []
    _parent_cmd: List[str] = []

    def _get_arg(self, key, value) -> List[str]:
        if value is None:
            return []
        arg = f"--{key.replace('_', '-')}"
        if key in self._options:
            return [arg] if value else []
        if isinstance(value, dict) and value:
            return _flatten([arg, f"{k}={v}"] for k, v in value.items())
        elif isinstance(value, list) and value:
            return _flatten([arg, v] for v in value)
        else:
            return [arg, str(value)]

    def _get_args(self) -> List[str]:
        return _flatten(
            self._get_arg(k, v)
            for (k, v) in attr.asdict(self, recurse=False).items()
            if v is not None and not k.startswith("_")
        )

    def _call_cmd(self, arguments: Iterable[str] = ()) -> List[str]:
        return [
            arg
            for arg in (
                (self._parent_cmd or ["docker-compose"])
                + [self._cmd or ""]
                + self._get_args()
                + list(arguments)
            )
            if arg
        ]

    def call(
        self,
        *args: str,
        stdin=None,
        stdout=None,
        stderr=None,
        capture_output=False,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        """Call docker-compose with the generated command

        :param args: arguments to append.
        :param stdin: stdin (See `subprocess.run`)
        :param stdout: stdout (See `subprocess.run`)
        :param stderr: stderr (See `subprocess.run`)
        :param capture_output: If True, output is captured in the retuning CompletedProcess object
        :param kwargs: Additional arguments for `subprocess.run`.
        :return CompletedProcess instance
        """
        cmd = self._call_cmd(args)
        logger.info("# {}", " ".join(cmd))
        p = subprocess.run(
            cmd,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            capture_output=capture_output,
            **kwargs,
        )
        logger.debug("Returned from {}: {}", cmd[0], p.returncode)
        return p

    def Popen(
        self,
        *args: str,
        stdin=None,
        stdout=None,
        stderr=None,
        **kwargs,
    ) -> subprocess.Popen:
        """get an Instance of `subprocess.Popen`

        :param args: arguments to be appended to the docker-compose command
        :param stdin: stdin to use (see subprocess.Popen)
        :param stdout: stdout to use (see subprocess.Popen)
        :param stderr: stderr to use (see subprocess.Popen)
        :param kwargs: Additional arguments for `subprocess.Popen`
        :return: An subprocess.Popen instance
        """
        cmd = self._call_cmd(args)
        logger.info("# {}", " ".join(cmd))
        return subprocess.Popen(
            cmd,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            **kwargs,
        )
