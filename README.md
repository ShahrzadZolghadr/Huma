# Huma – Agentic Invoice Processing System

An AI-powered Accounts Payable automation system built with **LangGraph**, **OpenAI**, and **Odoo**.

The system continuously monitors incoming emails, identifies invoice PDFs, extracts structured invoice information using an LLM, validates the extracted data, detects duplicates, verifies suppliers, and automatically creates Vendor Bills inside Odoo whenever possible.

Invoices requiring human intervention are automatically routed into a review workflow while preserving a complete audit trail.

---

# Features

* Agentic workflow built with LangGraph
* Automatic email inbox monitoring
* Invoice PDF detection
* PDF text extraction
* LLM-based structured invoice extraction
* Invoice validation
* LLM-powered supplier matching
* Duplicate detection using Odoo
* Automatic Vendor Bill creation
* Draft bill creation for incomplete invoices
* Human Review workflow for new suppliers
* Automatic Project Task creation inside Odoo
* PDF attachment to Vendor Bills and Review Tasks
* Complete workflow audit logging
* LangSmith tracing support
* Dockerized deployment

---

# Workflow

```
Email Inbox
    │
    ▼
Email Monitor
    │
    ▼
PDF Detection
    │
    ▼
PDF Text Extraction
    │
    ▼
Invoice Extraction Agent
(OpenAI Structured Output)
    │
    ▼
Invoice Validation
    │
    ▼
Supplier Matching Agent
(LLM + Odoo Suppliers)
    │
    ▼
Duplicate Detection
(Odoo)
    │
    ▼
Decision Engine
    │
    ├──────────────┐
    ▼              ▼

Auto Processing    Human Review

    │              │

Create Vendor Bill Create Review Task

Attach PDF         Attach PDF

Audit Log          Audit Log

Chatter Message    Chatter Message

Post/Draft Bill

    │              │

    ▼              ▼

Completed      Waiting for Review
```

---

# LangGraph Workflow

```
START

↓

Extract PDF Text

↓

Extract Invoice Data

↓

Validate Invoice

↓

Validate Supplier

↓

Duplicate Check

↓

Policy Engine

      │

 ┌────┴────┐

 ▼         ▼

Validate Bill   Human Review
      |

 ┌────┴────┐

 ▼         ▼
Draft Bill      Create Bill

      │

      ▼

END
```

---

# Decision Engine

The workflow automatically classifies every invoice into one of the following paths.

| Condition                                                              | Result                      |
| ---------------------------------------------------------------------- | --------------------------- |
| Approved supplier + complete invoice + high confidence + not duplicate | Create and Post Vendor Bill |
| Missing required fields                                                | Create Draft Vendor Bill    |
| Low extraction confidence                                              | Create Draft Vendor Bill    |
| Unknown supplier                                                       | Human Review Task           |
| Duplicate invoice                                                      | Processing stopped          |

---

# Human Review Workflow

Unknown suppliers are not automatically created.

Instead, the workflow:

* Creates an Odoo Project Task
* Attaches the original invoice PDF
* Records the review reason
* Waits for a human to approve or create the supplier
* Automatically retries processing after approval

---

# Audit Trail

Every workflow execution records audit events including:

* PDF_PARSED
* INVOICE_EXTRACTED
* INVOICE_VALIDATED
* SUPPLIER_MATCHED
* DUPLICATE_CHECKED
* DECISION_MADE
* ODOO_CREATED
* REVIEW_TASK_CREATED

---

# Running

Run in background

```bash
docker compose up -d --build
```

Or run locally

```bash
python agent_runner.py
```

---
