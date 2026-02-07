from typing import Literal
from pydantic import BaseModel


class TextToTextRequest(BaseModel):
    prompt: str
    model: Literal["model_1", "model_2"] = None


class TextToTextResponse(BaseModel):
    result: str
