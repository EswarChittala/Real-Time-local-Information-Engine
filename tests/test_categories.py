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

def test_shop_category_flow(client):
    # Two observers report ration shop open in Ameerpet
    client.post("/observations", json={
        "reporter_phone": "+919000000001",
        "location_name": "Ameerpet",
        "category": "SHOP",
        "event_type": "STATUS",
        "value_state": "OPEN",
        "raw_message": "Ration shop #42 is open right now",
        "source": "WHATSAPP"
    })
    client.post("/observations", json={
        "reporter_phone": "+919000000002",
        "location_name": "Ameerpet",
        "category": "SHOP",
        "event_type": "STATUS",
        "value_state": "OPEN",
        "raw_message": "Yes bought rice, ration shop is open",
        "source": "WHATSAPP"
    })

    # User asks about the ration shop
    res = client.post("/questions", json={
        "user_phone": "+919000000003",
        "raw_query": "Is the ration shop open near Ameerpet?",
        "location_name": "Ameerpet",
        "category": "SHOP"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["category"] == "SHOP"
    assert data["consensus_status"] == "CONFIRMED"
    assert data["value_state"] == "OPEN"
    assert "Confirmed: OPEN shop near Ameerpet" in data["answer"]

def test_water_category_flow(client):
    # Reporter reports water supply available in Kukatpally
    client.post("/observations", json={
        "reporter_phone": "+919000000004",
        "location_name": "Kukatpally",
        "category": "WATER",
        "event_type": "SUPPLY",
        "value_state": "AVAILABLE",
        "raw_message": "Municipal water supply started at 6am",
        "source": "WHATSAPP"
    })

    res = client.post("/questions", json={
        "user_phone": "+919000000005",
        "raw_query": "Is water available in Kukatpally?",
        "location_name": "Kukatpally",
        "category": "WATER"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["category"] == "WATER"
    assert data["consensus_status"] == "REPORTED"
    assert data["value_state"] == "AVAILABLE"
