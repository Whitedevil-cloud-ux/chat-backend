# Chat Summarizer Backend

A Django-powered backend for a smart chat summarization app that:
- Handles conversations through REST API
- Summarizes chats using Groq AI
- Provides intelligent queries across past chats using vector embeddings

---

## Tech Stack
- Python 3.12
- Django REST Framework
- Groq AI (`groq-python`)
- ChromaDB for embeddings search
- PostgreSQL on Render (optional local SQLite)

---

## Installation

1. Clone the repo
    ```bash
    git clone https://github.com/yourusername/chat-backend.git
    cd chat-backend
    ```

2. Create and activate virtual environment
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

4. Apply database migrations
    ```bash
    python manage.py migrate
    ```

5. Create `.env` file
    ```bash
    cp .env.example .env
    ```
    Add your actual secrets to `.env`.

6. Run development server
    ```bash
    python manage.py runserver
    ```

---

## API Routes

| Method | Endpoint                | Description |
|--------|--------------------------|-------------|
| POST   | `/api/chat/start/`       | Start a new conversation |
| POST   | `/api/chat/send/`        | Send a message, get an AI reply + follow-ups |
| POST   | `/api/chat/end/`         | End and summarize a conversation |
| GET    | `/api/chat/<id>/`        | Get full chat by id |
| POST   | `/api/chat/query/`       | Ask AI a question across past conversations |

---

## Environment Variables (`.env`)

DJANGO_SECRET_KEY=your_secret_here
GROQ_API_KEY=your_groq_key_here
CHROMA_DB_PATH=./chroma_data
DEBUG=True
DATABASE_URL=postgresql://user:pass@host:port/dbname