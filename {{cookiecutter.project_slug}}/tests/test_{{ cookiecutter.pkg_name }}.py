from {{ cookiecutter.pkg_name }} import log


def test_logger():
    log.info("running test")
