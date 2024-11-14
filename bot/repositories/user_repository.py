from datetime import datetime
from typing import List, Optional
from ..models import User, UserStatus
from .base_repository import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self._init_table()

    def _init_table(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    gitlab_name TEXT NOT NULL,
                    jira_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_review TEXT,
                    review_time TIMESTAMP,
                    UNIQUE(telegram_id, chat_id)
                )
            ''')
            conn.commit()

    def add_user(self, telegram_id: int, chat_id: int, gitlab_name: str, jira_name: str) -> User:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO users (telegram_id, chat_id, gitlab_name, jira_name, status)
                   VALUES (?, ?, ?, ?, ?)''',
                (telegram_id, chat_id, gitlab_name, jira_name, UserStatus.IN_QUEUE.value)
            )
            conn.commit()
            return self.get_user(telegram_id, chat_id)

    def get_user(self, telegram_id: int, chat_id: int) -> Optional[User]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE telegram_id = ? AND chat_id = ?',
                (telegram_id, chat_id)
            )
            row = cursor.fetchone()
            return self._map_to_user(row) if row else None

    def get_next_reviewer(self, chat_id: int, mr_author_gitlab_name: str) -> Optional[User]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM users 
                   WHERE chat_id = ? 
                   AND status = ? 
                   AND gitlab_name != ?
                   ORDER BY review_time ASC NULLS FIRST
                   LIMIT 1''',
                (chat_id, UserStatus.IN_QUEUE.value, mr_author_gitlab_name)
            )
            row = cursor.fetchone()
            return self._map_to_user(row) if row else None

    def update_user_review_status(self, user_id: int, status: UserStatus, 
                                current_review: str = None) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''UPDATE users 
                   SET status = ?, current_review = ?, review_time = ?
                   WHERE id = ?''',
                (status.value, current_review, 
                 datetime.now() if status == UserStatus.REVIEWING else None, 
                 user_id)
            )
            conn.commit()

    def _map_to_user(self, row) -> User:
        return User(
            id=row[0],
            telegram_id=row[1],
            chat_id=row[2],
            gitlab_name=row[3],
            jira_name=row[4],
            status=UserStatus(row[5]),
            current_review=row[6],
            review_time=row[7]
        ) 

    def delete_user(self, telegram_id: int, chat_id: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM users WHERE telegram_id = ? AND chat_id = ?',
                (telegram_id, chat_id)
            )
            conn.commit()