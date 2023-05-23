# DO NOT EDIT: Autogenerated by /Users/micha/dev/external/docker-composer/src/docker_composer/_utils/generate_class.py
# for Docker Compose version v2.17.3

from typing import List, Optional

import attr

from docker_composer.base import DockerBaseRunner


@attr.s(auto_attribs=True)
class DockerComposeStart(DockerBaseRunner):
    """
    Usage:  docker compose start [SERVICE...]
    Start services
    """

    _cmd: str = "start"
    _options: List[str] = []
