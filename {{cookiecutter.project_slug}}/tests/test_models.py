from sqlalchemy import select
from {{ cookiecutter.pkg_name }}.models import User

def test_query_models(session):
    user = session.execute(select(User).filter_by(login_name="root")).scalars().first()
    assert user.id == 1

def test_get_user(client):
    response = client.get("/users/root")
    assert response.status_code == 200
    assert response.json() == {"user_id": 1}
