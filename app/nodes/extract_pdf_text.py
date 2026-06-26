from app.state import InvoiceWorkflowState
from app.services.pdf_extractor import PDFExtractor
from app.services.audit_service import AuditService

def extract_pdf_text_node(
    state: InvoiceWorkflowState,
) -> InvoiceWorkflowState:

    text = PDFExtractor.extract_text(
        state["pdf_path"]
    )

    audit_events = AuditService.add_event(
        state,
        node_name="extract_pdf_text",
        action="PDF_PARSED",
        metadata={
            "pdf_path": state["pdf_path"],
        },
    )

    return {
        **state,
        "raw_text": text,
        "audit_events": audit_events
    }
