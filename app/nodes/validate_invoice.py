from app.models.validation import (
    ValidationResult,
    ValidationIssue,
)
from app.services.audit_service import AuditService

def validate_invoice_node(state):

    invoice = state["invoice"]

    issues = []

    if not invoice.vendor_name:
        issues.append(
            ValidationIssue(
                code="MISSING_VENDOR",
                message="Vendor name missing",
            )
        )

    if not invoice.invoice_number:
        issues.append(
            ValidationIssue(
                code="MISSING_INVOICE_NUMBER",
                message="Invoice number missing",
            )
        )

    if not invoice.invoice_date:
        issues.append(
            ValidationIssue(
                code="MISSING_INVOICE_DATE",
                message="Invoice date missing",
            )
        )

    if invoice.total_amount is None:
        issues.append(
            ValidationIssue(
                code="MISSING_TOTAL_AMOUNT",
                message="Total amount missing",
            )
        )

    if (
        not invoice.due_date
        and not invoice.payment_terms_id
    ):
        issues.append(
            ValidationIssue(
                code="MISSING_PAYMENT_INFO",
                message="Due date or payment terms required",
            )
        )

    if not invoice.line_items:
        issues.append(
            ValidationIssue(
                code="MISSING_LINE_ITEMS",
                message="Line items missing",
            )
        )

    validation = ValidationResult(
        passed=len(issues) == 0,
        issues=issues,
    )

    audit_events = AuditService.add_event(
        state,
        node_name="validate_invoice",
        action="INVOICE_VALIDATED",
        metadata={
            "passed": validation.passed,
            "issue_count": len(validation.issues),
        },
    )

    return {
        **state,
        "structural_validation": validation,
        "audit_events": audit_events

    }
