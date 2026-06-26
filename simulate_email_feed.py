import json
import time
from pathlib import Path
from datetime import datetime, timedelta

SOURCE = Path("data/invoices/Sample Invoices")
INBOX = Path("data/emails/inbox")

pdfs = sorted(SOURCE.glob("*.pdf"))

base_time = datetime.now()

for i, pdf in enumerate(pdfs, start=1):

    sender = pdf.stem.split("_")[1].lower().replace(" ", "")

    email = {
        "id": f"email{i:03}",
        "sender": f"billing@{sender}.com",
        "subject": f"Invoice {pdf.stem}",
        "body": "Please find attached invoice.",
        "received_at": (
            base_time + timedelta(seconds=i * 10)
        ).isoformat(timespec="seconds"),
        "attachments": [
            f"Sample Invoices/{pdf.name}"
        ],
    }

    with open(
        INBOX / f"email{i:03}.json",
        "w",
    ) as f:

        json.dump(email, f, indent=4)

    print(f"Delivered {pdf.name}")

    time.sleep(10)