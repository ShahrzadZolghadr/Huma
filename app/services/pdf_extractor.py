import fitz

class PDFExtractor:

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        doc = fitz.open(pdf_path)

        pages = []

        for page in doc:
            pages.append(page.get_text())

        return "\n".join(pages)
    
    # if extracted_text_is_not_appropriate:
    # run_ocr()
