from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.models.invoice import InvoiceData
from app.models.extraction import ExtractionResult
import os

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL_NAME"),
    temperature=0,
)

structured_llm = llm.with_structured_output(
    InvoiceData
)

SYSTEM_PROMPT = """
You are a very intelligent and precise invoice extraction system.

Extract only information explicitly present in the invoice.

Requirements:

- Never infer values. fields are so sensitive to us.
- Never invent values.
- Preserve invoice numbers exactly.
- Preserve currencies exactly. pay attention to the signs of the currency and extract it accurately. if you are not confident dont add it because of problems will make financial issues.
- Return null when information is unavailable.
- Extract line items individually.
- Use ISO date format (YYYY-MM-DD) whenever possible.
- Keep monetary values numeric.
- Do not perform calculations.
"""

class InvoiceExtractor:

    @staticmethod
    def extract(
        invoice_text: str,
    ) -> ExtractionResult:

        try:

            invoice = structured_llm.invoke(
                [
                    ("system", SYSTEM_PROMPT),
                    ("human", invoice_text),
                ]
            )

            required_fields = {
                "vendor_name": invoice.vendor_name,
                "invoice_number": invoice.invoice_number,
                "invoice_date": invoice.invoice_date,
                "due_date": invoice.due_date,
                "payment_terms_id": invoice.payment_terms_id,
                "currency_id": invoice.currency_id,
                "total_amount": invoice.total_amount,
                "line_items": invoice.line_items,
            }

            missing_fields = []

            for field_name, value in required_fields.items():

                if value is None:
                    missing_fields.append(field_name)

                elif isinstance(value, list) and len(value) == 0:
                    missing_fields.append(field_name)

            confidence = (
                len(required_fields)
                - len(missing_fields)
            ) / len(required_fields)

            return ExtractionResult(
                invoice=invoice,
                confidence=confidence,
                extraction_notes=[],
                missing_fields=missing_fields,
            )

        except Exception as e:

            raise RuntimeError(
                f"Invoice extraction failed: {str(e)}"
            )
