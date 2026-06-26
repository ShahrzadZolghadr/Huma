from pydantic import BaseModel


class SupplierMatchResult(BaseModel):
    matched: bool
    confidence: float
    supplier_id: str | None = None
    supplier_name: str | None = None
    matched_vendor_name: str | None = None
    supplier_status: str | None = None
    requires_review: bool = False
    match_type: str | None = None


class SupplierLLMMatch(BaseModel):
    matched: bool
    confidence: float
    matched_supplier_name: str | None = None
    explanation: str
