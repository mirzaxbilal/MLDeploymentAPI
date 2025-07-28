# Machine Learning Model Deployment API

This project allows users to use their prediction models through an API that supports both synchronous and asynchronous processing modes. 

## Tech Stack

- FastAPI – for building the RESTful API with support for async processing
- Redis – used as a message queue (via Redis Streams) and a temporary result store
- Python 3.11 – programming language used for both API and consumer service
- Docker – for containerizing the application and its services

---

## Instructions to Run:

- Step 1 - Make sure Docker and Docker Compose are installed on your machine.
- Step 2 - Start the Docker daemon if it's not already running.
- Step 3 - Rename .env.bak file to .env
- Step 3 - In the root directory of the project, run the following command in terminal: docker-compose up --build

- The application will now run at `http://localhost:8080`
- Redis server runs in the background
- Consumer service listens and processes queued jobs

---
## API Endpoints

POST /predict (Synchronously)

 -Description: Submits a prediction request to be processed synchronously.
 -Headers:
  - Async-Mode: false
 -Request Body:
   {
     "input": "some text input"
   }

Response (done):
{
    "input": "Sample input data for the model",
    "result": "mocked prediction"
}


POST /predict (Asynchronous)

 -Description: Submits a prediction request to be processed asynchronously.
 -Headers:
  - Async-Mode: true
 -Request Body:
   {
     "input": "some text input"
   }

Response (request received):
{
  "prediction_id": "uuid",
  "message": "Request received. Processing asynchronously."
}

GET /predict/{prediction_id}
 -Description: Fetches the result of a previously submitted async prediction.
 -Path Parameter: prediction_id – ID received in async response

Response (done):
{
  "prediction_id": "uuid",
  "output": {
    "input": "some text input",
    "result": "mocked prediction"
  }
}

Response (processing):
{
  "prediction_id": "uuid",
  "output": {
    "input": "some text",
    "result": "processing"
  }
}

Response (not found):
{
  "error": "Prediction ID not found."
}

---

## Assumptions

- Redis is used for both streaming and temporary result storage.
- No authentication is needed as per the requirements.
- The consumer always starts from the beginning of the stream (can be adjusted for production).

---

## Alternative Approaches Not Pursued

- Celery: Redis Streams gives you lightweight and low-latency background processing without the overhead of external brokers or complex task frameworks. It gives you  full control and simplicity in one place.
- Flask: FastAPI is faster than Flask and offers automatic data validation, type hints, and Swagger docs.
- Database Persistence: Results are not persisted to a DB; Redis is used as an in-memory store.

---

## Author

Built by Mirza Bilal
