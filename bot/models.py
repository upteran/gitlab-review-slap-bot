from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class UserStatus(Enum):
    IDLE = "idle"
    REVIEWING = "reviewing"
    IN_QUEUE = "in_queue"

@dataclass
class User:
    id: int
    telegram_id: int
    chat_id: int
    gitlab_name: str
    jira_name: str
    status: UserStatus
    current_review: str = None
    review_time: datetime = None 