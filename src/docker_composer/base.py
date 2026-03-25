import subprocess
from functools import reduce
from operator import add
from typing import Iterable, Optional
import dataclasses as _dc

import logging

logger = logging.getLogger(__name__)


def _flatten(lists: Iterable[list]):
    """Flatten an iterable of lists"""
    return reduce(add, lists, [])


@_dc.dataclass()
class DockerBaseRunner:
    _cmd: Optional[str] = _dc.field(default=None, init=False, repr=False)
    _options: list[str] = _dc.field(default_factory=list, init=False, repr=False)
    _parent_cmd: list[str] = _dc.field(default_factory=list, init=False, repr=False)

    def _get_arg(self, key, value) -> list[str]:
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

    def _get_args(self) -> list[str]:
        fields = _dc.asdict(self)
        return _flatten(
            self._get_arg(k, v)
            for (k, v) in fields.items()
            if v is not None and not k.startswith("_")
        )

    def _call_cmd(self, arguments: Iterable[str] = ()) -> list[str]:
        return [
            arg
            for arg in (
                (self._parent_cmd or ["docker", "compose"])
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
        logger.info("# %s", " ".join(cmd))
        p = subprocess.run(
            cmd,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            **kwargs,
        )
        logger.debug("Returned from %s: %s", cmd[0], p.returncode)
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
        logger.info("# %s", " ".join(cmd))
        return subprocess.Popen(
            cmd,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            **kwargs,
        )
