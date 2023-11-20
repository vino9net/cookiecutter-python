from {{ cookiecutter.pkg_name }} import log
{% if "pandas" in cookiecutter.extra_packages -%}
import pandas as pd

_ = pd.DataFrame()
{% endif %}

def test_logger():
    log.info("running test")
