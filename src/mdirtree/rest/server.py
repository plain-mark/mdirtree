# src/mdirtree/rest/server.py

from flask import Flask, request, jsonify
from ..generator import DirectoryStructureGenerator
import tempfile
import os

app = Flask(__name__)


@app.route("/generate", methods=["POST"])
def generate_structure():
    """REST endpoint do generowania struktury katalogów."""
    data = request.get_json()

    if not data or "structure" not in data:
        return jsonify({"error": "Missing structure in request"}), 400

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = DirectoryStructureGenerator(data["structure"])
            output_path = data.get("output_path", tmpdir)
            dry_run = data.get("dry_run", False)

            operations = generator.generate_structure(output_path, dry_run)

            return jsonify(
                {
                    "status": "success",
                    "operations": operations,
                    "output_path": output_path,
                }
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_server(host="0.0.0.0", port=5000):
    """Uruchom serwer REST."""
    app.run(host=host, port=port)


if __name__ == "__main__":
    run_server()
