async def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
