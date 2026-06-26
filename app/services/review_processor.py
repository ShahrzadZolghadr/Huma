import glob

class ReviewProcessor:

    @staticmethod
    def get_review_pdfs():

        return glob.glob(
            "data/emails/review/*.pdf"
        )
