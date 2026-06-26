from pydantic import BaseModel, Field
from app.models.invoice import InvoiceData


class ExtractionResult(BaseModel):

    invoice: InvoiceData
    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence score"
    )
    extraction_notes: list[str]
    missing_fields: list[str]
    raw_response: str | None = None