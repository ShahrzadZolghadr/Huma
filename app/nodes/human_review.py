from app.models.review import ReviewTask
from app.services.audit_service import AuditService
from app.services.odoo_service import OdooService
from app.services.file_manager import FileManager


odoo = OdooService()

def human_review_node(state):

    invoice = state["invoice"]

    task_id = odoo.create_supplier_review_task(
        vendor_name=invoice.vendor_name,
        reason=state["decision"].reason,
    )

    odoo.attach_pdf_to_task(
        task_id=task_id,
        pdf_path=state["pdf_path"],
    )

    review_task = ReviewTask(
        task_id=task_id,
        vendor_name=invoice.vendor_name,
        reason=state["decision"].review_reason,
    )


    audit_events = AuditService.add_event(
        state,
        node_name="human_review",
        action="REVIEW_TASK_CREATED",
        metadata={
            "task_id": task_id,
        },
    )

    FileManager.move_to_review(
        state["pdf_path"]
    )

    return {
        **state,
        "review_task": review_task,
        "audit_events": audit_events,
    }
