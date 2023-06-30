import os

from {{ cookiecutter.pkg_name }} import A


def test_stack_created():
    assert os.getcwd()
    assert A()
