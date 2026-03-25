try:
    from docker_composer.runner.root import DockerComposeRoot as DockerCompose
except ImportError:
    pass

__all__ = ["DockerCompose"]
