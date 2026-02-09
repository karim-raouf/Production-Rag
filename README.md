# Production Ready RAG System

A FastAPI-based AI text generation API with RAG (Retrieval-Augmented Generation) capabilities, real-time web scraping, and document ingestion support.

---

## ✨ Features

- **Text Generation** - AI-powered text generation with streaming support (SSE & WebSocket)
- **RAG Pipeline** - Retrieval-Augmented Generation using Qdrant vector database
- **Web Scraping** - Real-time URL content extraction and integration into prompts
- **Document Ingestion** - PDF upload and processing for knowledge base enrichment
- **Conversation Management** - Persistent conversation history with PostgreSQL
- **Multi-Model Support** - Integration with VLLM and Ollama backends
- **JWT Authentication** - Secure JWT-based authentication with token revocation support

---

## 🏗️ Architecture

```
app/
├── main.py                     # FastAPI application entry point
├── basic_auth.py               # Basic authentication (deprecated)
├── core/
│   ├── config.py               # Application settings (Pydantic)
│   ├── logging.py              # Request logging to CSV
│   ├── ml.py                   # Global ML model store
│   └── database/
│       ├── database.py         # AsyncEngine & session factory
│       ├── models.py           # SQLAlchemy ORM models (User, Token, Conversation, Message)
│       ├── dependencies.py     # Database session dependency
│       ├── repositories/       # Data access layer
│       │   ├── users.py
│       │   ├── tokens.py
│       │   ├── conversations.py
│       │   └── messages.py
│       ├── services/           # Business logic layer
│       │   ├── users.py
│       │   ├── tokens.py
│       │   ├── conversations.py
│       │   └── messages.py
│       ├── schemas/            # Pydantic request/response models
│       └── routers/            # CRUD API endpoints
│           ├── conversations/
│           └── messages/
├── modules/
│   ├── authentication/         # JWT authentication module
│   │   ├── router.py           # /auth/* endpoints (register, login, logout)
│   │   ├── dependencies.py     # Auth header & current user deps
│   │   ├── exceptions.py       # UnauthorizedException
│   │   └── services/
│   │       ├── auth.py         # AuthService (register, authenticate, logout)
│   │       └── password.py     # Password hashing utilities
│   ├── text_generation/        # Text generation module
│   │   ├── router.py           # API endpoints (POST, SSE, WebSocket)
│   │   ├── schemas.py          # Request/response schemas
│   │   ├── dependencies.py     # Ollama client dependency
│   │   ├── services/           # Generation & streaming logic
│   │   │   ├── generation_service.py
│   │   │   ├── ollama_cloud_service.py
│   │   │   └── stream.py       # WebSocket manager
│   │   ├── rag/                # RAG retrieval dependencies
│   │   ├── scraping/           # Web content extraction
│   │   └── infrastructure/     # Model lifecycle management
│   ├── document_ingestion/     # PDF upload & processing
│   └── image_generation/       # (Placeholder)
└── pages/                      # Static files
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

   # JWT Settings
   JWT_SECRET_KEY=your-super-secret-key-change-in-production
   JWT_ALGORITHM=HS256
   JWT_EXPIRES_IN_MINUTES=60
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

---

## 📚 API Endpoints

### Authentication (Public)
| Method | Endpoint         | Description                |
| ------ | ---------------- | -------------------------- |
| `POST` | `/auth/register` | Register a new user        |
| `POST` | `/auth/token`    | Login and get access token |
| `POST` | `/auth/logout`   | Logout and revoke token    |

### Health Check
| Method | Endpoint      | Description                |
| ------ | ------------- | -------------------------- |
| `GET`  | `/api/health` | Check API and model status |

### Text Generation (Protected)
| Method | Endpoint                                                     | Description            |
| ------ | ------------------------------------------------------------ | ---------------------- |
| `POST` | `/api/text-generation/text-to-text`                          | Generate text response |
| `GET`  | `/api/text-generation/stream/text-to-text/{conversation_id}` | Stream response (SSE)  |
| `WS`   | `/api/text-generation/ws/text-to-text`                       | WebSocket streaming    |

### Document Ingestion (Protected)
| Method | Endpoint                            | Description         |
| ------ | ----------------------------------- | ------------------- |
| `POST` | `/api/assets/documents/upload_file` | Upload PDF document |

### Conversations & Messages (Protected)
| Method     | Endpoint                  | Description               |
| ---------- | ------------------------- | ------------------------- |
| `GET/POST` | `/api/conversations/`     | List/Create conversations |
| `GET`      | `/api/conversations/{id}` | Get conversation by ID    |
| `GET/POST` | `/api/messages/`          | List/Create messages      |

---

## 🔐 Authentication

The API uses **JWT Bearer Token** authentication. All `/api/*` endpoints are protected.

### Authentication Flow

1. **Register** a new user:
   ```bash
   curl -X POST http://localhost:8080/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "password": "password"}'
   ```

2. **Login** to get access token:
   ```bash
   curl -X POST http://localhost:8080/auth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user&password=password"
   ```

3. **Use token** for protected endpoints:
   ```bash
   curl http://localhost:8080/api/health \
     -H "Authorization: Bearer <access_token>"
   ```

4. **Logout** to revoke token:
   ```bash
   curl -X POST http://localhost:8080/auth/logout \
     -H "Authorization: Bearer <access_token>"
   ```

---

## 🔧 Configuration

| Variable                 | Description                        | Default     |
| ------------------------ | ---------------------------------- | ----------- |
| `UPLOAD_CHUNK_SIZE`      | File upload chunk size in bytes    | `1048576`   |
| `RAG_CHUNK_SIZE`         | Text chunk size for RAG processing | `4000`      |
| `EMBEDDING_SIZE`         | Vector embedding dimensions        | `768`       |
| `QDRANT_HOST`            | Qdrant server hostname             | `localhost` |
| `QDRANT_PORT`            | Qdrant server port                 | `6333`      |
| `VLLM_API_KEY`           | VLLM API key                       | -           |
| `OLLAMA_API_KEY`         | Ollama API key                     | -           |
| `POSTGRES_URL`           | PostgreSQL connection string       | -           |
| `JWT_SECRET_KEY`         | Secret key for JWT token signing   | -           |
| `JWT_ALGORITHM`          | Algorithm for JWT signing          | `HS256`     |
| `JWT_EXPIRES_IN_MINUTES` | Token expiration time in minutes   | `60`        |

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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
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

### Logging

The application uses **Loguru** for structured logging:
- Request logs are written to `system_logs/` as CSV files
- Application logs include request IDs for tracing

---

## 📝 License

This project is for educational and practice purposes.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
