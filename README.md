# Simple FastAPI Service

A production-grade FastAPI service to identify and consolidate customer contacts across multiple purchases, following SOLID principles and modular design.

## Features
- Identify or create customer contacts by email and/or phone number
- Link multiple contacts as primary/secondary
- Merge contacts when new links are found
- Fully tested and documented
- **Deployable on AWS Lambda (serverless, free tier) with Mangum**

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

## Docker Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t bitespeed-identity:latest .
   ```
2. **Run the container:**
   ```bash
   docker run --env-file .env -p 8000:8000 bitespeed-identity:latest
   ```

## AWS Lambda (Serverless) Deployment

This project is ready to deploy on AWS Lambda using [Mangum](https://github.com/jordaneremieff/mangum) and AWS SAM (Serverless Application Model).

1. **Install AWS SAM CLI:**
   https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

2. **Build and deploy:**
   ```bash
   sam build
   sam deploy --guided
   ```
   - Follow the prompts to set up your stack and region.

3. **Get your endpoint:**
   After deploy, SAM will output an API Gateway URL you can use for your FastAPI app.

**Note:** For persistent data, use AWS RDS (Free Tier) or DynamoDB. SQLite is not recommended for production Lambda.

--- 