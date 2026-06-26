from app.services.odoo_service import OdooService
from app.services.audit_service import AuditService
from app.services.duplicate_detector import DuplicateDetector
from app.models.decision import ProcessingStatus
from app.services.file_manager import FileManager
import os


odoo = OdooService()
detector = DuplicateDetector()

def create_odoo_bill_node(state):
    invoice = state["invoice"]
    supplier_match = state["supplier_match"]

    if supplier_match.matched == False:
        raise ValueError(
            f"Supplier not found in Odoo"
        )
    
    supplier = odoo.get_supplier(
        supplier_match.supplier_name
    )

    try:
        bill_id = odoo.create_vendor_bill(
            partner_id=supplier["id"],
            invoice=invoice,
        )
    except Exception as e:
        return {
            **state,
            "decision": state["decision"].status(
                status=ProcessingStatus.REVIEW_REQUIRED,
                reason=f"Odoo error: {e}",
            ),
        }

    attachment_id = odoo.attach_pdf(
        bill_id=bill_id,
        pdf_path=state["pdf_path"],
    )

    should_post = (
        state["decision"].status
        == ProcessingStatus.APPROVED
    )

    comment = f"""
        Created automatically by Huma Invoice Agent

        Status:
        {"POSTED" if should_post else "DRAFT - REVIEW REQUIRED"}

        Extraction confidence:
        {state["extraction_confidence"]:.2f}

        Vendor match confidence:
        {supplier_match.confidence:.0f}%

        Decision:
        {state["decision"].reason}

        Source PDF:
        {os.path.basename(state["pdf_path"])}

        Workflow:
        PDF_PARSED
        INVOICE_EXTRACTED
        INVOICE_VALIDATED
        SUPPLIER_MATCHED
        DUPLICATE_CHECKED
        DECISION_MADE
        ODOO_CREATED
        """
    odoo.add_chatter_comment(
        bill_id=bill_id,
        message=comment,
    )

    if should_post:
        odoo.post_bill(bill_id)

    detector.save_processed_invoice(
        supplier_id=supplier_match.supplier_id,
        invoice_number=invoice.invoice_number,
        odoo_bill_id=str(bill_id),
    )

    audit_events = AuditService.add_event(
        state,
        node_name="create_odoo_bill",
        action="ODOO_CREATED",
        metadata={
            "bill_id": bill_id,
            "attachment_id": attachment_id,
            "posted": should_post,
            "status": state["decision"].status.value,
        },
    )

    FileManager.move_to_processed(
        state["pdf_path"]
    )

    return {
        **state,
        "odoo_bill_id": str(bill_id),
        "audit_events": audit_events,
    }
