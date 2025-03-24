from pydantic import BaseModel
from dataclasses import dataclass

@dataclass
class LLMQuery():
    question: str

class APILLMQuery(BaseModel):
    question: str

class PostTest(BaseModel):
    user: str
    age: int

class AlertAnnotations(BaseModel):
    summary: str

class Alert(BaseModel):
    status: str
    annotations: AlertAnnotations
    startsAt: str
    endsAt: str
    dashboardURL: str
    panelURL: str

class GrafanaMessage(BaseModel):
    alerts: list[Alert]
    commonAnnotations: dict
    title: str
    status: str
    state: str
    message: str