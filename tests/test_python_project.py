import itertools
import json
import os
import os.path
import random
import shlex
import subprocess
from typing import Any

import pytest


def run_pytest_in_generated_project(project_path):
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    try:
        os.chdir(project_path)

        subprocess.call(shlex.split("uv sync"))
        assert subprocess.call(shlex.split("uv run pytest -v -s")) == 0
    finally:
        os.chdir(current_path)


def run_linting_in_generated_project(project_path):
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    try:
        os.chdir(project_path)

        subprocess.call(shlex.split("uv sync"))
        # run ruff but ignore formatting realted errors
        result = subprocess.run(
            shlex.split(
                "uv run ruff check . --ignore I001,E302,E303,F401,W291,W391 --verbose"
            ),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"==RUFF output===\n{result.stdout}"

        result = subprocess.run(
            shlex.split("uv run pyright"),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"==PYRIGHT output===\n{result.stdout}"

    finally:
        os.chdir(current_path)


def run_precommit_in_generated_project(project_path):
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    try:
        os.chdir(project_path)

        subprocess.call(shlex.split("uv sync"))
        assert subprocess.call(shlex.split("uv run pre-commit install")) == 0

        # is adding a file necceeary?
        with open("a.py", "w") as f:
            f.write("# just some text\n")
            f.write("some_var = 0\n")
        assert subprocess.call(shlex.split("git add a.py")) == 0

        assert subprocess.call(shlex.split("uv run pre-commit run")) == 0
    finally:
        os.chdir(current_path)


def check_project_structure(project_path, context):
    """check generate project structure based on options"""
    dockerfile_option = context["dockerfile_option"]
    extra_packages = context["extra_packages"]
    use_devcontainer = context["use_devcontainer"]

    assert project_path.is_dir()
    assert (project_path / ".git/HEAD").is_file()

    if use_devcontainer == "Yes":
        assert (project_path / ".devcontainer").is_dir()
        assert (project_path / "devcontainer.json").is_file()
    else:
        assert not (project_path / ".devcontainer").is_dir()

    if dockerfile_option == "None":
        assert not (project_path / "Dockerfile").is_file()
        assert not (project_path / ".github").is_dir()
    elif dockerfile_option == "Dockerfile only":
        assert (project_path / "Dockerfile").is_file()
        assert not (project_path / ".github").is_dir()
    elif "Github" in dockerfile_option:
        assert (project_path / "Dockerfile").is_file()
        assert (project_path / ".github").is_dir()

    if "alembic" in extra_packages:
        assert (project_path / "migrations").is_dir()


def is_valid_test_scenario(context) -> bool:
    dockerfile_option = context["dockerfile_option"]
    extra_packages = context["extra_packages"]
    use_devcontainer = context["use_devcontainer"]

    if extra_packages == "None":
        return True
    elif (
        extra_packages != "None"
        and use_devcontainer != "Yes"
        and dockerfile_option == "None"
    ):
        return True

    return False


def scenario_id(context) -> str:
    val = context["dockerfile_option"].lower()
    if val == "none":
        dockerfile_option = "nodocker"
    elif "github" in val:
        dockerfile_option = "github"
    else:
        dockerfile_option = "dockerfile"

    if context["extra_packages"] == "None":
        extra_packages = "none"
    elif context["extra_packages"] == "fastapi":
        extra_packages = "fastapi"
    else:
        extra_packages = "fastpi-sql"

    use_devcontainer = "devcon" if context["use_devcontainer"] == "Yes" else "nodevcon"

    return f"{use_devcontainer}_{dockerfile_option}_{extra_packages}"


def enumerate_test_scenarios() -> dict[str, dict[str, Any]]:
    """
    read parameters from cookiecutter.json and generate all possible combinations
    filter out the combination that should not be tested
    then return a dict with key as the test id and value is context for generation
    """
    ctx_file = os.path.dirname(os.path.abspath(__file__)) + "/../cookiecutter.json"

    keys = ["extra_packages", "use_devcontainer", "dockerfile_option"]

    with open(ctx_file) as f:
        ctx = json.load(f)
        param_lists = [ctx[key] for key in keys]
        all_entries = [dict(zip(keys, val)) for val in itertools.product(*param_lists)]
        return {
            scenario_id(entry): entry
            for entry in all_entries
            if is_valid_test_scenario(entry)
        }


def pytest_generate_tests(metafunc):
    """dynamically generate test cases based on content of cookiecutter.json"""
    if "generator_ctx" in metafunc.fixturenames:
        scenarios = enumerate_test_scenarios()
        metafunc.parametrize(
            "generator_ctx",
            scenarios.values(),
            ids=scenarios.keys(),
        )


def test_generate_and_build(cookies, generator_ctx):
    suffix = str(random.randint(1, 100))
    result = cookies.bake(
        extra_context={
            "project_name": f"My Test Service {suffix}",
        }
    )

    assert result.exit_code == 0 and result.exception is None
    assert result.project_path.is_dir()

    check_project_structure(result.project_path, result.context)
    print(f"\ntest project generated {result.project_path}")

    run_pytest_in_generated_project(result.project_path)
    run_linting_in_generated_project(result.project_path)
    run_precommit_in_generated_project(result.project_path)


@pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="for local test only",
)
def test_local_generate(cookies):
    """used to test locally"""
    result = cookies.bake(
        extra_context={
            "project_name": "My Local Project",
            "project_type": "lib",
            "use_devcontainer": "No",
            "dockerfile_option": "Build container with Github action",
            "extra_packages": "fastapi sqlmodel alembic",
            # "extra_packages": "fastapi",
        }
    )
    assert result.exit_code == 0 and result.exception is None
    assert result.project_path.is_dir()
    print(result.project_path)

    check_project_structure(result.project_path, result.context)
    run_pytest_in_generated_project(result.project_path)
    run_linting_in_generated_project(result.project_path)
    run_precommit_in_generated_project(result.project_path)
