from loguru import logger
{% if "pandas" in cookiecutter.extra_packages -%}
import pandas as pd

_ = pd.DataFrame()
{% endif %}

def test_logger():
    logger.info("running test_logger")
