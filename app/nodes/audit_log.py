from datetime import datetime
from pydantic import BaseModel


class AuditEvent(BaseModel):
    timestamp: datetime
    node_name: str
    action: str
    metadata: dict = {}
