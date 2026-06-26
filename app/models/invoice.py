from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class InvoiceLineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    amount: float
    # vat_id: Optional[int] = Field(description="only if the VAT id is in the header the vat percent may be in invoice line, id for 20 percent is 5")

class InvoiceData(BaseModel):
    vendor_name: str = Field(description='The vendor Name')
    invoice_number: str
    invoice_date: date
    due_date: Optional[date] = Field(description="note that fill this field if and only if the due date is specifically mentioned in the invoice")
    payment_terms_id: Optional[int] = Field(description="the payment terms id, for example Net 30 id is 9, Net 14 id is 12, Charged to card is 13. if the payment exists in text but not in informed ids, default is 9. if you see the payment term always make an id for it.")
    total_amount: float
    currency_id: int = Field(description='The currency id. USD is 1, EUR is 126 and GBP is 144')
    line_items: list[InvoiceLineItem]
