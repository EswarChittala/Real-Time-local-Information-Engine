import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.db.session import get_db

@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()

def test_ask_question_unknown_when_no_data(client):
    res = client.post("/questions", json={
        "user_phone": "+918888888881",
        "raw_query": "Is there heavy traffic near Begumpet?",
        "location_name": "Begumpet",
        "category": "TRAFFIC"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["consensus_status"] == "UNKNOWN"
    assert data["witness_count"] == 0
    assert "No recent reports" in data["answer"]

def test_end_to_end_traffic_demonstration(client):
    """
    Demonstration from Section 19 & 22 of Specification:
    User A reports heavy traffic near Begumpet
    User B reports heavy traffic near Begumpet
    User C asks about traffic near Begumpet
    System retrieves reports -> confirms 2 independent witnesses -> answers C as CONFIRMED!
    """
    # 1. User A reports heavy traffic
    res_a = client.post("/observations", json={
        "reporter_phone": "+919000000001",
        "location_name": "Begumpet",
        "category": "TRAFFIC",
        "event_type": "CONGESTION",
        "value_state": "HEAVY",
        "raw_message": "Begumpet bridge completely choked with heavy traffic",
        "source": "WHATSAPP"
    })
    assert res_a.status_code == 201

    # 2. User C asks before second report -> should be REPORTED (1 witness)
    res_c1 = client.post("/questions", json={
        "user_phone": "+919000000003",
        "raw_query": "Is there heavy traffic near Begumpet?",
        "location_name": "Begumpet"
    })
    assert res_c1.status_code == 200
    assert res_c1.json()["consensus_status"] == "REPORTED"
    assert res_c1.json()["witness_count"] == 1

    # 3. User B reports heavy traffic
    res_b = client.post("/observations", json={
        "reporter_phone": "+919000000002",
        "location_name": "Begumpet",
        "category": "TRAFFIC",
        "event_type": "CONGESTION",
        "value_state": "HEAVY",
        "raw_message": "Stuck in heavy traffic near Begumpet flyover",
        "source": "WHATSAPP"
    })
    assert res_b.status_code == 201

    # 4. User C asks again -> should be CONFIRMED (2 independent witnesses)
    res_c2 = client.post("/questions", json={
        "user_phone": "+919000000003",
        "raw_query": "Is there heavy traffic near Begumpet?",
        "location_name": "Begumpet"
    })
    assert res_c2.status_code == 200
    data = res_c2.json()
    assert data["consensus_status"] == "CONFIRMED"
    assert data["witness_count"] == 2
    assert data["value_state"] == "HEAVY"
    assert "Confirmed: HEAVY traffic near Begumpet" in data["answer"]
    assert len(data["recent_observations"]) == 2
