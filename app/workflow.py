from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.state import InvoiceWorkflowState

from app.nodes.extract_pdf_text import (
    extract_pdf_text_node,
)

from app.nodes.extract_invoice_data import (
    extract_invoice_data_node,
)

from app.nodes.validate_invoice import (
    validate_invoice_node,
)

from app.nodes.validate_supplier import (
    validate_supplier_node,
)

from app.nodes.duplicate_check import (
    duplicate_check_node,
)

from app.nodes.policy_engine import (
    policy_engine_node,
    route_after_policy,
)

from app.nodes.create_odoo_bill import (
    create_odoo_bill_node,
)

from app.nodes.human_review import (
    human_review_node,
)

builder = StateGraph(
    InvoiceWorkflowState
)

builder.add_node(
    "extract_pdf_text",
    extract_pdf_text_node,
)

builder.add_node(
    "extract_invoice_data",
    extract_invoice_data_node,
)

builder.add_node(
    "validate_invoice",
    validate_invoice_node,
)

builder.add_node(
    "validate_supplier",
    validate_supplier_node,
)

builder.add_node(
    "duplicate_check",
    duplicate_check_node,
)

builder.add_node(
    "policy_engine",
    policy_engine_node,
)

builder.add_node(
    "create_odoo_bill",
    create_odoo_bill_node,
)

builder.add_node(
    "human_review",
    human_review_node,
)

builder.add_edge(
    START,
    "extract_pdf_text",
)

builder.add_edge(
    "extract_pdf_text",
    "extract_invoice_data",
)

builder.add_edge(
    "extract_invoice_data",
    "validate_invoice",
)

builder.add_edge(
    "validate_invoice",
    "validate_supplier",
)

builder.add_edge(
    "validate_supplier",
    "duplicate_check",
)

builder.add_edge(
    "duplicate_check",
    "policy_engine",
)

builder.add_conditional_edges(
    "policy_engine",
    route_after_policy,
    {
        "create_odoo_bill":
            "create_odoo_bill",

        "human_review":
            "human_review",
        
        "end": END,
    },
)

builder.add_edge(
    "create_odoo_bill",
    END,
)

builder.add_edge(
    "human_review",
    END,
)

graph = builder.compile()
