from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.question import QuestionCreate, QuestionAnswerResponse
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.post("", response_model=QuestionAnswerResponse, status_code=status.HTTP_200_OK)
def ask_question(
    data: QuestionCreate,
    db: Session = Depends(get_db)
):
    service = QuestionService(db)
    return service.ask_question(data)
