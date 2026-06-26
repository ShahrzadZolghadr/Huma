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

# High-level Architecture

```text
                           Incoming Emails
                                  │
                                  ▼
                           Email Monitoring
                                  │
                                  ▼
                           PDF Identification
                                  │
                                  ▼
                        LangGraph Workflow Engine
                                  │
                                  ▼
                     PDF Text Extraction (PyMuPDF)
               (Future: OpenAI OCR / Vision Models)
                                  │
                                  ▼
                     Invoice Extraction Agent (LLM)
                    (OpenAI Structured Output)
                                  │
                                  ▼
                         Validation Layer
                ┌────────────────────────────────┐
                │ • Invoice Schema Validation    │
                │ • Supplier Matching (LLM)      │
                │ • Duplicate Detection (Odoo)   │
                └────────────────────────────────┘
                                  │
                                  ▼
                           Policy Engine
                                  │
          ┌───────────────────────┼────────────────────────┐
          │                       │                        │
          ▼                       ▼                        ▼
   1. Auto Processing         2. Draft Processing        3. Duplicate Invoice
          │                       │                        │
          │                       │                        ▼
          │                       │                 Ignore Processing
          │                       │
          ▼                       ▼
    Create Vendor Bill     Create Draft Bill
    Attach PDF             Attach PDF
    Audit Log              Audit Log
    Post Bill              Leave as Draft
          │                       │
          └───────────────┬───────┘
                          │
                          ▼
                    Processing Complete


                    4. Unknown Supplier
                           │
                           ▼
                 Create Odoo Review Task
                 Attach Original PDF
                 Audit Log
                           │
                           ▼
              Human Creates / Approves Supplier
                           │
                           ▼
              Review Folder Retry Processor
                    (Background Worker)
                           │
                           └──────────────► Re-enter LangGraph Workflow
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

Run this two commands to run postgres and odoo containers

```bash
docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres --name db postgres:15

docker run -p 8069:8069 --name odoo --link db:db -t odoo
```

Then run following command to create virtual environment and activate it

```bash
python3.12 -m venv venv
source venv/bin/activate
python agent_runner.py
```

Open new terminal and run these command to populate data

```bash
python3.12 -m venv venv
source venv/bin/activate
python simulate_email_feed.py
```

---
