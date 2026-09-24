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

def test_whatsapp_help_message(client):
    res = client.post(
        "/webhooks/whatsapp",
        data={"From": "whatsapp:+919876543210", "Body": "help"}
    )
    assert res.status_code == 200
    assert "text/xml" in res.headers["content-type"] or "application/xml" in res.headers["content-type"]
    assert "Welcome to the Real-Time Hyperlocal Information Engine" in res.text

def test_whatsapp_report_and_question_flow(client):
    # 1. Report traffic via WhatsApp
    rep_res = client.post(
        "/webhooks/whatsapp",
        data={"From": "whatsapp:+919876543210", "Body": "Report: Heavy traffic near Begumpet"}
    )
    assert rep_res.status_code == 200
    assert "Your report has been recorded" in rep_res.text
    assert "Begumpet" in rep_res.text

    # 2. Ask question via WhatsApp
    q_res = client.post(
        "/webhooks/whatsapp",
        data={"From": "whatsapp:+919876543211", "Body": "Is there heavy traffic near Begumpet?"}
    )
    assert q_res.status_code == 200
    assert "Begumpet" in q_res.text
    assert "Reported: HEAVY traffic" in q_res.text
