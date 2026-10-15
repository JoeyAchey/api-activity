import pytest

from api_activity.app import create_app

@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a separate temporary database for each test.
    monkeypatch.chdir(tmp_path)

    app = create_app()
    app.testing = True

    with app.test_client() as client:
        yield client


def register_user(client):
    response = client.put(
        "/register",
        json={"username": "testuser", "password": "testpass123"},
        base_url="https://localhost",
    )
    assert response.status_code == 201


def test_hello(client):
    response = client.get("/", base_url="https://localhost")
    assert response.status_code == 200
    assert response.json == {"message": "Hello World!"}


def test_square(client):
    response = client.get("/square/5", base_url="https://localhost")
    assert response.status_code == 200
    assert response.json == {"Shape": "Square", "Area": 25}


def test_echo(client):
    response = client.get(
        "/echo?arg1=hello&arg2=Joey",
        base_url="https://localhost",
    )
    assert response.status_code == 200
    assert response.json == {"arg1": "hello", "arg2": "Joey"}


def test_register(client):
    register_user(client)


def test_duplicate_registration(client):
    register_user(client)
    response = client.put(
        "/register",
        json={"username": "testuser", "password": "testpass123"},
        base_url="https://localhost",
    )
    assert response.status_code == 409


@pytest.mark.parametrize("endpoint", ["/profile", "/secret"])
def test_requires_auth(client, endpoint):
    response = client.get(endpoint, base_url="https://localhost")
    assert response.status_code == 401


@pytest.mark.parametrize("endpoint", ["/profile", "/secret"])
def test_wrong_password(client, endpoint):
    register_user(client)
    response = client.get(
        endpoint,
        auth=("testuser", "wrongpassword"),
        base_url="https://localhost",
    )
    assert response.status_code == 401


@pytest.mark.parametrize("endpoint", ["/profile", "/secret"])
def test_unknown_user(client, endpoint):
    response = client.get(
        endpoint,
        auth=("unknownuser", "testpass123"),
        base_url="https://localhost",
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    "endpoint, expected_message",
    [
        ("/profile", "Hello, testuser!"),
        ("/secret", "testuser, you accessed the secret endpoint!"),
    ],
)
def test_valid_auth(client, endpoint, expected_message):
    register_user(client)
    response = client.get(
        endpoint,
        auth=("testuser", "testpass123"),
        base_url="https://localhost",
    )
    assert response.status_code == 200
    assert response.json == {"message": expected_message}