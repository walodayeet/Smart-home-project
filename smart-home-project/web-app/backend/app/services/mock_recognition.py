import random
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from PIL import Image

from app.models.schemas import RecognitionResult, RecognitionStatus, AccessLogEntry


class MockRecognitionService:
    """Mock face recognition service for demo purposes."""

    # Mock known persons
    KNOWN_PERSONS = [
        {"id": "person_001", "name": "Home Owner"},
        {"id": "person_002", "name": "Family Member"},
        {"id": "person_003", "name": "Guest"},
    ]

    def __init__(self):
        self.recent_events: List[RecognitionResult] = []
        self.access_log: List[AccessLogEntry] = []
        self._generate_initial_events()

    def _generate_initial_events(self):
        """Generate some initial events for demo."""
        now = datetime.now()

        # Add some past events
        for i in range(5):
            event_time = now - timedelta(minutes=i * 15)

            if i % 3 == 0:
                # Recognized event
                person = self.KNOWN_PERSONS[0]
                event = RecognitionResult(
                    status=RecognitionStatus.RECOGNIZED,
                    person_id=person["id"],
                    person_name=person["name"],
                    confidence=0.92 + random.random() * 0.07,
                    timestamp=event_time,
                    message=f"Recognized: {person['name']}",
                    requires_action=False,
                )
            elif i % 3 == 1:
                # Unknown person
                event = RecognitionResult(
                    status=RecognitionStatus.UNKNOWN,
                    confidence=0.0,
                    timestamp=event_time,
                    message="Unknown person detected",
                    requires_action=True,
                )
            else:
                # Masked person
                event = RecognitionResult(
                    status=RecognitionStatus.MASKED,
                    confidence=0.75 + random.random() * 0.15,
                    timestamp=event_time,
                    message="Person wearing mask - partial recognition",
                    requires_action=False,
                )

            self.recent_events.append(event)

            # Add to access log
            self.access_log.append(
                AccessLogEntry(
                    id=str(uuid.uuid4()),
                    timestamp=event_time,
                    person_name=event.person_name,
                    person_id=event.person_id,
                    camera_id="cam_front_door",
                    camera_name="Front Door",
                    event_type=event.status.value,
                    confidence=event.confidence if event.confidence > 0 else None,
                )
            )

    def recognize(self, image: Image.Image) -> RecognitionResult:
        """
        Perform mock face recognition on an image.
        Returns random results for demo purposes.
        """
        # Simulate recognition with weighted random outcomes
        outcomes = [
            (RecognitionStatus.RECOGNIZED, 0.5),  # 50% chance
            (RecognitionStatus.UNKNOWN, 0.3),  # 30% chance
            (RecognitionStatus.MASKED, 0.2),  # 20% chance
        ]

        status = random.choices(
            [o[0] for o in outcomes], weights=[o[1] for o in outcomes]
        )[0]

        now = datetime.now()

        if status == RecognitionStatus.RECOGNIZED:
            person = random.choice(self.KNOWN_PERSONS)
            confidence = 0.85 + random.random() * 0.14
            result = RecognitionResult(
                status=status,
                person_id=person["id"],
                person_name=person["name"],
                confidence=round(confidence, 3),
                timestamp=now,
                message=f"Recognized: {person['name']}",
                requires_action=False,
            )

        elif status == RecognitionStatus.UNKNOWN:
            result = RecognitionResult(
                status=status,
                confidence=0.0,
                timestamp=now,
                message="Unknown person detected - Alert sent to owner",
                requires_action=True,
            )

        else:  # MASKED
            confidence = 0.60 + random.random() * 0.30
            result = RecognitionResult(
                status=status,
                confidence=round(confidence, 3),
                timestamp=now,
                message="Person wearing mask - partial face visible",
                requires_action=False,
            )

        # Store event
        self.recent_events.insert(0, result)
        self.recent_events = self.recent_events[:50]  # Keep last 50

        # Add to access log
        self.access_log.insert(
            0,
            AccessLogEntry(
                id=str(uuid.uuid4()),
                timestamp=now,
                person_name=result.person_name,
                person_id=result.person_id,
                camera_id="cam_front_door",
                camera_name="Front Door",
                event_type=result.status.value,
                confidence=result.confidence if result.confidence > 0 else None,
            ),
        )
        self.access_log = self.access_log[:100]  # Keep last 100

        return result

    def get_recent_events(self, limit: int = 10) -> List[RecognitionResult]:
        """Get recent recognition events."""
        return self.recent_events[:limit]

    def get_access_log(self, limit: int = 50) -> List[AccessLogEntry]:
        """Get access log entries."""
        return self.access_log[:limit]
