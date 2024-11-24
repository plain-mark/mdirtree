import requests
from typing import Dict, List, Optional


class MdirtreeClient:
    """Klient REST API dla mdirtree."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")

    def generate_structure(
        self, structure: str, output_path: Optional[str] = None, dry_run: bool = False
    ) -> Dict:
        """
        Wyślij żądanie generowania struktury do serwera.

        Args:
            structure: ASCII art struktury katalogów
            output_path: Opcjonalna ścieżka wyjściowa
            dry_run: Czy tylko symulować operacje

        Returns:
            Dict z odpowiedzią serwera
        """
        data = {"structure": structure, "dry_run": dry_run}

        if output_path:
            data["output_path"] = output_path

        response = requests.post(f"{self.base_url}/generate", json=data)
        response.raise_for_status()

        return response.json()
