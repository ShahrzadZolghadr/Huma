from datetime import datetime
from pydantic import BaseModel


class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    received_at: datetime
    attachments: list[str]
