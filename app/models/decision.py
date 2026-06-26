from enum import Enum
from pydantic import BaseModel


class ReviewReason(str, Enum):
    UNKNOWN_VENDOR = "UNKNOWN_VENDOR"
    MISSING_FIELDS = "MISSING_FIELDS"
    DUPLICATE_INVOICE = "DUPLICATE_INVOICE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"

class ProcessingStatus(str, Enum):
    APPROVED = "APPROVED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    DRAFT_CREATED = "DRAFT_CREATED"
    REJECTED = "REJECTED"

class Decision(BaseModel):
    status: ProcessingStatus
    reason: str
    review_reason: ReviewReason | None = None