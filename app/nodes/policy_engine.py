from app.models.decision import (
    Decision,
    ProcessingStatus,
    ReviewReason,
)

from app.services.audit_service import AuditService


def policy_engine_node(state):

    validation = state["structural_validation"]
    supplier_match = state["supplier_match"]
    confidence = state["extraction_confidence"]
    is_duplicate = state["is_duplicate"]

    # Unknown supplier

    if (
        supplier_match is None
        or not supplier_match.matched
    ):

        decision = Decision(
            status=ProcessingStatus.REVIEW_REQUIRED,
            reason="Supplier not approved",
            review_reason=ReviewReason.UNKNOWN_VENDOR,
        )

    # Missing fields

    elif not validation.passed:

        decision = Decision(
            status=ProcessingStatus.DRAFT_CREATED,
            reason="Missing required fields",
            review_reason=ReviewReason.MISSING_FIELDS,
        )

    # Duplicate

    elif is_duplicate:

        decision = Decision(
            status=ProcessingStatus.REJECTED,
            reason="Duplicate invoice",
            review_reason=ReviewReason.DUPLICATE_INVOICE,
        )

    # Low confidence

    elif confidence < 0.80:

        decision = Decision(
            status=ProcessingStatus.DRAFT_CREATED,
            reason="Low extraction confidence",
            review_reason=ReviewReason.LOW_CONFIDENCE,
        )

    # Approved

    else:

        decision = Decision(
            status=ProcessingStatus.APPROVED,
            reason="Ready for Odoo posting",
        )

    audit_events = AuditService.add_event(
        state,
        node_name="policy_engine",
        action="DECISION_MADE",
        metadata={
            "status": decision.status.value,
            "reason": decision.reason,
        },
    )

    return {
        **state,
        "decision": decision,
        "audit_events": audit_events,
    }


def route_after_policy(state):

    status = state["decision"].status

    if status in [
        ProcessingStatus.APPROVED,
        ProcessingStatus.DRAFT_CREATED,
    ]:
        return "create_odoo_bill"

    if status == ProcessingStatus.REVIEW_REQUIRED:
        return "human_review"

    return "end"
