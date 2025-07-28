from app.services.predictor import mock_model_predict
from app.utils.redis_client import redis_stream
from app.utils.constants import STREAM_KEY, RESULT_PREFIX

print("Consumer is now listening for new messages...")

# Set the last read message ID to "0" to read from the beginning of the stream
last_id = "0"

# Infinite loop to keep listening for new prediction requests on the Redis stream
while True:
    # Read a new message from the Redis stream (blocking call until a message is received)
    messages = redis_stream.xread({STREAM_KEY: last_id}, block=0, count=1)

    # Process each received message
    for stream, entries in messages:
        for message_id, message_data in entries:
            # Update last_id to avoid re-processing the same message
            last_id = message_id

            # Extract prediction ID and input text from the message data
            prediction_id = message_data.get("prediction_id")
            input_text = message_data.get("input")

            # Skip processing if the message format is invalid
            if not prediction_id or not input_text:
                print(f"Invalid message format: {message_data}")
                continue

            print(f"Processing: {prediction_id}")

            # Mark the prediction as "processing" in Redis so it can be queried immediately
            redis_stream.hset(RESULT_PREFIX + prediction_id, mapping = {
                "status": "processing",
                "input": input_text,
                "result": ""
            })

            # Run the prediction model
            try:
                result = mock_model_predict(input_text)
            except Exception as e:
                # If an error occurs, store the error status and message in Redis
                redis_stream.hset(RESULT_PREFIX + prediction_id, mapping = {
                    "status": "error",
                    "input": input_text,
                    "result": str(e)
                })
                print(f"Error processing prediction {prediction_id}: {e}")
                continue

            # Once prediction is successful, store the final result in Redis
            redis_stream.hset(RESULT_PREFIX + prediction_id, mapping={
                "status": "done",
                "input": result["input"],
                "result": result["result"]
            })

            print(f"Processed: {prediction_id}")
