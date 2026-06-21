import secrets
import uuid
from datetime import UTC, datetime

instance_id: uuid.UUID = uuid.uuid4()
background_color: str = f"#{secrets.token_hex(nbytes=3)}"
started_at: datetime = datetime.now(UTC).astimezone()
