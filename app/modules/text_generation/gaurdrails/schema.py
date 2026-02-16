from pydantic import BaseModel


class TopicalGuardResponse(BaseModel):
    classification: bool



