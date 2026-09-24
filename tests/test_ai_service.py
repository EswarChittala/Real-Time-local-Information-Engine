import pytest
from app.services.ai_service import AIService, AIParsedIntent

def test_regional_heauristics_telugu_english_traffic():
    # "Begumpet lo traffic unda?" (Is there traffic in Begumpet?)
    intent = AIService.parse_with_heuristics("Begumpet lo traffic unda?")
    assert intent.category == "TRAFFIC"
    assert intent.location == "Begumpet"
    assert intent.is_report is False

def test_regional_heuristics_telugu_english_shop():
    # "Ameerpet daggara ration dukanam open unda?"
    intent = AIService.parse_with_heuristics("Ameerpet daggara ration dukanam open unda?")
    assert intent.category == "SHOP"
    assert intent.location == "Ameerpet"
    assert intent.is_report is False

def test_regional_heuristics_traffic_heavy_report():
    # "Begumpet lo baga traffic undi" (There is heavy traffic in Begumpet)
    intent = AIService.parse_with_heuristics("Begumpet lo baga traffic undi")
    assert intent.category == "TRAFFIC"
    assert intent.value_state == "HEAVY"
    assert intent.location == "Begumpet"
    assert intent.is_report is True
