import pytest
import requests
import threading
import time
from mdirtree.rest.server import app
from mdirtree.rest.client import MdirtreeClient


@pytest.fixture
def client():
    """Fixture dla klienta testowego Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def rest_client():
    """Fixture dla klienta REST API."""
    return MdirtreeClient("http://localhost:5000")


@pytest.fixture(scope="module")
def server():
    """Fixture uruchamiający serwer testowy."""
    thread = threading.Thread(target=lambda: app.run(port=5000))
    thread.daemon = True
    thread.start()
    time.sleep(1)  # Poczekaj na uruchomienie serwera
    yield
    # Serwer zostanie zamknięty automatycznie po zakończeniu testów


def test_generate_endpoint(client):
    """Test endpointu /generate."""
    data = {
        "structure": """
        project/
        └── src/
            └── main.py
        """,
        "dry_run": True,
    }

    response = client.post("/generate", json=data)
    assert response.status_code == 200

    result = response.get_json()
    assert "status" in result
    assert result["status"] == "success"
    assert "operations" in result
    assert len(result["operations"]) > 0


def test_missing_structure(client):
    """Test błędu przy braku struktury."""
    response = client.post("/generate", json={})
    assert response.status_code == 400

    result = response.get_json()
    assert "error" in result


def test_client_dry_run(rest_client, server):
    """Test klienta w trybie dry run."""
    structure = """
    project/
    └── src/
        └── main.py
    """

    result = rest_client.generate_structure(structure, dry_run=True)
    assert "status" in result
    assert result["status"] == "success"
    assert "operations" in result
    assert len(result["operations"]) > 0


def test_client_error_handling(rest_client, server):
    """Test obsługi błędów w kliencie."""
    with pytest.raises(requests.exceptions.HTTPError):
        rest_client.generate_structure("")  # Pusta struktura powinna zwrócić błąd
