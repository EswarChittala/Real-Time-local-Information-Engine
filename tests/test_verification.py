import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.base import Base
from app.models.user import User
from app.models.location import Location
from app.models.notification import Notification
from app.schemas.question import QuestionCreate
from app.services.question_service import QuestionService

@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSession()
    yield db
    db.close()

def test_verification_triggered_when_data_missing(session):
    # 1. Create a location and opted-in community users
    loc = Location(name="Begumpet", slug="begumpet")
    session.add(loc)

    helper1 = User(phone_number="+919000000010", name="Helper 1", opted_in_notifications=True)
    helper2 = User(phone_number="+919000000020", name="Helper 2", opted_in_notifications=True)
    session.add_all([helper1, helper2])
    session.commit()

    # 2. User asks a question with no observations
    service = QuestionService(session)
    q_create = QuestionCreate(
        user_phone="+919000000099",
        raw_query="Is there traffic near Begumpet?",
        location_name="Begumpet",
        category="TRAFFIC"
    )
    res = service.ask_question(q_create)

    # 3. Assert status and notifications created
    assert res.consensus_status == "UNKNOWN"
    assert "Fresh verification requested" in res.answer

    notifications = session.query(Notification).all()
    assert len(notifications) == 2
    assert any("+919000000010" == n.user.phone_number for n in notifications)
    assert any("+919000000020" == n.user.phone_number for n in notifications)
