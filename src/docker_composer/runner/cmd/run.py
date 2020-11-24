# DO NOT EDIT: Autogenerated by src/docker_composer/_utils/generate_class.py
# for docker-compose version 1.25.0, build unknown

from typing import List, Optional

import attr

from docker_composer.base import DockerBaseRunner


@attr.s(auto_attribs=True)
class DockerComposeRun(DockerBaseRunner):
    """
    Run a one-off command on a service.

    For example:

        $ docker-compose run web python manage.py shell

    By default, linked services will be started, unless they are already
    running. If you do not want to start linked services, use
    `docker-compose run --no-deps SERVICE COMMAND [ARGS...]`.

    Usage:
        run [options] [-v VOLUME...] [-p PORT...] [-e KEY=VAL...] [-l KEY=VALUE...]
            SERVICE [COMMAND] [ARGS...]

    """

    detach: Optional[bool] = None
    """Detached mode: Run container in the background, print
       new container name."""
    name: Optional[str] = None
    """Assign a name to the container"""
    entrypoint: Optional[str] = None
    """Override the entrypoint of the image."""
    e: Optional[dict] = None
    """Set an environment variable (can be used multiple times)"""
    label: Optional[dict] = None
    """Add or override a label (can be used multiple times)"""
    user: Optional[str] = None
    """Run as specified username or uid"""
    no_deps: Optional[bool] = None
    """Don't start linked services."""
    rm: Optional[bool] = None
    """Remove container after run. Ignored in detached mode."""
    publish: Optional[list] = None
    """Publish a container's port(s) to the host"""
    service_ports: Optional[bool] = None
    """Run command with the service's ports enabled and mapped
       to the host."""
    use_aliases: Optional[bool] = None
    """Use the service's network aliases in the network(s) the
       container connects to."""
    volume: Optional[list] = None
    """Bind mount a volume (default [])"""
    T: Optional[bool] = None
    """Disable pseudo-tty allocation. By default `docker-compose run`
       allocates a TTY."""
    workdir: Optional[str] = None
    """Working directory inside the container"""
    _cmd: str = "run"
    _options: List[str] = [
        "detach",
        "no_deps",
        "rm",
        "service_ports",
        "use_aliases",
        "T",
    ]
