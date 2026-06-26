from app.services.supplier_registry import SupplierRegistry
from app.services.audit_service import AuditService
from app.services.odoo_service import OdooService


odoo = OdooService()
registry = SupplierRegistry(odoo)


def validate_supplier_node(state):

    invoice = state["invoice"]

    if invoice is None:
        return {
            **state,
            "supplier_match": None,
        }

    supplier_match = registry.match_supplier(
        invoice.vendor_name
    )

    audit_events = AuditService.add_event(
        state,
        node_name="validate_supplier",
        action="SUPPLIER_MATCHED",
        metadata={
            "matched": supplier_match.matched,
            "confidence": supplier_match.confidence,
            "supplier_id": supplier_match.supplier_id,
            "supplier_name": supplier_match.supplier_name,
            "match_type": supplier_match.match_type,
        },
    )

    return {
        **state,
        "supplier_match": supplier_match,
        "audit_events": audit_events,
    }
