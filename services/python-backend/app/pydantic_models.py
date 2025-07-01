from pydantic import BaseModel
from typing import List

# Pydantic модели для ответа
class ClassificationResult(BaseModel):
    class_name: str
    #confidence: float
    image_name: str
    probabilities: List[float]

class ClassificationResponse(BaseModel):
    results: List[ClassificationResult]