from pathlib import Path
from app.models.email import Email


class EmailMonitor:

    def __init__(
        self,
        inbox_path="data/emails/inbox",
    ):
        self.inbox = Path(inbox_path)

    def get_next_email(self):

        files = sorted(
            self.inbox.glob("*.json")
        )

        if not files:
            return None

        file = files[0]

        email = Email.model_validate_json(
            file.read_text()
        )

        processed = self.inbox.parent / "processed"

        processed.mkdir(
            exist_ok=True,
        )

        file.rename(
            processed / file.name
        )
        return email
