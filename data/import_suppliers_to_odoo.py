import pandas as pd

from app.services.odoo_service import (
    OdooService,
)

odoo = OdooService()

df = pd.read_csv(
    "data/approvedSuppliers.csv",
    skiprows=3,
)

for _, row in df.iterrows():

    existing = odoo.get_supplier(
        row["Vendor (Partner) Name"]
    )

    if existing:
        continue

    odoo.create_supplier(
        supplier_name=row["Vendor (Partner) Name"],
        vat_id=row["VAT / Tax ID"],
    )

    print(
        f"Created {row['Vendor (Partner) Name']}"
    )
