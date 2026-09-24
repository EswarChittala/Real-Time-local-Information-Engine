from datetime import datetime, timedelta, timezone
from app.models.observation import Observation
from app.services.consensus_service import ConsensusService

def create_mock_obs(reporter_id: int, value_state: str, minutes_ago: int = 5):
    obs = Observation()
    obs.id = reporter_id * 10
    obs.reporter_id = reporter_id
    obs.category = "TRAFFIC"
    obs.event_type = "STATUS"
    obs.location_id = 1
    obs.value_state = value_state
    obs.raw_message = f"Traffic is {value_state}"
    obs.source = "WHATSAPP"
    obs.confidence = 1.0
    obs.observed_at = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    return obs

def test_zero_reports_is_unknown():
    res = ConsensusService.calculate_consensus([])
    assert res.status == "UNKNOWN"
    assert res.witness_count == 0
    assert res.winning_state is None

def test_single_report_is_reported():
    obs = [create_mock_obs(reporter_id=1, value_state="HEAVY")]
    res = ConsensusService.calculate_consensus(obs)
    assert res.status == "REPORTED"
    assert res.witness_count == 1
    assert res.winning_state == "HEAVY"

def test_two_independent_agreeing_reports_is_confirmed():
    obs = [
        create_mock_obs(reporter_id=1, value_state="HEAVY"),
        create_mock_obs(reporter_id=2, value_state="HEAVY"),
    ]
    res = ConsensusService.calculate_consensus(obs)
    assert res.status == "CONFIRMED"
    assert res.witness_count == 2
    assert res.winning_state == "HEAVY"

def test_same_user_repeated_reports_counts_as_single_witness():
    # User 1 sends 3 reports
    obs = [
        create_mock_obs(reporter_id=1, value_state="HEAVY", minutes_ago=10),
        create_mock_obs(reporter_id=1, value_state="HEAVY", minutes_ago=5),
        create_mock_obs(reporter_id=1, value_state="HEAVY", minutes_ago=1),
    ]
    res = ConsensusService.calculate_consensus(obs)
    assert res.status == "REPORTED"  # NOT CONFIRMED because it's only 1 independent person
    assert res.witness_count == 1
    assert res.total_reporters == 1

def test_conflicting_reports_is_conflicting():
    obs = [
        create_mock_obs(reporter_id=1, value_state="HEAVY"),
        create_mock_obs(reporter_id=2, value_state="CLEAR"),
    ]
    res = ConsensusService.calculate_consensus(obs)
    assert res.status == "CONFLICTING"
