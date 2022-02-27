import os
import os.path
import shlex
import subprocess


def assert_pipeline_yaml(project_path):
    # check if pipeline.yaml handled correctly by post_gen_project hook
    with open(f"{project_path}/.github/workflows/pipeline.yaml", "r") as f:
        content = "".join(f.readlines())
        assert "DUMMYSTACKNAME" not in content
    assert not os.path.isfile(f"{project_path}/.github/workflows/pipeline.yaml.pre")


def run_pytest_in_generated_project(project_path):
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    os.chdir(project_path)
    subprocess.call(["poetry", "install"])
    retcode = subprocess.call(shlex.split("poetry run pytest -v tests/unit"))

    os.chdir(current_path)

    return retcode


def test_default_project(cookies):
    result = cookies.bake(extra_context={"project_name": "My Default Stack"})

    assert result.exit_code == 0
    assert result.exception is None

    assert result.project_path.name == "my-default-stack"
    assert result.project_path.is_dir()

    print(f"test project generated {result.project_path}")

    assert_pipeline_yaml(result.project_path)

    # project default does not generate lambda funciton
    assert not os.path.exists(f"{result.project_path}/runtime")
    assert not os.path.exists(f"{result.project_path}/tests/runtime")

    assert run_pytest_in_generated_project(result.project_path) == 0


def test_lambda_project(cookies):
    result = cookies.bake(
        extra_context={"project_name": "My Lambda Stack", "use_lambda": "y"}
    )

    assert result.exit_code == 0
    assert result.exception is None

    assert result.project_path.name == "my-lambda-stack"
    assert result.project_path.is_dir()

    print(f"test project generated {result.project_path}")

    # should be replaced by post_gen_project hook
    assert_pipeline_yaml(result.project_path)

    # these diretories should exist when lambda function is enabeld
    assert os.path.isfile(f"{result.project_path}/runtime/app.py")
    assert os.path.isdir(f"{result.project_path}/tests/unit/runtime")

    assert run_pytest_in_generated_project(result.project_path) == 0
