# Simple FastAPI Service

A production-grade FastAPI service to identify and consolidate customer contacts across multiple purchases, following SOLID principles and modular design.

## Features
- Identify or create customer contacts by email and/or phone number
- Link multiple contacts as primary/secondary
- Merge contacts when new links are found
- Fully tested and documented

## Setup

1. **Clone the repository**
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```
   DATABASE_URL=sqlite:///./test.db
   ```
5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```
6. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Usage

### Identify Contact
- **POST** `/identify`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "phoneNumber": "1234567890"
  }
  ```
- **Response:**
  ```json
  {
    "primaryContatctId": 1,
    "emails": ["user@example.com"],
    "phoneNumbers": ["1234567890"],
    "secondaryContactIds": []
  }
  ```

See [http://localhost:8000/docs](http://localhost:8000/docs) for full OpenAPI documentation.

## Testing

```bash
PYTHONPATH=. pytest
```

## Deployment
- For production, use a robust database (e.g., PostgreSQL) and a production ASGI server (e.g., Gunicorn with Uvicorn workers).
- You can also use Docker for containerized deployment.

--- 