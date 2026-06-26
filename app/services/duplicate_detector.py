import hashlib
import sqlite3
from pathlib import Path

class DuplicateDetector:

    def __init__(
        self,
        db_path: str = "data/invoices.db",
    ):
        self.db_path = db_path

        Path(db_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_db()

    def _initialize_db(self):

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id TEXT NOT NULL,
                invoice_number TEXT NOT NULL,
                invoice_hash TEXT NOT NULL UNIQUE,
                odoo_bill_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()
        conn.close()

    def generate_hash(
        self,
        supplier_id: str,
        invoice_number: str,
    ) -> str:

        value = (
            f"{supplier_id}:{invoice_number}"
        )

        return hashlib.sha256(
            value.encode()
        ).hexdigest()
    
    def is_duplicate(
        self,
        supplier_id: str,
        invoice_number: str,
    ) -> bool:
        invoice_hash = self.generate_hash(
            supplier_id,
                invoice_number,
            )

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM processed_invoices
            WHERE invoice_hash = ?
            """,
            (invoice_hash,),
        )

        result = cursor.fetchone()

        conn.close()

        return result is not None
    
    def save_processed_invoice(
        self,
        supplier_id: str,
        invoice_number: str,
        odoo_bill_id: str,
    ):
        invoice_hash = self.generate_hash(
            supplier_id,
            invoice_number,
            )

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO processed_invoices (
                    supplier_id,
                    invoice_number,
                    invoice_hash,
                    odoo_bill_id
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    supplier_id,
                    invoice_number,
                    invoice_hash,
                    odoo_bill_id,
                ),
            )

            conn.commit()

        except sqlite3.IntegrityError:
            pass

        finally:
            conn.close()
 