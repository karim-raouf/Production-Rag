from pydantic import BaseModel

class InputGuardResponse(BaseModel):
    classification: bool


class OutputGuardResponse(BaseModel):
    classification: bool
