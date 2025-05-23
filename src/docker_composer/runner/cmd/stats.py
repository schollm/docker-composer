# DO NOT EDIT: Autogenerated by /Users/micha/dev/docker-composer/src/docker_composer/_utils/generate_class.py
# for Docker Compose version v2.29.7-desktop.1

from typing import List, Optional

import attr

from docker_composer.base import DockerBaseRunner


@attr.s(auto_attribs=True)
class DockerComposeStats(DockerBaseRunner):
    """
    Usage:  docker compose stats [OPTIONS] [SERVICE]
    Display a live stream of container(s) resource usage statistics
    """

    all: Optional[bool] = None
    """Show all containers (default shows just running)"""
    dry_run: Optional[bool] = None
    """Execute command in dry run mode"""
    format: Optional[str] = None
    """Format output using a custom template:
       'table':            Print output in table format with column headers (default)
       'table TEMPLATE':   Print output in table format using the given Go template
       'json':             Print in JSON format
       'TEMPLATE':         Print output using the given Go template.
       Refer to https://docs.docker.com/go/formatting/ for more information about formatting output with templates"""
    no_stream: Optional[bool] = None
    """Disable streaming stats and only pull the first result"""
    no_trunc: Optional[bool] = None
    """Do not truncate output"""
    _cmd: str = "stats"
    _options: List[str] = [
        "all",
        "dry_run",
        "no_stream",
        "no_trunc",
    ]
