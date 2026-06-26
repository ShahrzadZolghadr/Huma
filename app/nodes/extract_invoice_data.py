from app.state import InvoiceWorkflowState
from app.services.invoice_extractor import InvoiceExtractor
from app.services.audit_service import AuditService

def extract_invoice_data_node(
    state: InvoiceWorkflowState,
) -> InvoiceWorkflowState:

    extraction_result = (
        InvoiceExtractor.extract(
            state["raw_text"]
        )
    )

    audit_events = AuditService.add_event(
        state,
        node_name="extract_invoice_data",
        action="INVOICE_EXTRACTED",
        metadata={
            "confidence": extraction_result.confidence,
        },
    )

    return {
        **state,
        "invoice": extraction_result.invoice,
        "extraction_confidence":
            extraction_result.confidence,
        "audit_events": audit_events
    }
