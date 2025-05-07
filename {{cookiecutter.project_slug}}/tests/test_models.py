from sqlalchemy import select

from {{ cookiecutter.pkg_name }}.models import User


def test_query_models(session):
    user = session.execute(select(User).filter_by(login_name="root")).scalars().first()
    assert user and user.id
