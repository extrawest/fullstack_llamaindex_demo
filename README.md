# Document Indexing and Query Application

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)]()
[![Maintainer](https://img.shields.io/static/v1?label=Yevhen%20Ruban&message=Maintainer&color=red)](mailto:yevhen.ruban@extrawest.com)
[![Ask Me Anything !](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)]()
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![GitHub release](https://img.shields.io/badge/release-v1.0.0-blue)

## 📝 Overview

This application is a full-stack document indexing and retrieval system that allows users to upload documents, index their content, and perform natural language queries against the indexed documents. It utilizes LlamaIndex, OpenAI embeddings, and a modern React frontend to provide an interactive experience for semantic search and document retrieval.

## 🚀 Features

- **Document Upload**: Upload text files to be indexed and stored
- **Document Management**: View a list of all uploaded documents
- **Semantic Search**: Ask questions in natural language and get AI-generated answers
- **Source References**: View the source documents and passages used to generate answers
- **Real-time Responses**: Asynchronous processing with live feedback

## 🏗️ Architecture

The application follows a multi-service architecture:

### Backend Components:

1. **Index Server** (`index_server.py`)
   - Core document processing and indexing logic
   - Uses LlamaIndex and OpenAI embeddings for semantic understanding
   - Maintains a vector store index for document retrieval
   - Exposes services via a BaseManager server on port 5602

2. **API Server** (`flask_demo.py`)
   - Flask-based REST API
   - Handles document upload, query requests, and document listing
   - Communicates with the index server using BaseManager client
   - Exposes endpoints on port 5601

### Frontend Components:

1. **React Application** (`react_frontend/`)
   - TypeScript React application
   - Responsive UI for document management and querying
   - Components for uploading, viewing documents, and querying the index

## 🔧 Technologies Used

### Backend
- **Python 3.11**
- **Flask**: Web framework for API endpoints
- **LlamaIndex**: Document indexing and retrieval library
- **OpenAI API**: For embeddings and LLM capabilities
- **Multiprocessing**: For inter-process communication

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **SCSS**: Styling
- **React Spinners**: Loading indicators
- **ClassNames**: Conditional class application

## 📋 Prerequisites

- Python 3.11+
- Node.js 16+
- OpenAI API key

## 🛠️ Installation

### Manual Installation

1. **Clone the repository**

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set up React frontend**
   ```bash
   cd react_frontend
   npm install
   ```

4. **Set OpenAI API key**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

5. **Start the application**
   ```bash
   ./launch_app.sh
   ```

### Docker Installation

1. **Build the Docker image**
   ```bash
   docker build -t document-indexer .
   ```

2. **Run the container**
   ```bash
   docker run -p 5601:5601 -p 3000:3000 -e OPENAI_API_KEY="your-api-key-here" document-indexer
   ```

## 💻 Usage

1. **Access the application**
   - Open a web browser and navigate to `http://localhost:3000`

2. **Upload documents**
   - Use the upload area to select and upload text files
   - Check the document list to verify successful uploads

3. **Query the index**
   - Type a natural language question in the query box
   - Press Enter to submit the query
   - View the AI-generated answer and source references

## 📚 API Endpoints

- **GET `/query?text=<query_text>`**
  - Submit a query to the index
  - Returns the answer text and source references

- **POST `/uploadFile`**
  - Upload a document for indexing
  - Form data: `file` (document file), `filename_as_doc_id` (optional)

- **GET `/getDocuments`**
  - Retrieve the list of indexed documents

## 🧪 Development

### Structure

```
.
├── documents/                 # Document storage directory
├── react_frontend/            # React frontend application
│   ├── src/
│   │   ├── apis/              # API client code
│   │   ├── components/        # React components
│   │   └── ...
│   └── ...
├── saved_index/               # Persisted vector index storage
├── flask_demo.py              # Flask API server
├── flask_simple_demo.py       # Simplified Flask demo
├── index_server.py            # LlamaIndex processing server
├── launch_app.sh              # Application startup script
├── requirements.txt           # Python dependencies
└── Dockerfile                 # Docker configuration
```

### Running in development mode

1. Start the index server:
   ```bash
   python index_server.py
   ```

2. Start the Flask API server:
   ```bash
   python flask_demo.py
   ```

3. Start the React development server:
   ```bash
   cd react_frontend
   npm start
   ```

## 🔒 Security Considerations

- The application uses a hardcoded password for the BaseManager server
- No user authentication is implemented in this version
- Data is stored locally in the file system
