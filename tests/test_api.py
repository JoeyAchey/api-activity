import pytest

from api_activity.app import create_app

@pytest.fixture
def client():
    with create_app().test_client() as client:
        yield client


def test_hello(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json == {"message": "Hello World!"}

def test_square(client):
    response = client.get("/square/5")
    assert response.status_code == 200
    assert response.json == {"Shape": "Square", "Area": 25}


def test_echo(client):
    response = client.get("/echo?arg1=hello&arg2=world")
    assert response.status_code == 200
    assert response.json == {"arg1": "hello", "arg2": "world"}

    