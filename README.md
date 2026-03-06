# Production Ready RAG System

A FastAPI-based AI text generation API with RAG (Retrieval-Augmented Generation) capabilities, real-time web scraping, document ingestion, security guardrails, and multi-provider auth.

---

## ✨ Features

- **Text Generation** — AI-powered text generation with streaming support (SSE & WebSocket)
- **RAG Pipeline** — Retrieval-Augmented Generation using Qdrant vector database
- **Web Scraping** — Real-time URL content extraction and integration into prompts
- **Document Ingestion** — PDF upload and processing for knowledge base enrichment
- **Security Guardrails** — Dual-layer LLM-based safety system (input + output) with score-based classification
- **Conversation Management** — Persistent conversation history with PostgreSQL
- **Multi-Model Support** — Integration with VLLM and Ollama backends
- **JWT Auth** — Secure JWT-based auth with token revocation support
- **GitHub OAuth** — Sign in with GitHub via OAuth 2.0 with CSRF protection
- **Session Management** — Server-side session middleware for OAuth flows and token storage
- **Request Monitoring** — HTTP middleware that logs every request to CSV with timing and status
- **CORS Support** — Configurable Cross-Origin Resource Sharing middleware

---

## 🛡️ Security Guardrails

The system implements a **dual-layer guardrail architecture** using a dedicated LLM classifier that runs independently from the main chat model.

### Input Guardrail

Analyzes user queries **before** they reach the chat model. Detects:
- Prompt injection & jailbreak attempts
- System prompt extraction attacks
- Code injection & shell command execution
- Social engineering & harmful content requests

Returns `True` (safe) or `False` (unsafe). Runs **concurrently** with URL/RAG content fetching via `asyncio.create_task` — if the guardrail rejects, pending fetch tasks are cancelled immediately.

### Output Guardrail

Analyzes the AI-generated response **after** generation, using a **score-based system** (1-10):

| Score | Severity   | Action                            |
| ----- | ---------- | --------------------------------- |
| 1-3   | Safe       | Allowed                           |
| 4-6   | Suspicious | Allowed (below default threshold) |
| 7-8   | Unsafe     | Blocked                           |
| 9-10  | Critical   | Blocked                           |

Checks for: leaked system instructions, harmful content, sensitive data exposure, bypassed safety, and manipulation.

- **Non-streaming endpoint** — Blocks unsafe responses and returns a safe static message. Original response is saved to DB for auditing.
- **Streaming endpoint** — Runs after the stream completes. If unsafe, sends `[RETRACTED]` event to the client.

### Fail-Open Design

Both guardrails are configured with `fail_open=True` by default — if the guardrail times out or errors, the request is **allowed** to proceed. This prevents guardrail failures from blocking the entire service.

---

## 🏗️ Architecture

