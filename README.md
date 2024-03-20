## Cookiecutter template for Python3 project

This is a cookiecutter template for generic Python3 project with preconfigured linting tools.

The [poetry](https://python-poetry.org/) package manager should exist in PATH in order to use this template.

The following linting tools are also required and preconfigured to use with the generated project:
* flake8
* isort
* black
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
poetry install --no-root --with linting

# kick the tires...
pytest -v

# hack away!

```
