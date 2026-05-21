from pydantic import BaseModel
from enum import Enum
from typing import Literal

class HTMLPayload(BaseModel):
    url: str
    html: str

class LatencyEntry(BaseModel):
    type: Literal["pre", "post", "spoiler"]
    location: Literal["ui", "backend"]
    site: str
    time: int

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
