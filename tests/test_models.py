import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.location import Location
from app.models.entity import Entity
from app.models.observation import Observation
from app.models.question import Question
from app.models.user_preference import UserPreference
from app.models.notification import Notification

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_create_user_and_location(db_session):
    user = User(phone_number="+919876543210", name="Ravi Kumar", opted_in_notifications=True)
    location = Location(name="Begumpet", slug="begumpet", radius_meters=1500, aliases=["begumpet-x-roads"])
    db_session.add(user)
    db_session.add(location)
    db_session.commit()

    assert user.id is not None
    assert location.id is not None
    assert location.slug == "begumpet"
    assert "begumpet-x-roads" in location.aliases

def test_observation_creation_and_relationship(db_session):
    user = User(phone_number="+919876543211", name="Priya")
    location = Location(name="Hitec City", slug="hitec-city")
    db_session.add_all([user, location])
    db_session.commit()

    obs = Observation(
        reporter_id=user.id,
        category="TRAFFIC",
        event_type="CONGESTION",
        location_id=location.id,
        value_state="HEAVY",
        raw_message="Heavy traffic moving very slowly towards cyber towers",
        source="WHATSAPP",
        confidence=1.0
    )
    db_session.add(obs)
    db_session.commit()

    assert obs.id is not None
    assert obs.reporter.name == "Priya"
    assert obs.location.name == "Hitec City"
    assert obs.value_state == "HEAVY"

def test_question_and_user_preference(db_session):
    user = User(phone_number="+919876543212", name="Kiran")
    location = Location(name="Ameerpet", slug="ameerpet")
    db_session.add_all([user, location])
    db_session.commit()

    pref = UserPreference(user_id=user.id, category="TRAFFIC", location_id=location.id, notification_enabled=True)
    q = Question(user_id=user.id, raw_query="How is traffic in Ameerpet?", parsed_category="TRAFFIC", parsed_location_id=location.id)
    
    db_session.add_all([pref, q])
    db_session.commit()

    assert pref.id is not None
    assert q.id is not None
    assert len(user.preferences) == 1
    assert len(user.questions) == 1
