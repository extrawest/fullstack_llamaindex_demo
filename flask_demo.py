import os
from multiprocessing.managers import BaseManager
from typing import Any, List, Dict, Tuple, Union
from flask import Flask, request, jsonify, Response # Import Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

class IndexManagerInterface:
    def query_index(self, query_text: str) -> Any: ...
    def insert_into_index(self, filepath: str, doc_id: str | None = None) -> None: ...
    def get_documents_list(self) -> List[Dict[str, Any]]: ...

manager_client: BaseManager = BaseManager(('', 5602), b'password')
manager_client.register('query_index')
manager_client.register('insert_into_index')
manager_client.register('get_documents_list')
manager_client.connect()

manager: IndexManagerInterface = manager_client

FlaskResponse = Union[Response, Tuple[str, int], Tuple[Response, int]]

@app.route("/query", methods=["GET"])
def query_index() -> FlaskResponse:
    """Handles GET requests to query the index.

    Retrieves the query text from the request arguments,
    calls the remote query_index method, and returns the
    response and source documents in JSON format.
    """
    query_text = request.args.get("text")
    if query_text is None:
        return jsonify(error="No text found, please include a ?text=blah parameter"), 400

    try:
        response = manager.query_index(query_text)._getvalue()

        sources = []
        for x in getattr(response, 'source_nodes', []):
            node = getattr(x, 'node', None)
            if node:
                sources.append({
                    "text": getattr(node, 'text', 'N/A'),
                    "similarity": round(getattr(x, 'score', 0.0), 2),
                    "doc_id": getattr(node, 'node_id', 'N/A'),
                    "start": getattr(node, 'metadata', {}).get('start'),
                    "end": getattr(node, 'metadata', {}).get('end'),
                })
            else:
                 app.logger.warning(f"Unexpected source node structure: {x}")

        response_json = {
            "text": str(response),
            "sources": sources
        }
        return jsonify(response_json)
    except Exception as e:
        app.logger.error(f"Error querying index: {e}", exc_info=True)
        return jsonify(error="An error occurred while querying the index."), 500


@app.route("/uploadFile", methods=["POST"])
def upload_file() -> FlaskResponse:
    """Handles POST requests to upload a file and insert it into the index.

    Saves the uploaded file temporarily, calls the remote insert_into_index
    method, and cleans up the temporary file.
    """
    if 'file' not in request.files:
        return jsonify(error="Please send a POST request with a file"), 400

    uploaded_file = request.files["file"]
    if not uploaded_file or not uploaded_file.filename:
         return jsonify(error="Invalid file provided"), 400

    filename = secure_filename(uploaded_file.filename)
    docs_dir = os.path.join(app.root_path, 'documents')
    os.makedirs(docs_dir, exist_ok=True)
    filepath = os.path.join(docs_dir, filename)

    try:
        uploaded_file.save(filepath)
        app.logger.info(f"File temporarily saved to {filepath}")

        use_filename_as_id = request.form.get("filename_as_doc_id") is not None
        doc_id_to_pass = filename if use_filename_as_id else None

        manager.insert_into_index(filepath, doc_id=doc_id_to_pass)
        app.logger.info(f"Remote insert_into_index called for {filepath} with doc_id: {doc_id_to_pass}")

        return jsonify(message=f"File '{filename}' uploaded and sent for indexing."), 200

    except Exception as e:
        app.logger.error(f"Error during file upload or indexing call: {e}", exc_info=True)
        return jsonify(error="An error occurred during file processing."), 500
    finally:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                app.logger.info(f"Cleaned up temporary file: {filepath}")
            except OSError as e:
                app.logger.error(f"Error removing temporary file {filepath}: {e}", exc_info=True)


@app.route("/getDocuments", methods=["GET"])
def get_documents() -> Response:
    """Handles GET requests to retrieve the list of indexed documents."""
    try:
        document_list = manager.get_documents_list()._getvalue()
        return jsonify(document_list)
    except Exception as e:
        app.logger.error(f"Error getting documents list: {e}", exc_info=True)
        return jsonify(error="An error occurred while retrieving documents."), 500


@app.route("/")
def home() -> str:
    """Returns a simple welcome message for the root endpoint."""
    return "Hello, World! Welcome to the llama_index docker image!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5601, debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
