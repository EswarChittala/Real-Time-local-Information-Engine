from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.models.question import Question

class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, question: Question) -> Question:
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def get_by_id(self, question_id: int) -> Optional[Question]:
        return self.db.get(Question, question_id)

    def update_answer(self, question_id: int, answer: str, status: str) -> Optional[Question]:
        q = self.get_by_id(question_id)
        if q:
            q.answer_text = answer
            q.status = status
            self.db.commit()
            self.db.refresh(q)
        return q

    def get_recent_by_user(self, user_id: int, limit: int = 10) -> List[Question]:
        query = select(Question).where(Question.user_id == user_id).order_by(desc(Question.created_at)).limit(limit)
        return list(self.db.execute(query).scalars().all())
