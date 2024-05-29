import os
import os.path
import shlex
import subprocess


def run_pytest_in_generated_project(project_path):
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    try:
        os.chdir(project_path)

        subprocess.call(["poetry", "install", "--no-root"])
        assert subprocess.call(shlex.split("poetry run pytest -v -s")) == 0
    finally:
        os.chdir(current_path)


def run_linting_in_generated_project(project_path):
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    try:
        os.chdir(project_path)

        subprocess.call(["poetry", "install", "--no-root"])
        # run ruff but ignore formatting realted errors
        result = subprocess.run(
            shlex.split("poetry run ruff check . --ignore I001,E302,E303,W291,W391 --verbose"),
            capture_output=True,
            text=True,
        )
        if result.returncode:
            print("=== stdout ===")
            print(result.stdout)
            print("=== stderr ===")
            print(result.stderr)

        assert result.returncode == 0
    finally:
        os.chdir(current_path)


def run_precommit_in_generated_project(project_path):
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    try:
        os.chdir(project_path)

        subprocess.call(["poetry", "install", "--no-root"])
        assert subprocess.call(shlex.split("poetry run pre-commit install")) == 0

        # is adding a file necceeary?
        with open("a.py", "w") as f:
            f.write("# just some text\n")
            f.write("some_var = 0\n")
        assert subprocess.call(shlex.split("git add a.py")) == 0

        # skip black formatting for pre-commit
        # it is prone to fail and too much hassle to fix
        # env = os.environ.copy()
        # env["SKIP"] = "black"
        assert subprocess.call(shlex.split("poetry run pre-commit run")) == 0
    finally:
        os.chdir(current_path)


def check_project_structure(project_path, context):
    """check generate project structure based on options"""
    dockerfile_option = context["dockerfile_option"]
    extra_packages = context["extra_packages"]

    assert project_path.is_dir()
    assert (project_path / ".git/HEAD").is_file()

    if dockerfile_option == "None":
        assert not (project_path / "Dockerfile").is_file()
        assert not (project_path / ".github").is_dir()
    elif dockerfile_option == "Dockerfile only":
        assert (project_path / "Dockerfile").is_file()
        assert not (project_path / ".github").is_dir()
    elif dockerfile_option == "Dockerfile with Github workflow":
        assert (project_path / "Dockerfile").is_file()
        assert (project_path / ".github").is_dir()

    if "sqlalchemy" in extra_packages:
        assert (project_path / "alembic.ini").is_file()
        assert (project_path / "migrations").is_dir()


def test_default_project(cookies):
    result = cookies.bake(
        extra_context={
            "project_name": "My Default Project",
        }
    )

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.name == "my-default-project"

    check_project_structure(result.project_path, result.context)
    print(f"\ntest project generated {result.project_path}")

    run_pytest_in_generated_project(result.project_path)
    run_linting_in_generated_project(result.project_path)
    run_precommit_in_generated_project(result.project_path)


def test_project_with_sqlalchemy(cookies):
    result = cookies.bake(
        extra_context={
            "project_name": "Database Project",
            "extra_packages": "Install sqlalchemy and alembic with postgresql driver",
        }
    )

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.name == "database-project"

    check_project_structure(result.project_path, result.context)
    print(f"\ntest project generated {result.project_path}")

    run_pytest_in_generated_project(result.project_path)
    run_linting_in_generated_project(result.project_path)
    run_precommit_in_generated_project(result.project_path)
