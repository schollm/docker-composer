# DO NOT EDIT: Autogenerated by /Users/micha/dev/docker-composer/src/docker_composer/_utils/generate_class.py
# for Docker Compose version v2.29.7-desktop.1

from typing import List, Optional

import attr

from docker_composer.base import DockerBaseRunner


@attr.s(auto_attribs=True)
class DockerComposeWatch(DockerBaseRunner):
    """
    Usage:  docker compose watch [SERVICE...]
    Watch build context for service and rebuild/refresh containers when files are updated
    """

    dry_run: Optional[bool] = None
    """Execute command in dry run mode"""
    no_up: Optional[bool] = None
    """Do not build & start services before watching"""
    prune: Optional[bool] = None
    """Prune dangling images on rebuild"""
    quiet: Optional[bool] = None
    """hide build output"""
    _cmd: str = "watch"
    _options: List[str] = [
        "dry_run",
        "no_up",
        "prune",
        "quiet",
    ]
