## Cookiecutter template for Python3 project

This is a [cookiecutter](https://www.cookiecutter.io/) template for generic Python3 project with preconfigured with the following tools:

* [uv](https://docs.astral.sh/uv/)
* [ruff](https://docs.astral.sh/ruff/)
* [pre-commit](https://pre-commit.com/)
* [pyright](https://github.com/microsoft/pyright)
* VS Code support

## Project Options
The template supports the following application types with or without database drivers. If database driver is chosen, ```conftest.py``` will contain test databae preparation fixtures.

* simple
* [fastpi](https://quart.palletsprojects.com/en/latest/)
* [fastpi tortoise-orm aerich]


To use the template, please install cookiecutter on your computer by following [instructions here](https://cookiecutter.readthedocs.io/en/latest/installation.html)

```

# generate the template, enter project name when prompted
cookiecutter gh:vino9org/cookiecutter-python

# init venv and install dependencies
cd <project_path>
uv sync

# activate venv
source .venv/bin/activate

# kick the tires...
pytest -v

# hack away!

```
