from datetime import datetime
from app.models.audit import AuditEvent


class AuditService:

    @staticmethod
    def add_event(
        state,
        node_name: str,
        action: str,
        metadata: dict | None = None,
    ):

        events = state.get(
            "audit_events",
            [],
        )

        events.append(
            AuditEvent(
                timestamp=datetime.utcnow(),
                node_name=node_name,
                action=action,
                metadata=metadata or {},
            )
        )

        return events
