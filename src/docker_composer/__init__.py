try:
    from docker_composer.runner.root import DockerComposeRoot as DockerCompose
except (ImportError, ValueError):
    pass

__all__ = ["DockerCompose"]
