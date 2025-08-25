# app/utils/schemas.py
from pydantic import BaseModel, Field

class ProcessParams(BaseModel):
    pitch_semitones: float = Field(0.0, ge=-24, le=24)  # 반음 단위
    time_stretch: float = Field(1.0, gt=0.25, lt=4.0)   # 배속(0.25~4.0)