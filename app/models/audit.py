from datetime import datetime
from pydantic import BaseModel
from pydantic import Field


class AuditEvent(BaseModel):

    timestamp: datetime
    node_name: str
    action: str
    metadata: dict = Field(
        default_factory=dict
    )
