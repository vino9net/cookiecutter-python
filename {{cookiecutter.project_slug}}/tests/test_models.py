from {{ cookiecutter.pkg_name }}.models import User

async def test_query_models():
    user = await User.filter(login_name="root").first()
    assert user and user.id == 1
