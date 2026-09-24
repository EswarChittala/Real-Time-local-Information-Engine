from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_phone(self, phone: str) -> Optional[User]:
        stmt = select(User).where(User.phone_number == phone)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_or_create(self, phone: str, name: Optional[str] = None) -> User:
        user = self.get_by_phone(phone)
        if not user:
            user = User(phone_number=phone, name=name)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        elif name and not user.name:
            user.name = name
            self.db.commit()
            self.db.refresh(user)
        return user
