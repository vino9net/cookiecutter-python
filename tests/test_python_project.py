import os
import os.path
import shlex
import subprocess


def run_pytest_in_generated_project(project_path):
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    os.chdir(project_path)
    subprocess.call(["poetry", "install"])
    retcode = subprocess.call(shlex.split("poetry run pytest -v"))

    os.chdir(current_path)

    return retcode


def test_default_project(cookies):
    result = cookies.bake(extra_context={"project_name": "My Default Project"})

    assert result.exit_code == 0
    assert result.exception is None

    assert result.project_path.name == "my-default-project"
    assert result.project_path.is_dir()
    assert (result.project_path / ".git/HEAD").is_file()

    print(f"test project generated {result.project_path}")

    assert run_pytest_in_generated_project(result.project_path) == 0
