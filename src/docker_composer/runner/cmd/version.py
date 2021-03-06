# DO NOT EDIT: Autogenerated by src/docker_composer/_utils/generate_class.py
# for docker-compose version 1.25.0, build unknown

from typing import List, Optional

import attr

from docker_composer.base import DockerBaseRunner


@attr.s(auto_attribs=True)
class DockerComposeVersion(DockerBaseRunner):
    """
    Show version information

    Usage: version [--short]

    """

    short: Optional[bool] = None
    """Shows only Compose's version number."""
    _cmd: str = "version"
    _options: List[str] = [
        "short",
    ]
