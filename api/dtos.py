from pydantic import BaseModel
from enum import Enum

class HTMLPayload(BaseModel):
    url: str
    html: str

class Article(BaseModel):
    title: str
    content: str

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    explanation: str
    spoiler: str

class DetectionResponse(BaseModel):
    predictions: dict

class ConfName(Enum):
    GOOGLE = 'google'
    THESUN = 'thesun'
    UNKNOWN = 'unknown'
