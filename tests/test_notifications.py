import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.base import Base
from app.models.user import User
from app.models.location import Location
from app.models.user_preference import UserPreference
from app.models.notification import Notification
from app.schemas.observation import ObservationCreate
from app.services.observation_service import ObservationService

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

def test_notification_delivery_and_cooldown(session):
    # 1. Setup location and user preference
    loc = Location(name="Begumpet", slug="begumpet")
    session.add(loc)
    subscriber = User(phone_number="+919111111111", name="Subscriber")
    session.add(subscriber)
    session.commit()

    pref = UserPreference(
        user_id=subscriber.id,
        category="TRAFFIC",
        location_id=loc.id,
        notification_enabled=True
    )
    session.add(pref)
    session.commit()

    # 2. Reporter submits observation
    obs_service = ObservationService(session)
    obs1 = obs_service.record_observation(ObservationCreate(
        reporter_phone="+919222222222",
        location_name="Begumpet",
        category="TRAFFIC",
        value_state="HEAVY",
        raw_message="Heavy traffic jam on flyover",
        source="WHATSAPP"
    ))

    # Check notification sent
    notifs = session.query(Notification).filter_by(user_id=subscriber.id).all()
    assert len(notifs) == 1
    assert notifs[0].status == "SENT"
    assert "Begumpet" in notifs[0].message

    # 3. Immediately submit another observation for same location & category (cooldown test)
    obs2 = obs_service.record_observation(ObservationCreate(
        reporter_phone="+919333333333",
        location_name="Begumpet",
        category="TRAFFIC",
        value_state="HEAVY",
        raw_message="Still blocked",
        source="WHATSAPP"
    ))

    notifs_after = session.query(Notification).filter_by(user_id=subscriber.id).order_by(Notification.id).all()
    assert len(notifs_after) == 2
    assert notifs_after[1].status == "SKIPPED_COOLDOWN"  # Anti-spam cooldown prevented notification spam
