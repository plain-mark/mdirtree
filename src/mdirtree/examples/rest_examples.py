# src/mdirtree/examples/rest_examples.py

"""Przykłady użycia REST API mdirtree."""

from mdirtree.rest.client import MdirtreeClient
from mdirtree.rest.server import run_server
import threading
import time


def server_example():
    """Uruchom serwer w osobnym wątku."""
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)  # Poczekaj na uruchomienie serwera


def client_example():
    """Przykład użycia klienta."""
    client = MdirtreeClient()

    # Przykładowa struktura
    structure = """
    project/
    ├── src/
    │   └── main.py
    └── tests/
        └── test_main.py
    """

    # Generowanie z dry run
    result = client.generate_structure(structure, dry_run=True)
    print("Dry run results:", result)

    # Rzeczywiste generowanie
    result = client.generate_structure(structure, output_path="./output")
    print("Generation results:", result)


if __name__ == "__main__":
    server_example()
    client_example()
