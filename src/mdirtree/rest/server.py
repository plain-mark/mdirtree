from flask import Flask, request, jsonify
import tempfile
import os
import logging

from ..generator import DirectoryStructureGenerator

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route("/generate", methods=["POST"])
def generate_structure():
    """REST endpoint for generating directory structures."""
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
        logger.error(f"Error generating structure: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def run_server(host="0.0.0.0", port=5000, debug=False):
    """Run the REST server."""
    logger.info(f"Starting mdirtree server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    run_server()