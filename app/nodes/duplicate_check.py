from app.services.odoo_duplicate_detector import OdooDuplicateDetector
from app.services.audit_service import AuditService


detector = OdooDuplicateDetector()

def duplicate_check_node(state):

    supplier_match = state["supplier_match"]

    if supplier_match.matched == False:
        return {
            **state,
            "is_duplicate": False,
        }

    invoice = state["invoice"]

    is_duplicate = detector.is_duplicate(
        supplier_name=supplier_match.supplier_name,
        invoice_number=invoice.invoice_number,
    )
    audit_events = AuditService.add_event(
        state,
        node_name="duplicate_check",
        action="DUPLICATE_CHECKED",
        metadata={
            "is_duplicate": is_duplicate,
        },
    )
    return {
        **state,
        "is_duplicate": is_duplicate,
        "audit_events": audit_events
    }
