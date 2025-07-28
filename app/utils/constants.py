from dotenv import load_dotenv
import os

load_dotenv()

STREAM_KEY = os.environ.get("STREAM_KEY", "prediction_stream")
RESULT_PREFIX = os.environ.get("RESULT_PREFIX", "result:")