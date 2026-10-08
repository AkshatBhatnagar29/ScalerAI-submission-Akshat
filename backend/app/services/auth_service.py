from typing import Optional

from ..core.config import MOCK_PASSWORD, MOCK_USERNAME
from ..core.security import generate_session_id


class AuthService:
    def __init__(self) -> None:
        self._sessions: dict[str, str] = {}

    def validate_credentials(self, username: str, password: str) -> bool:
        return secretsafe_compare(username, MOCK_USERNAME) and secretsafe_compare(password, MOCK_PASSWORD)

    def create_session(self, username: str) -> str:
        session_id = generate_session_id()
        self._sessions[session_id] = username
        return session_id

    def get_username(self, session_id: Optional[str]) -> Optional[str]:
        if not session_id:
            return None
        return self._sessions.get(session_id)

    def delete_session(self, session_id: Optional[str]) -> None:
        if session_id:
            self._sessions.pop(session_id, None)


def secretsafe_compare(left: str, right: str) -> bool:
    import hmac

    return hmac.compare_digest(left, right)


auth_service = AuthService()
