## Cookiecutter template for Python3 project

This is a cookiecutter template for generic Python3 project with preconfigured linting tools.

The [poetry](https://python-poetry.org/) package manager should exist in PATH in order to use this template.

The following linting tools are also required and preconfigured to use with the generated project:
* ruff
* mypy
* pre-commit


Visual Studio Code is the preferred editor for the author and the [settings]({{cookiecutter.pkg_name}}/.vscode/settings.json) are provided for quick startup.

To use the template, please install cookiecutter on your computer by following [instructions here](https://cookiecutter.readthedocs.io/en/latest/installation.html)

```

# generate the template, enter project name when prompted
cookiecutter gh:vino9org/cookiecutter-python

# init venv and install dependencies
cd <project_path>
poetry shell
poetry install --no-root

# kick the tires...
pytest -v

# hack away!

```

## Design Decisions
This section logs design decisions made in this project.

| Decision          | Reason                                                                                                                                                                                                                                                                           |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [```poetry.toml```](poetry.toml) | The ```in-project = true``` setting instructs poetry to create a virtual env in project directory, so that ```python.defaultInterpreterPath``` in [```settings.json```](.vscode/settings.json) can be hard coded to ```.venv/bin/python```. This allows VSCode to access lint tools installed by package mananager, e.g. ruff, mypy, etc. The downside is the ```.venv``` directory needs to be deleted and recreated when switching between devcontainer and local python |
| [```pyproject.toml```](pyproject.toml) | all linting related configuration are consolidated into the same file to easier configuration |
| [```.pre-commit-config.yaml```](.pre-commit-config.yaml) | ```pre-commit@3.4.4``` and ```poetry@1.7.1``` apparently make conflicting changes to ```requirements.txt```, so bypass the files is required |
