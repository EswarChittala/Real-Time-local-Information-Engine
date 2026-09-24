import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.db.session import get_db

@pytest.fixture
def client_and_db():
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
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_create_and_search_observation(client_and_db):
    client = client_and_db
    
    # 1. Create observation
    payload = {
        "reporter_phone": "+919999999991",
        "location_name": "Begumpet",
        "category": "TRAFFIC",
        "event_type": "CONGESTION",
        "value_state": "HEAVY",
        "raw_message": "Heavy traffic jam near lifestyle building",
        "source": "WHATSAPP",
        "confidence": 1.0
    }
    res = client.post("/observations", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["category"] == "TRAFFIC"
    assert data["value_state"] == "HEAVY"
    assert data["id"] is not None

    # 2. Search observations
    search_res = client.get("/observations/search?category=TRAFFIC")
    assert search_res.status_code == 200
    results = search_res.json()
    assert len(results) == 1
    assert results[0]["value_state"] == "HEAVY"
