from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import Dict, Optional

from PIL import Image

from app.models.schemas import DeviceType, RecognitionResult, RecognitionStatus
from app.services.device_manager import DeviceManager


class FaceVerificationService:
    """Coordinates face verification and short-lived action authorization."""

    PROTECTED_LOCK_ACTIONS = {"unlock", "open"}

    def __init__(
        self,
        recognition_service,
        device_manager: DeviceManager,
        verification_ttl_seconds: int = 60,
        min_confidence: float = 0.8,
        authorized_person_ids: Optional[list[str]] = None,
    ):
        self.recognition_service = recognition_service
        self.device_manager = device_manager
        self.verification_ttl_seconds = verification_ttl_seconds
        self.min_confidence = min_confidence
        self.authorized_person_ids = set(authorized_person_ids or [])
        self.active_tokens: Dict[str, dict] = {}

    def verify_face(
        self,
        image: Image.Image,
        device_id: Optional[str] = None,
        action: Optional[str] = None,
    ) -> dict:
        """Verify face image and issue a short-lived token for protected actions."""
        recognition_result = self.recognition_service.recognize(image)
        normalized_action = action.lower() if action else None
        is_authorized_person = self._is_authorized_person(recognition_result)
        is_confident = recognition_result.confidence >= self.min_confidence
        verified = (
            recognition_result.status == RecognitionStatus.RECOGNIZED
            and is_authorized_person
            and is_confident
        )

        token: Optional[str] = None
        expires_at: Optional[datetime] = None
        if verified:
            token = token_urlsafe(24)
            expires_at = datetime.now() + timedelta(
                seconds=self.verification_ttl_seconds
            )
            self.active_tokens[token] = {
                "person_id": recognition_result.person_id,
                "person_name": recognition_result.person_name,
                "device_id": device_id,
                "action": normalized_action,
                "expires_at": expires_at,
            }

        return {
            "verified": verified,
            "allowed": verified,
            "token": token,
            "expires_at": expires_at,
            "device_id": device_id,
            "action": normalized_action,
            "result": recognition_result,
        }

    def consume_token(
        self, token: Optional[str], device_id: str, action: Optional[str] = None
    ) -> bool:
        """Validate and consume a one-time verification token."""
        self._cleanup_expired_tokens()
        if not token:
            return False

        payload = self.active_tokens.get(token)
        if not payload:
            return False

        expected_device_id = payload.get("device_id")
        expected_action = payload.get("action")
        normalized_action = action.lower() if action else None

        if expected_device_id and expected_device_id != device_id:
            return False

        if expected_action and expected_action != normalized_action:
            return False

        del self.active_tokens[token]
        return True

    def requires_verification(
        self, device_id: str, action: Optional[str] = None, toggle: bool = False
    ) -> bool:
        """Determine whether a device action needs face verification."""
        device = self.device_manager.get_device(device_id)
        if not device or device.type != DeviceType.LOCK:
            return False

        if toggle:
            return device.state == "locked"

        normalized_action = (action or "").lower()
        return normalized_action in self.PROTECTED_LOCK_ACTIONS

    def _is_authorized_person(self, result: RecognitionResult) -> bool:
        if result.status != RecognitionStatus.RECOGNIZED or not result.person_id:
            return False

        if not self.authorized_person_ids:
            return True

        return result.person_id in self.authorized_person_ids

    def _cleanup_expired_tokens(self) -> None:
        now = datetime.now()
        expired = [
            token
            for token, payload in self.active_tokens.items()
            if payload["expires_at"] <= now
        ]
        for token in expired:
            del self.active_tokens[token]
