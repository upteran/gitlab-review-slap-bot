from typing import Optional, Tuple
from ..models import User, UserStatus
from ..repositories.user_repository import UserRepository

class ReviewService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def assign_review(self, chat_id: int, mr_link: str, 
                     mr_author_gitlab_name: str) -> Tuple[bool, Optional[User], str]:
        try:
            reviewer = self.user_repository.get_next_reviewer(chat_id, mr_author_gitlab_name)
            if not reviewer:
                return False, None, "No available reviewers in the queue"

            self.user_repository.update_user_review_status(
                reviewer.id, 
                UserStatus.REVIEWING, 
                mr_link
            )
            return True, reviewer, "Review successfully assigned"
        except Exception as e:
            return False, None, f"Error assigning review: {str(e)}"

    def end_review(self, user: User) -> Tuple[bool, str]:
        try:
            self.user_repository.update_user_review_status(
                user.id,
                UserStatus.IN_QUEUE,
                None
            )
            return True, "Review ended successfully"
        except Exception as e:
            return False, f"Error ending review: {str(e)}" 