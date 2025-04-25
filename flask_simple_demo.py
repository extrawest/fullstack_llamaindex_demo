import os

from flask import Flask
from flask import request
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.indices.base import BaseIndex

app = Flask(__name__)

index: BaseIndex | None = None

script_dir = os.path.dirname(os.path.abspath(__file__))
persist_dir = os.path.join(script_dir, ".index")
documents_dir = os.path.join(script_dir, "documents")

def initialize_index():
    global index
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)

    if os.path.exists(persist_dir):
        index = load_index_from_storage(storage_context)
    else:
        documents = SimpleDirectoryReader(documents_dir).load_data()
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )
        storage_context.persist(persist_dir)

@app.route("/")
def home():
    return "Hello World!"

@app.route("/query", methods=["GET"])
def query_index():
    global index
    query_text = request.args.get("text", None)
    if query_text is None:
        return (
            "No text found, please include a ?text=blah parameter in the URL",
            400,
        )
    query_engine = index.as_query_engine() #BaseIndex
    response = query_engine.query(query_text)
    return str(response), 200


def main() -> None:
    """Main entry point for the script."""
    initialize_index()


if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=5601)