# Production Ready RAG System

A FastAPI-based AI text generation API with RAG (Retrieval-Augmented Generation) capabilities, real-time web scraping, document ingestion, and multi-provider authentication.

---

## ✨ Features

- **Text Generation** — AI-powered text generation with streaming support (SSE & WebSocket)
- **RAG Pipeline** — Retrieval-Augmented Generation using Qdrant vector database
- **Web Scraping** — Real-time URL content extraction and integration into prompts
- **Document Ingestion** — PDF upload and processing for knowledge base enrichment
- **Conversation Management** — Persistent conversation history with PostgreSQL
- **Multi-Model Support** — Integration with VLLM and Ollama backends
- **JWT Authentication** — Secure JWT-based authentication with token revocation support
- **GitHub OAuth** — Sign in with GitHub via OAuth 2.0 with CSRF protection
- **Session Management** — Server-side session middleware for OAuth flows and token storage
- **Request Monitoring** — HTTP middleware that logs every request to CSV with timing and status
- **CORS Support** — Configurable Cross-Origin Resource Sharing middleware

---

## 🏗️ Architecture

```
app/
├── main.py                         # FastAPI entry point, middleware, router wiring
├── basic_auth_depricated.py        # Legacy basic auth (deprecated)
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
│   ├── authentication/
│   │   ├── router.py               # /auth/* endpoints (register, login, logout)
│   │   ├── dependencies.py         # Auth header & current user dependencies
│   │   ├── exceptions.py           # UnauthorizedException
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
│   │   ├── dependencies.py         # Ollama client dependency
│   │   ├── services/
│   │   │   ├── generation_service.py  # VLLM-based generation
│   │   │   ├── ollama_cloud_service.py # Ollama streaming client
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

### Authentication (Public)
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

The API supports **two authentication methods**: JWT Bearer Token and GitHub OAuth 2.0. All `/api/*` endpoints are protected.

### JWT Authentication Flow

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

| Model          | Table           | Key Fields                                                                                           |
| -------------- | --------------- | ---------------------------------------------------------------------------------------------------- |
| `User`         | `users`         | `id` (UUID), `github_id`, `email`, `username`, `hashed_password`, `role`                             |
| `Token`        | `tokens`        | `id` (UUID), `user_id`, `expires_at`, `is_active`, `ip_address`                                      |
| `Conversation` | `conversations` | `id`, `user_id`, `title`, `model_type`                                                               |
| `Message`      | `messages`      | `id`, `conversation_id`, `request_content`, `response_content`, `url_content`, `rag_content`, tokens |

All models include `created_at` and `updated_at` timestamps.

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
├── .gitignore              # Git ignore rules
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

### Middleware Stack

The application applies middleware in the following order:

1. **Session Middleware** — Stores OAuth state and access tokens in server-side sessions
2. **CORS Middleware** — Allows cross-origin requests (configured for all origins in development)
3. **Request Monitor** — Logs every HTTP request with timing, status code, and unique request ID

### Logging

The application uses **Loguru** for structured logging:
- Request logs are written to `system_logs/` as CSV files
- Application logs include request IDs for tracing
- Authentication errors are logged at `ERROR` level for debugging

---

## 📝 License

This project is for educational and practice purposes.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
