# 🤖 Generation Web Scraping Practice

A FastAPI-based AI text generation API with RAG (Retrieval-Augmented Generation) capabilities, real-time web scraping, and document ingestion support.

---

## ✨ Features

- **Text Generation** - AI-powered text generation with streaming support (SSE & WebSocket)
- **RAG Pipeline** - Retrieval-Augmented Generation using Qdrant vector database
- **Web Scraping** - Real-time URL content extraction and integration into prompts
- **Document Ingestion** - PDF upload and processing for knowledge base enrichment
- **Conversation Management** - Persistent conversation history with PostgreSQL
- **Multi-Model Support** - Integration with VLLM and Ollama backends
- **Authentication** - Basic authentication for API endpoints

---

## 🏗️ Architecture

```
app/
├── main.py                 # FastAPI application entry point
├── basic_auth.py           # Authentication middleware
├── core/
│   ├── config.py          # Application settings (Pydantic)
│   ├── logging.py         # Request logging to CSV
│   ├── ml.py              # Global ML model store
│   └── database/          # Database models, repositories & routers
└── modules/
    ├── text_generation/   # Text generation endpoints & services
    │   ├── router.py      # API endpoints (POST, SSE, WebSocket)
    │   ├── services/      # Ollama client, generation logic
    │   ├── rag/           # RAG retrieval dependencies
    │   └── scraping/      # Web content extraction
    ├── document_ingestion/ # PDF upload & processing
    └── image_generation/   # (Placeholder)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL database
- Qdrant vector database
- (Optional) VLLM or Ollama instance for LLM inference

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd generataion_webscraping_practice
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   UPLOAD_CHUNK_SIZE=1048576    # 1MB
   RAG_CHUNK_SIZE=4000          # ~1k tokens
   EMBEDDING_SIZE=768

   QDRANT_HOST=localhost
   QDRANT_PORT=6333

   VLLM_API_KEY=your-vllm-api-key
   OLLAMA_API_KEY=your-ollama-api-key
   POSTGRES_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 📚 API Endpoints

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Check API and model status |

### Text Generation
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/text-generation/text-to-text` | Generate text response |
| `GET` | `/api/text-generation/stream/text-to-text/{conversation_id}` | Stream response (SSE) |
| `WS` | `/api/text-generation/ws/text-to-text` | WebSocket streaming |

### Document Ingestion
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/assets/documents/upload_file` | Upload PDF document |

### Conversations & Messages
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/api/conversations/` | List/Create conversations |
| `GET/POST` | `/api/messages/` | List/Create messages |

---

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `UPLOAD_CHUNK_SIZE` | File upload chunk size in bytes | `1048576` |
| `RAG_CHUNK_SIZE` | Text chunk size for RAG processing | `4000` |
| `EMBEDDING_SIZE` | Vector embedding dimensions | `768` |
| `QDRANT_HOST` | Qdrant server hostname | `localhost` |
| `QDRANT_PORT` | Qdrant server port | `6333` |
| `VLLM_API_KEY` | VLLM API key | - |
| `OLLAMA_API_KEY` | Ollama API key | - |
| `POSTGRES_URL` | PostgreSQL connection string | - |

---

## 📁 Project Structure

```
generataion_webscraping_practice/
├── app/                    # Application source code
├── alembic/                # Database migrations
├── uploads/                # Uploaded documents (gitignored)
├── dbstorage/              # Local database storage (gitignored)
├── qdrant_storage/         # Qdrant data (gitignored)
├── system_logs/            # Request logs (gitignored)
├── .env.example            # Environment template
├── alembic.ini             # Alembic configuration
└── README.md               # This file
```

---

## 🛠️ Development

### Running with Auto-reload
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📝 License

This project is for educational and practice purposes.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