```
app/
├── main.py                         # FastAPI entry point, middleware, router wiring
├── core/
│   ├── config.py                   # Application settings (Pydantic BaseSettings)
│   ├── logging.py                  # Request logging to CSV via Loguru
│   ├── ml.py                       # Global ML model store
│   └── database/
│       ├── database.py             # AsyncEngine & session factory
│       ├── models.py               # SQLAlchemy ORM models (User, Token, Conversation, Message)
│       ├── dependencies.py         # Database session dependency
│       ├── repositories/           # Data access layer (CRUD operations)
│       │   ├── users.py
│       │   ├── tokens.py
│       │   ├── conversations.py
│       │   └── messages.py
│       ├── services/               # Business logic layer
│       │   ├── users.py
│       │   ├── tokens.py
│       │   ├── conversations.py
│       │   └── messages.py
│       ├── schemas/                # Pydantic request/response models
│       │   ├── users.py
│       │   ├── tokens.py
│       │   ├── conversations.py
│       │   └── messages.py
│       └── routers/                # CRUD API endpoints
│           ├── conversations/
│           └── messages/
├── modules/
│   ├── auth/
│   │   ├── router.py               # /auth/* endpoints (register, login, logout)
│   │   ├── dependencies.py         # Auth header & current user dependencies
│   │   ├── exceptions.py           # UnauthenticatedException
│   │   ├── services/
│   │   │   ├── auth.py             # AuthService (register, authenticate, logout)
│   │   │   └── password.py         # Password hashing utilities (bcrypt)
│   │   └── oauth/
│   │       ├── router.py           # OAuth router aggregator
│   │       ├── config.py           # OAuth credentials from AppSettings
│   │       ├── github/
│   │       │   ├── router.py       # /oauth/github/* endpoints (login, callback)
│   │       │   └── dependencies.py # CSRF check, token exchange, user info
│   │       └── google/             # (Placeholder for Google OAuth)
│   ├── text_generation/
│   │   ├── router.py               # API endpoints (POST, SSE, WebSocket)
│   │   ├── schemas.py              # Request/response schemas
│   │   ├── dependencies.py         # Annotated FastAPI deps (client, guardrails)
│   │   ├── guardrails/
│   │   │   ├── schema.py           # InputGuardResponse & OutputGuardResponse
│   │   │   ├── input_guardrail.py  # InputGuardrail class (True/False classification)
│   │   │   └── output_guardrail.py # OutputGuardrail class (1-10 score classification)
│   │   ├── services/
│   │   │   ├── generation_service.py  # VLLM-based generation
│   │   │   ├── ollama_cloud_service.py # Ollama chat client (invoke + streaming)
│   │   │   └── stream.py           # WebSocket connection manager
│   │   ├── rag/
│   │   │   ├── dependencies.py     # RAG content dependency
│   │   │   ├── repository.py       # Qdrant vector store operations
│   │   │   ├── service.py          # RAG retrieval logic
│   │   │   ├── extractor.py        # Embedding extraction
│   │   │   └── transform.py        # Text chunking & transformation
│   │   ├── scraping/
│   │   │   ├── dependencies.py     # URL content dependency
│   │   │   └── service.py          # Web content extraction
│   │   └── infrastructure/
│   │       └── model_lifecycle.py   # Model loading & cleanup at startup/shutdown
│   ├── document_ingestion/
│   │   ├── router.py               # /api/assets/documents/* endpoints
│   │   ├── schema.py               # Upload schemas
│   │   ├── service.py              # PDF processing & chunking
│   │   └── dependencies.py         # File upload dependencies
│   └── image_generation/           # (Placeholder)
└── pages/                          # Static HTML files
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

   # GitHub OAuth
   GITHUB_OAUTH_CLIENT_ID=your-github-client-id
   GITHUB_OAUTH_CLIENT_SECRET=your-github-client-secret
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

### Auth (Public)
| Method | Endpoint         | Description                |
| ------ | ---------------- | -------------------------- |
| `POST` | `/auth/register` | Register a new user        |
| `POST` | `/auth/token`    | Login and get access token |
| `POST` | `/auth/logout`   | Logout and revoke token    |

### GitHub OAuth (Public)
| Method | Endpoint                 | Description                                    |
| ------ | ------------------------ | ---------------------------------------------- |
| `GET`  | `/oauth/github/login`    | Redirect to GitHub for authorization           |
| `GET`  | `/oauth/github/callback` | GitHub callback — exchanges code for JWT token |

### Health Check
| Method | Endpoint      | Description                |
| ------ | ------------- | -------------------------- |
| `GET`  | `/api/health` | Check API and model status |

### Text Generation (Protected)
| Method | Endpoint                                                     | Description                        |
| ------ | ------------------------------------------------------------ | ---------------------------------- |
| `POST` | `/api/text-generation/text-to-text/vllm`                     | Generate text via VLLM             |
| `POST` | `/api/text-generation/text-to-text/ollama/{conversation_id}` | Generate text via Ollama (guarded) |
| `GET`  | `/api/text-generation/stream/text-to-text/{conversation_id}` | Stream response via SSE (guarded)  |
| `WS`   | `/api/text-generation/ws/text-to-text`                       | WebSocket streaming                |

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

## 🔐 Auth

The API supports **two auth methods**: JWT Bearer Token and GitHub OAuth 2.0. All `/api/*` endpoints are protected.

### JWT Auth Flow

1. **Register** a new user:
   ```bash
   curl -X POST http://localhost:8080/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "email": "user@example.com", "password": "password"}'
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

### GitHub OAuth Flow

1. Navigate to `http://localhost:8080/oauth/github/login`
2. User is redirected to GitHub for authorization
3. GitHub redirects back to `/oauth/github/callback` with an authorization code
4. The server exchanges the code for an access token, fetches user info, and creates/links the account
5. A JWT token is stored in the session and the user is redirected to `/`

> **Note:** GitHub OAuth requires a registered GitHub OAuth App. Set `GITHUB_OAUTH_CLIENT_ID` and `GITHUB_OAUTH_CLIENT_SECRET` in your `.env` file. The callback URL in your GitHub App should point to `http://localhost:8080/oauth/github/callback`.

---

## 🔧 Configuration

| Variable                     | Description                        | Default     |
| ---------------------------- | ---------------------------------- | ----------- |
| `UPLOAD_CHUNK_SIZE`          | File upload chunk size in bytes    | `1048576`   |
| `RAG_CHUNK_SIZE`             | Text chunk size for RAG processing | `4000`      |
| `EMBEDDING_SIZE`             | Vector embedding dimensions        | `768`       |
| `QDRANT_HOST`                | Qdrant server hostname             | `localhost` |
| `QDRANT_PORT`                | Qdrant server port                 | `6333`      |
| `VLLM_API_KEY`               | VLLM API key                       | —           |
| `OLLAMA_API_KEY`             | Ollama API key                     | —           |
| `POSTGRES_URL`               | PostgreSQL async connection string | —           |
| `JWT_SECRET_KEY`             | Secret key for JWT token signing   | —           |
| `JWT_ALGORITHM`              | Algorithm for JWT signing          | `HS256`     |
| `JWT_EXPIRES_IN_MINUTES`     | Token expiration time in minutes   | `60`        |
| `GITHUB_OAUTH_CLIENT_ID`     | GitHub OAuth App client ID         | —           |
| `GITHUB_OAUTH_CLIENT_SECRET` | GitHub OAuth App client secret     | —           |

---

## 🗄️ Database Models

The application uses **SQLAlchemy 2.0** async ORM with **PostgreSQL** and **Alembic** for migrations.

| Model          | Table           | Key Fields                                                                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `User`         | `users`         | `id` (UUID), `github_id`, `email`, `username`, `hashed_password`, `role`, `is_active`                                    |
| `Token`        | `tokens`        | `id` (UUID), `user_id`, `expires_at`, `is_active`, `ip_address`                                                          |
| `Conversation` | `conversations` | `id`, `user_id`, `title`, `model_type`                                                                                   |
| `Message`      | `messages`      | `id`, `conversation_id`, `request_content`, `response_content`, `thinking_content`, `url_content`, `rag_content`, tokens |

All models include `created_at` and `updated_at` timestamps.

---

## 📁 Project Structure

```
generataion_webscraping_practice/
├── app/                    # Application source code
├── alembic/                # Database migrations
├── tests/                  # Unit tests (pytest)
│   ├── conftest.py         # Shared fixtures (mock DB, fake user, test client)
│   ├── test_schemas.py     # Pydantic schema validation tests
│   ├── test_password_service.py  # Password hashing & verification tests
│   ├── test_auth_service.py      # Auth service tests (register, login, token)
│   ├── test_guardrails.py        # Input guardrail classification tests
│   └── test_conversation_endpoints.py  # API endpoint tests (CRUD)
├── uploads/                # Uploaded documents (gitignored)
├── dbstorage/              # Local database storage (gitignored)
├── qdrant_storage/         # Qdrant data (gitignored)
├── system_logs/            # Request logs (gitignored)
├── .env.example            # Environment template
├── alembic.ini             # Alembic configuration
├── pytest.ini              # Pytest configuration
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## 🛠️ Development

### Running with Auto-reload
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Testing

The project uses **pytest** with **pytest-asyncio** for async tests and **pytest-mock** for mocking.

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock httpx

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_schemas.py -v

# Run a specific test class
pytest tests/test_auth_service.py::TestRegisterUser -v
```

| Test File                        | What It Tests                                    | Concepts Used                              |
| -------------------------------- | ------------------------------------------------ | ------------------------------------------ |
| `test_schemas.py`                | Pydantic schema validation                       | `pytest.raises`, Arrange-Act-Assert        |
| `test_password_service.py`       | Bcrypt hashing & verification                    | `async` tests                              |
| `test_auth_service.py`           | Registration, login, token validation            | `mocker.AsyncMock()`, `mocker.MagicMock()` |
| `test_guardrails.py`             | Input classification, timeouts, fail-open/closed | Mocking external APIs                      |
| `test_conversation_endpoints.py` | Conversations CRUD API                           | `httpx.AsyncClient`, `mocker.patch()`      |

> **Note:** All tests run in-memory with mocked dependencies — no PostgreSQL, Qdrant, or LLM instance required.

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Dependency Injection Pattern

The text generation module uses **`Annotated` type aliases** for clean dependency injection:

```python
OllamaClientDep   = Annotated[OllamaCloudChatClient, Depends(get_ollama_client)]
InputGuardrailDep  = Annotated[InputGuardrail, Depends(get_input_guardrail)]
OutputGuardrailDep = Annotated[OutputGuardrail, Depends(get_output_guardrail)]
```

Each guardrail is a standalone class with its own `AsyncClient`, injected via FastAPI's `Depends()` — fully decoupled from the chat service.

### Middleware Stack

The application applies middleware in the following order:

1. **Session Middleware** — Stores OAuth state and access tokens in server-side sessions
2. **CORS Middleware** — Allows cross-origin requests (configured for all origins in development)
3. **Request Monitor** — Logs every HTTP request with timing, status code, and unique request ID

### Logging

The application uses **Loguru** for structured logging:
- Request logs are written to `system_logs/` as CSV files
- Application logs include request IDs for tracing
- Auth errors are logged at `ERROR` level for debugging
- Guardrail decisions are logged with classification details (score, threshold, allowed status)

---

## 📝 License

This project is for educational and practice purposes.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
