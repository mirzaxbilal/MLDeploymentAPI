import uuid
from fastapi import APIRouter, Header, status
from fastapi.responses import JSONResponse
from app.services.predictor import mock_model_predict
from app.models.schema import PredictRequest, PredictResponse, PredictResponseAsync, PredictResultAsync
from app.utils.redis_client import redis_stream
from app.utils.constants import STREAM_KEY, RESULT_PREFIX

router = APIRouter()

# POST endpoint to handle prediction requests
@router.post("/predict")
async def predict(
    request: PredictRequest,
    async_mode: str = Header(default = "false", alias = "Async-Mode")
):
    # If async mode is enabled, push the task to Redis Stream
    if async_mode.lower() == "true":
        prediction_id = str(uuid.uuid4())  # Generate a unique ID
        redis_stream.xadd(STREAM_KEY, {"input": request.input, "prediction_id": prediction_id})  # Push to stream

        # Return the ID with a "processing" status
        return JSONResponse(
            status_code = status.HTTP_202_ACCEPTED,
            content = PredictResultAsync(
                prediction_id = prediction_id,
                message = "Request received. Processing asynchronously."
            ).model_dump()
        )

    # Otherwise, process synchronously using the mock model
    try:
        result = mock_model_predict(request.input)
    except Exception as e:
        # Handle prediction failure
        return JSONResponse(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            content = {"error": f"Prediction failed: {str(e)}"}
        )

    # Return the actual prediction result
    return JSONResponse(
        status_code = status.HTTP_200_OK,
        content = PredictResponse(
            input = request.input,
            result = result["result"]
        ).model_dump()
    )

# GET endpoint to retrieve result by prediction ID
@router.get("/predict/{prediction_id}")
async def get_result(prediction_id: str):
    key = RESULT_PREFIX + prediction_id  # Build Redis key

    # Check if the result exists in Redis
    if not redis_stream.exists(key):
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {"error": "Prediction ID not found."}
        )

    result = redis_stream.hgetall(key)  # Get result from Redis hash

    # If prediction is still processing, return a message
    if result.get("status") == "processing":
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {"error": "Prediction is still being processed."}
        )

    # Return the final result
    return JSONResponse(
        status_code = status.HTTP_200_OK,
        content = PredictResponseAsync(
            prediction_id = prediction_id,
            output = PredictResponse(
                input = result["input"],
                result = result["result"]
            )
        ).model_dump()
    )
