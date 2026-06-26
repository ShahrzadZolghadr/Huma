import os
import base64
import xmlrpc.client
from dotenv import load_dotenv

load_dotenv()

class OdooService:

    def __init__(self):

        self.url = os.getenv("ODOO_URL")
        self.db = os.getenv("ODOO_DB")
        self.username = os.getenv("ODOO_USERNAME")
        self.password = os.getenv("ODOO_PASSWORD")

        common = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/common"
        )

        self.uid = common.authenticate(
            self.db,
            self.username,
            self.password,
            {},
        )

        self.models = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/object"
        )

    # SUPPLIERS

    def get_supplier(
        self,
        supplier_name: str,
    ):

        suppliers = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "search_read",
            [
                [
                    ["supplier_rank", ">", 0],
                    ["name", "ilike", supplier_name],
                ]
            ],
            {
                "fields": [
                    "id",
                    "name",
                    "vat",
                    "supplier_rank",
                ],
                "limit": 1,
            },
        )

        if not suppliers:
            return None

        return suppliers[0]

    def find_supplier_by_vat(
        self,
        vat_id: str,
    ):

        suppliers = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "search_read",
            [
                [
                    ["vat", "=", vat_id],
                ]
            ],
            {
                "fields": [
                    "id",
                    "name",
                    "vat",
                ],
                "limit": 1,
            },
        )

        if not suppliers:
            return None

        return suppliers[0]

    def get_all_suppliers(self):

        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "search_read",
            [
                [
                    ["supplier_rank", ">", 0]
                ]
            ],
            {
                "fields": [
                    "id",
                    "name",
                    "vat",
                    "supplier_rank",
                ]
            },
        )
    
    def create_supplier(
        self,
        supplier_name: str,
        vat_id: str | None = None,
    ):

        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "create",
            [
                {
                    "name": supplier_name,
                    "supplier_rank": 1,
                    "vat": vat_id or False,
                }
            ],
        )

    # DUPLICATE DETECTION

    def search_vendor_bills(
        self,
        supplier_name: str,
        invoice_number: str,
    ):

        supplier = self.get_supplier(
            supplier_name
        )

        if supplier is None:
            return []

        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "account.move",
            "search_read",
            [
                [
                    ["move_type", "=", "in_invoice"],
                    ["partner_id", "=", supplier["id"]],
                    ["ref", "=", invoice_number],
                ]
            ],
            {
                "fields": [
                    "id",
                    "name",
                    "state",
                    "ref",
                ]
            },
        )

    def bill_exists(
        self,
        supplier_name: str,
        invoice_number: str,
    ) -> bool:

        bills = self.search_vendor_bills(
            supplier_name=supplier_name,
            invoice_number=invoice_number,
        )

        return len(bills) > 0

    # VENDOR BILL CREATION

    def create_vendor_bill(
        self,
        partner_id: int,
        invoice,
    ) -> int:

        invoice_lines = []

        for item in invoice.line_items:

            invoice_lines.append(
                (
                    0,
                    0,
                    {
                        "name": item.description,
                        "quantity": item.quantity,
                        "price_unit": item.unit_price,
                        # "tax_ids": (
                        #     [(6, 0, [item.vat_id])]
                        #     if item.vat_id
                        #     else False
                        # )
                    },
                )
            )

        bill_id = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "account.move",
            "create",
            [
                {
                    "move_type": "in_invoice",
                    "partner_id": partner_id,
                    "invoice_date": str(
                        invoice.invoice_date
                    ),
                    "invoice_date_due": (
                        str(invoice.due_date)
                        if invoice.due_date
                        else False
                    ),
                    "currency_id": invoice.currency_id,
                    "invoice_payment_term_id": (
                        int(invoice.payment_terms_id)
                        if invoice.payment_terms_id and not invoice.due_date
                        else False
                    ),
                    "ref": invoice.invoice_number,
                    "invoice_line_ids": invoice_lines,
                }
            ],
        )

        return bill_id

    def post_bill(
        self,
        bill_id: int,
    ):

        self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "account.move",
            "action_post",
            [[bill_id]],
        )

    # AUDIT LOGGING

    def add_chatter_comment(
        self,
        bill_id: int,
        message: str,
    ):

        self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "mail.message",
            "create",
            [
                {
                    "model": "account.move",
                    "res_id": bill_id,
                    "body": message,
                    "message_type": "comment",
                }
            ],
        )

    # ATTACHMENTS

    def attach_pdf(
        self,
        bill_id: int,
        pdf_path: str,
    ):

        with open(
            pdf_path,
            "rb",
        ) as file:

            encoded = (
                base64.b64encode(
                    file.read()
                ).decode()
            )

        attachment_id = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "ir.attachment",
            "create",
            [
                {
                    "name": os.path.basename(
                        pdf_path
                    ),
                    "datas": encoded,
                    "res_model": "account.move",
                    "res_id": bill_id,
                }
            ],
        )

        return attachment_id


    def attach_pdf_to_task(
        self,
        task_id: int,
        pdf_path: str,
    ):
        with open(
            pdf_path,
            "rb",
        ) as file:

            encoded = (
                base64.b64encode(
                    file.read()
                ).decode()
            )

        attachment_id = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "ir.attachment",
            "create",
            [
                {
                    "name": os.path.basename(
                        pdf_path
                    ),
                    "datas": encoded,
                    "res_model": "project.task",
                    "res_id": task_id,
                }
            ],
        )

        return attachment_id

    # HITL / SUPPLIER REVIEW

    def create_supplier_review_task(
        self,
        vendor_name: str,
        reason: str,
    ):

        task_id = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "project.task",
            "create",
            [
                {
                    "project_id": int(os.getenv("REVIEW_PROJECT_ID")),
                    "name":
                        f"Supplier Evaluation - {vendor_name}",
                    "description": reason,
                }
            ],
        )

        return task_id
