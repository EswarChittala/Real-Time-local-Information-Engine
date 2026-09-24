import re
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.observation import ObservationCreate
from app.schemas.question import QuestionCreate
from app.services.observation_service import ObservationService
from app.services.question_service import QuestionService
from app.services.location_service import LocationService

class ConversationService:
    def __init__(self, db: Session):
        self.db = db
        self.obs_service = ObservationService(db)
        self.question_service = QuestionService(db)
        self.location_service = LocationService(db)

    def handle_incoming_message(self, sender_phone: str, message_body: str) -> str:
        text = message_body.strip()
        text_lower = text.lower()

        # 1. Greetings / Help
        if text_lower in ["hi", "hello", "help", "menu", "start"]:
            return (
                "👋 Welcome to the Real-Time Hyperlocal Information Engine!\n\n"
                "• Ask a question: e.g., 'Is there heavy traffic near Begumpet?' or 'Is the ration shop open?'\n"
                "• Submit a report: e.g., 'Report: Heavy traffic near Begumpet' or 'Ration shop is open in Ameerpet'\n"
                "• Type 'optin' or 'optout' to manage notifications."
            )

        # 2. Check if the message is a report/observation submission
        is_report = (
            text_lower.startswith("report")
            or "is heavy" in text_lower
            or "is clear" in text_lower
            or "is open" in text_lower
            or "is closed" in text_lower
            or "road blocked" in text_lower
            or "jam near" in text_lower
        ) and not text.endswith("?")

        # 3. AI / Regional Language Fallback check if message has dialect or unknown structure
        from app.services.ai_service import AIService
        if any(w in text_lower for w in ["unda", "undi", "dukanam", "jaam", "bagundi", "baga", "bandh"]):
            ai_intent = AIService.parse_with_heuristics(text)
            if ai_intent.is_report and ai_intent.value_state:
                return self._handle_report(sender_phone, text, parsed_intent=ai_intent)
            else:
                return self._handle_question(sender_phone, text, parsed_intent=ai_intent)

        if is_report:
            return self._handle_report(sender_phone, text)

        # 4. Otherwise, treat as a question
        return self._handle_question(sender_phone, text)

    def _handle_report(self, sender_phone: str, text: str, parsed_intent=None) -> str:
        text_lower = text.lower()

        # Category
        if parsed_intent and parsed_intent.category != "GENERAL":
            category = parsed_intent.category
        else:
            category = "TRAFFIC"
            if "shop" in text_lower or "ration" in text_lower:
                category = "SHOP"
            elif "road" in text_lower or "blocked" in text_lower:
                category = "ROAD"
            elif "water" in text_lower:
                category = "WATER"
            elif "power" in text_lower:
                category = "POWER"

        # Value state
        if parsed_intent and parsed_intent.value_state:
            value_state = parsed_intent.value_state
        else:
            value_state = "REPORTED"
            if "heavy" in text_lower or "jam" in text_lower:
                value_state = "HEAVY"
            elif "clear" in text_lower or "smooth" in text_lower or "moving" in text_lower:
                value_state = "CLEAR"
            elif "open" in text_lower:
                value_state = "OPEN"
            elif "closed" in text_lower:
                value_state = "CLOSED"
            elif "blocked" in text_lower:
                value_state = "BLOCKED"

        # Resolve location
        loc_name_hint = parsed_intent.location if parsed_intent else None
        location = self.location_service.resolve_location(location_name=loc_name_hint, text=text)
        loc_name = location.name if location else (loc_name_hint or "General Area")

        # Save observation
        obs_create = ObservationCreate(
            reporter_phone=sender_phone,
            location_name=loc_name,
            category=category,
            event_type="STATUS",
            value_state=value_state,
            raw_message=text,
            source="WHATSAPP"
        )
        self.obs_service.record_observation(obs_create)

        return (
            f"✅ Thank you! Your report has been recorded:\n"
            f"📍 Location: {loc_name}\n"
            f"📌 Category: {category} ({value_state})\n"
            f"Your observation helps keep your local community informed."
        )

    def _handle_question(self, sender_phone: str, text: str, parsed_intent=None) -> str:
        category = parsed_intent.category if parsed_intent and parsed_intent.category != "GENERAL" else None
        location_name = parsed_intent.location if parsed_intent else None

        q_create = QuestionCreate(
            user_phone=sender_phone,
            raw_query=text,
            location_name=location_name,
            category=category
        )
        res = self.question_service.ask_question(q_create)
        return res.answer
