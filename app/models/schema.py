from pydantic import BaseModel

class PredictRequest(BaseModel):
    input: str

class PredictResponse(BaseModel):
    input: str
    result: str

class PredictResponseAsync(BaseModel):
    prediction_id: str
    output: PredictResponse
    
class PredictResultAsync(BaseModel):
    prediction_id: str
    message: str
