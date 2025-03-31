import requests
import logging
from typing import Dict, List, Optional


class MdirtreeClient:
    """REST API client for mdirtree."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")
        self.logger = logging.getLogger(__name__)

    def generate_structure(
            self, structure: str, output_path: Optional[str] = None, dry_run: bool = False
    ) -> Dict:
        """
        Send a request to generate directory structure.

        Args:
            structure: ASCII art directory structure
            output_path: Optional output path (server-side)
            dry_run: Whether to only simulate operations

        Returns:
            Dict with server response
        """
        data = {"structure": structure, "dry_run": dry_run}

        if output_path:
            data["output_path"] = output_path

        self.logger.debug(f"Sending request to {self.base_url}/generate")

        try:
            response = requests.post(f"{self.base_url}/generate", json=data)
            response.raise_for_status()

            self.logger.debug("Request successful")
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise