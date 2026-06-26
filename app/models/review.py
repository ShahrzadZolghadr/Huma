from datetime import datetime
from pydantic import BaseModel
from app.models.decision import ReviewReason


# class ReviewTask(BaseModel):
#     invoice_number: str
#     vendor_name: str
#     review_reason: ReviewReason
#     created_at: datetime

class ReviewTask(BaseModel):
    task_id: int
    vendor_name: str
    reason: ReviewReason
