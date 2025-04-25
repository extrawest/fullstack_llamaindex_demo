import os
import pickle
import logging
from multiprocessing import Lock
from multiprocessing.managers import BaseManager
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.indices.base import BaseIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

index: BaseIndex | None = None
stored_docs: Dict[str, str] = {}
lock = Lock()

index_name = "./saved_index"
pkl_name = "stored_documents.pkl"


def initialize_index() -> None:
    """Create a new global index, or load one from the pre-set path."""
    global index, stored_docs
    logger.info("Initializing index...")
    embed_model = OpenAIEmbedding(model_name="text-embedding-3-small")
    with lock:
        if os.path.exists(index_name):
            logger.info(f"Loading index from {index_name}")
            try:
                index = load_index_from_storage(
                    StorageContext.from_defaults(persist_dir=index_name), embed_model=embed_model
                )
            except Exception as e:
                 logger.error(f"Failed to load index: {e}. Creating a new one.", exc_info=True)
                 index = VectorStoreIndex([], embed_model=embed_model)
                 index.storage_context.persist(persist_dir=index_name)
        else:
            logger.info(f"Creating new index at {index_name}")
            index = VectorStoreIndex([], embed_model=embed_model)
            index.storage_context.persist(persist_dir=index_name)

        if os.path.exists(pkl_name):
            logger.info(f"Loading stored documents from {pkl_name}")
            try:
                with open(pkl_name, "rb") as f:
                    stored_docs = pickle.load(f)
            except Exception as e:
                logger.error(f"Failed to load stored documents: {e}. Initializing empty.", exc_info=True)
                stored_docs = {}
        else:
            logger.info(f"Stored documents file {pkl_name} not found. Initializing empty.")
            stored_docs = {}
    logger.info("Index initialization complete.")

def query_index(query_text: str) -> Any:
    """Query the global index."""
    global index
    if not index:
        logger.error("Query attempted before index was initialized.")
        return "Error: Index not ready."
    logger.info(f"Querying index: '{query_text[:50]}...'")
    try:
        llm = OpenAI(model="gpt-4o-mini")
        query_engine = index.as_query_engine(similarity_top_k=2, llm=llm)
        response = query_engine.query(query_text)
        logger.info("Query successful.")
        return response
    except Exception as e:
        logger.error(f"Error during query: {e}", exc_info=True)
        return f"Error during query: {e}"

def insert_into_index(doc_file_path: str, doc_id: str | None = None) -> None:
    """Insert new document into global index using insert_document.

    Applies SentenceSplitter transformation during insertion.
    """
    global index, stored_docs
    if not index:
        logger.error("Insertion attempted before index was initialized.")
        return
    if not os.path.exists(doc_file_path):
        logger.error(f"File not found for insertion: {doc_file_path}")
        return

    logger.info(f"Inserting document: {doc_file_path} (ID: {doc_id or 'Auto'})")
    transformations = SentenceSplitter(chunk_size=512)

    try:
        reader = SimpleDirectoryReader(input_files=[doc_file_path])
        documents = reader.load_data()
        if not documents:
            logger.warning(f"No documents loaded from {doc_file_path}")
            return

        logger.info(f"Loaded {len(documents)} document part(s). Processing...")

        with lock:
            processed_ids = []
            for document in documents:
                effective_doc_id = doc_id if doc_id is not None else document.id_
                if not effective_doc_id:
                    effective_doc_id = os.path.basename(doc_file_path)
                    logger.warning(f"Document ID not provided or found, using filename: {effective_doc_id}")
                document.id_ = effective_doc_id

                try:
                    index.insert_document(document, transformations=transformations)
                    logger.info(f"Successfully inserted chunk for doc ID: {effective_doc_id}")
                except Exception as e:
                    logger.error(f"Failed to insert chunk for doc ID {effective_doc_id}: {e}", exc_info=True)
                    continue

                preview = document.text[:200] + ("..." if len(document.text) > 200 else "")
                stored_docs[effective_doc_id] = preview
                if effective_doc_id not in processed_ids:
                     processed_ids.append(effective_doc_id)

            if processed_ids:
                 logger.info(f"Persisting index changes for docs: {processed_ids}")
                 try:
                     index.storage_context.persist(persist_dir=index_name)
                 except Exception as e:
                     logger.error(f"Failed to persist index: {e}", exc_info=True)

                 logger.info("Persisting stored documents dictionary...")
                 try:
                     with open(pkl_name, "wb") as f:
                         pickle.dump(stored_docs, f)
                 except Exception as e:
                     logger.error(f"Failed to save stored documents: {e}", exc_info=True)
            else:
                 logger.info("No new documents were processed to persist.")

    except Exception as e:
        logger.error(f"Error processing file {doc_file_path}: {e}", exc_info=True)

    return

def get_documents_list() -> List[Dict[str, str]]:
    """Get the list of currently stored documents previews."""
    global stored_docs
    if not isinstance(stored_docs, dict):
        logger.warning("stored_docs is not a dictionary. Attempting reload.")
        if os.path.exists(pkl_name):
            try:
                with open(pkl_name, "rb") as f:
                    loaded_data = pickle.load(f)
                    if isinstance(loaded_data, dict):
                        stored_docs = loaded_data
                        logger.info(f"Reloaded {len(stored_docs)} documents from {pkl_name}.")
                    else:
                        stored_docs = {}
            except Exception as e:
                logger.error(f"Error reloading stored_docs: {e}", exc_info=True)
                stored_docs = {}
        else:
            stored_docs = {}

    documents_list = [{"id": doc_id, "text": text_preview}
                      for doc_id, text_preview in stored_docs.items()]
    logger.info(f"Returning {len(documents_list)} documents.")
    return documents_list

if __name__ == "__main__":
    initialize_index()

    logger.info("Setting up BaseManager server...")
    class IndexManagerInterface:
        def query_index(self, query_text: str) -> Any: ...
        def insert_into_index(self, filepath: str, doc_id: str | None = None) -> None: ...
        def get_documents_list(self) -> List[Dict[str, str]]: ...

    manager = BaseManager(('', 5602), b'password')
    manager.register('query_index', query_index)
    manager.register('insert_into_index', insert_into_index)
    manager.register('get_documents_list', get_documents_list)
    server = manager.get_server()

    logger.info("Server starting on port 5602...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopping.")
    finally:
        logger.info("Server stopped.")
