from rapidfuzz import fuzz
from rapidfuzz import process
import re, os

from app.models.supplier import (
    SupplierMatchResult, SupplierLLMMatch
)

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL_NAME"),
    temperature=0,
)
supplier_llm = llm.with_structured_output(
    SupplierLLMMatch
)

class SupplierRegistry:

    def __init__(
        self,
        odoo,
    ):
        self.odoo = odoo

    def normalize_vendor_name(
        self,
        vendor_name,
    ):

        if not vendor_name:
            return ""

        vendor_name = str(vendor_name)

        vendor_name = vendor_name.lower()

        vendor_name = re.sub(
            r"[^a-z0-9 ]",
            "",
            vendor_name,
        )

        return " ".join(
            vendor_name.split()
        )
    
    def match_supplier(
        self,
        vendor_name: str,
    ) -> SupplierMatchResult:
        
        SYSTEM_PROMPT = """
        You are an Accounts Payable supplier matching assistant.

        Your task is to determine whether an extracted invoice vendor refers to one of the approved suppliers.

        Rules:

        - Match legal entity variations.
        - Match abbreviations.
        - Match subsidiaries when they clearly belong to the same supplier.
        - Ignore punctuation.
        - Ignore capitalization.
        - Ignore company suffixes like:
            Ltd
            Limited
            LLC
            Inc
            GmbH
            SARL
            BV
            PLC

        Return the approved supplier name exactly as written.

        Confidence:

        100
        Exact legal name

        95-99
        Very obvious variation

        90-94
        Strong confidence

        80-89
        Probably same company

        Below 80
        Treat as different supplier.

        Never invent suppliers.

        If none matches, return:

        matched=False

        confidence=0

        matched_supplier_name=null

        Always explain your reasoning briefly.
        """

        suppliers = (
                    self.odoo.get_all_suppliers()
                )

        if not suppliers:

            return SupplierMatchResult(
                matched=False,
                confidence=0,
                requires_review=True,
                match_type="none",
            )

        normalized_input = (
            self.normalize_vendor_name(
                vendor_name
            )
        )

        for supplier in suppliers:

            normalized_supplier = (
                self.normalize_vendor_name(
                    supplier["name"]
                )
            )

            if (
                normalized_supplier
                == normalized_input
            ):

                return SupplierMatchResult(
                    matched=True,
                    confidence=100,
                    supplier_id=str(
                        supplier["id"]
                    ),
                    supplier_name=supplier["name"],
                    matched_vendor_name=supplier["name"],
                    requires_review=False,
                    match_type="exact",
                )

        supplier_names = [
            supplier["name"]
            for supplier in suppliers
        ]

        response = supplier_llm.invoke(
            [
                ("system", SYSTEM_PROMPT),
                (
                    "human",
                    f"""
        Extracted vendor:

        {vendor_name}

        Approved suppliers:

        {supplier_names}
        """,
                ),
            ]
        )

        if not response.matched:

            return SupplierMatchResult(
                matched=False,
                confidence=0,
                requires_review=True,
                match_type="llm_none",
            )
        matched_supplier = next(
            (
                s
                for s in suppliers
                if s["name"] == response.matched_supplier_name
            ),
            None,
        )

        if matched_supplier is None:

            return SupplierMatchResult(
                matched=False,
                confidence=0,
                requires_review=True,
                match_type="llm_none",
            )
        
        return SupplierMatchResult(

            matched=True,

            confidence=response.confidence,

            supplier_id=str(
                matched_supplier["id"]
            ),

            supplier_name=matched_supplier["name"],

            matched_vendor_name=matched_supplier["name"],

            requires_review=response.confidence < 90,

            match_type="llm",
        )

    def match_supplier_fuzzy_match(
        self,
        vendor_name: str,
    ) -> SupplierMatchResult:

        suppliers = (
            self.odoo.get_all_suppliers()
        )

        if not suppliers:

            return SupplierMatchResult(
                matched=False,
                confidence=0,
                requires_review=True,
                match_type="none",
            )

        normalized_input = (
            self.normalize_vendor_name(
                vendor_name
            )
        )

        # Exact match

        for supplier in suppliers:

            normalized_supplier = (
                self.normalize_vendor_name(
                    supplier["name"]
                )
            )

            if (
                normalized_supplier
                == normalized_input
            ):

                return SupplierMatchResult(
                    matched=True,
                    confidence=100,
                    supplier_id=str(
                        supplier["id"]
                    ),
                    supplier_name=supplier["name"],
                    matched_vendor_name=supplier["name"],
                    requires_review=False,
                    match_type="exact",
                )

        # Fuzzy match

        supplier_names = [
            supplier["name"]
            for supplier in suppliers
        ]

        result = process.extractOne(
            vendor_name,
            supplier_names,
            scorer=fuzz.WRatio,
        )

        if result is None:

            return SupplierMatchResult(
                matched=False,
                confidence=0,
                requires_review=True,
                match_type="none",
            )

        matched_name, score, _ = result

        matched_supplier = next(
            s
            for s in suppliers
            if s["name"] == matched_name
        )

        if score >= 95:

            return SupplierMatchResult(
                matched=True,
                confidence=score,
                supplier_id=str(
                    matched_supplier["id"]
                ),
                supplier_name=matched_name,
                matched_vendor_name=matched_name,
                requires_review=False,
                match_type="fuzzy_high",
            )

        if score >= 85:

            return SupplierMatchResult(
                matched=True,
                confidence=score,
                supplier_id=str(
                    matched_supplier["id"]
                ),
                supplier_name=matched_name,
                matched_vendor_name=matched_name,
                requires_review=True,
                match_type="fuzzy_medium",
            )

        return SupplierMatchResult(
            matched=False,
            confidence=score,
            matched_vendor_name=matched_name,
            requires_review=True,
            match_type="fuzzy_low",
        )
