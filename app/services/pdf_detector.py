from pathlib import Path


class PdfDetector:

    @staticmethod
    def get_invoice_pdf(email):

        for attachment in email.attachments:

            if attachment.lower().endswith(".pdf"):

                return str(
                    Path("data/invoices") / attachment
                )

        return None