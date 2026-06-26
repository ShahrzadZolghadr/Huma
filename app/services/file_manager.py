import shutil
import os


class FileManager:

    @staticmethod
    def move_to_processed(pdf_path):

        destination = os.path.join(
            "data",
            "emails",
            "processed",
            os.path.basename(pdf_path),
        )

        shutil.move(pdf_path, destination)

        return destination


    @staticmethod
    def move_to_review(pdf_path):

        destination = os.path.join(
            "data",
            "emails",
            "review",
            os.path.basename(pdf_path),
        )

        shutil.move(pdf_path, destination)

        return destination
