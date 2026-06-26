from app.services.odoo_service import OdooService


class OdooDuplicateDetector:

    def __init__(self):
        self.odoo = OdooService()

    def is_duplicate(
        self,
        supplier_name: str,
        invoice_number: str,
    ) -> bool:

        bills = self.odoo.search_vendor_bills(
            supplier_name=supplier_name,
            invoice_number=invoice_number,
        )

        return len(bills) > 0
