# DO NOT EDIT: Autogenerated by /Users/micha/dev/external/docker-composer/src/docker_composer/_utils/generate_class.py
# for Docker Compose version v2.17.3

from typing import List, Optional

import attr

from docker_composer.base import DockerBaseRunner


@attr.s(auto_attribs=True)
class DockerComposePush(DockerBaseRunner):
    """
    Usage:  docker compose push [OPTIONS] [SERVICE...]
    Push service images
    """

    ignore_push_failures: Optional[bool] = None
    """Push what it can and ignores images with push failures"""
    include_deps: Optional[bool] = None
    """Also push images of services declared as dependencies"""
    quiet: Optional[bool] = None
    """Push without printing progress information"""
    _cmd: str = "push"
    _options: List[str] = [
        "ignore_push_failures",
        "include_deps",
        "quiet",
    ]
