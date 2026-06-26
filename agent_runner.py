import time

from app.workflow import graph
from app.services.email_monitor import EmailMonitor
from app.services.pdf_detector import PdfDetector
from app.services.review_processor import ReviewProcessor

monitor = EmailMonitor()

def run_workflow(pdf):

    return graph.invoke(
        {
                "pdf_path": pdf,
                "raw_text": "",
                "invoice": None,
                "structural_validation": None,
                "supplier_match": None,
                "extraction_confidence": 0,
                "is_duplicate": False,
                "decision": None,
                "odoo_bill_id": None,
                "review_task_id": None,
                "audit_events": [],
                "needs_reprocessing": False
            }
    )

last_review_check = 0

while True:
    email = monitor.get_next_email()

    if email is None:
        print("📥 Waiting for new emails...")

    if email:

        print(f"\nEmail received: {email.subject}")

        pdf = PdfDetector.get_invoice_pdf(email)

        if pdf:

            try:

                print(f"Processing {pdf}")

                result = run_workflow(pdf)

                print(f"Status      : {result['decision'].status}")
                print("\nAudit Trail")

                for event in result["audit_events"]:
                    print(
                        f"{event.timestamp:%H:%M:%S} | "
                        f"{event.node_name:<25} | "
                        f"{event.action}"
                    )

                print("-" * 60)

            except Exception as e:
                print(f"Failed to process {pdf}")
                print(e)

    if time.time() - last_review_check >= 20:

        print("\nChecking review queue...")

        last_review_check = time.time()

        for pdf in ReviewProcessor.get_review_pdfs():

            try:
                print(f"Retrying {pdf}")
                result = run_workflow(pdf)

                print(f"Status      : {result['decision'].status}")
                print("\nAudit Trail")

                for event in result["audit_events"]:
                    print(
                        f"{event.timestamp:%H:%M:%S} | "
                        f"{event.node_name:<25} | "
                        f"{event.action}"
                    )

                print("-" * 60)

            except Exception as e:
                print(f"Failed to process {pdf}")
                print(e)

    time.sleep(5)
