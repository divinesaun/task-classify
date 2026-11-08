from typing import Literal

from pydantic import BaseModel, Field

SignId = Literal[
    "reduced_appetite",
    "weakness",
    "swelling",
    "rapid_breathing",
    "cloudy_eye",
    "froth_nose_mouth",
    "red_urine",
    "unable_to_stand",
    "ticks",
]

Value = Literal["yes", "no", "not_sure"]


class Finding(BaseModel):
    sign_id: SignId
    value: Value
    quote: str


class Extraction(BaseModel):
    findings: list[Finding]


class ExtractRequest(BaseModel):
    message: str = Field(min_length=1)


class ExtractResponse(BaseModel):
    findings: list[Finding]
    escalate: bool
    reason: str
