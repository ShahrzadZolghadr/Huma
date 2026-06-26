from typing import TypedDict

from app.models.audit import AuditEvent
from app.models.decision import Decision
from app.models.invoice import InvoiceData
from app.models.validation import ValidationResult
from app.models.supplier import SupplierMatchResult
from app.models.review import ReviewTask

class InvoiceWorkflowState(TypedDict):

    pdf_path: str
    source_filename: str
    raw_text: str
    invoice: InvoiceData | None
    structural_validation: ValidationResult | None
    supplier_match: SupplierMatchResult | None
    extraction_confidence: float
    is_duplicate: bool
    decision: Decision | None
    odoo_bill_id: str | None
    audit_events: list[AuditEvent]
    review_task: ReviewTask | None
    review_task_id: int | None
    attachment_id: int | None
    needs_reprocessing: bool | None