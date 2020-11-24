# Docker Composer
A library to interact with `docker-compose` from a python Program.
All commands and parameters are exposed as python classes and attributes
to allow for full auto-completion of its parameters with IDEs
that support it.


## Install
```shell script
pip install docker-composer
```

## Usage
The main class is `docker_composer.DockerCompose`. Its parameters are
all options from `docker-compose`.
 
Each `docker-compose` command has a corresponding function, e.g. 
`DockerCompose.run` or `DockerCompose.scale`. Their arguments again mirror 
the options of the corresponding command.

The resulting object has a `call` function. 
It takes arbitrary strings as input, as well as all keyword arguments from 
`subprocess.run`, and returns a `subprocess.CompletedProcess`

```python
from docker_composer import DockerCompose
base = DockerCompose(file="docker-compose.yml", verbose=True)

base.run(detach=True, workdir="/tmp").call("app")

base.run(workdir="/tmp").call("app", "/bin/bash", "-l")
# /tmp $ ls /.dockerenv
# /.dockerenv
# /tmp $ exit

process = base.ps(all=True).call(capture_output=True)
print(process.stdout.encode("UTF-8"))
#          Name                      Command           State    Ports
# -------------------------------------------------------------------
# myapp_app_70fd8b786b76   myapp --start-server        Exit 0        
# myapp_app_6ac3db4e1b55   myapp --client              Exit 0   
```

## Develop

### Coding Standards

| **Type**       | Package  | Comment                         |
| -------------- | -------- | ------------------------------- |
| **Linter**     | `black`  | Also for auto-formatted modules |
| **Logging**    | `loguru` |                                 |
| **Packaging**  | `poetry` |                                 |
| **Tests**      | `pytest` |                                 |
| **Typing**     | `mypy`   | Type all methods                |
