import re
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionAnswerResponse
from app.schemas.observation import ObservationRead
from app.repositories.user_repository import UserRepository
from app.repositories.question_repository import QuestionRepository
from app.services.location_service import LocationService
from app.services.retrieval_service import RetrievalService
from app.services.consensus_service import ConsensusService
from app.services.response_service import ResponseService

class QuestionService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.question_repo = QuestionRepository(db)
        self.location_service = LocationService(db)
        self.retrieval_service = RetrievalService(db)

    def parse_intent(self, text: str) -> Tuple[str, Optional[str]]:
        """Deterministic query parser for category and keywords."""
        text_lower = text.lower()

        # Category detection
        category = "GENERAL"
        if any(w in text_lower for w in ["traffic", "jam", "rush", "vehicles", "cars"]):
            category = "TRAFFIC"
        elif any(w in text_lower for w in ["shop", "store", "ration", "market"]):
            category = "SHOP"
        elif any(w in text_lower for w in ["road", "blocked", "closure", "pothole", "route"]):
            category = "ROAD"
        elif any(w in text_lower for w in ["water", "tanker", "pipeline", "supply"]):
            category = "WATER"
        elif any(w in text_lower for w in ["power", "electricity", "current", "outage"]):
            category = "POWER"

        return category, None

    def ask_question(self, data: QuestionCreate) -> QuestionAnswerResponse:
        user = self.user_repo.get_or_create(phone=data.user_phone)

        # 1. Parse category
        category = data.category.upper() if data.category else self.parse_intent(data.raw_query)[0]

        # 2. Resolve location
        location = self.location_service.resolve_location(
            location_name=data.location_name,
            text=data.raw_query
        )
        location_id = location.id if location else None
        location_name = location.name if location else (data.location_name or "Unknown Location")

        # 3. Retrieve fresh observations
        observations = []
        max_age = self.retrieval_service.get_max_age_for_category(category)
        if location_id:
            observations = self.retrieval_service.retrieve_fresh_observations(
                category=category,
                location_id=location_id
            )

        # 4. Consensus
        consensus = ConsensusService.calculate_consensus(observations)

        # 5. Format natural answer
        answer = ResponseService.format_answer(
            category=category,
            location_name=location_name,
            consensus=consensus,
            max_age_minutes=max_age
        )

        # 6. Save question record
        question_status = "ANSWERED" if consensus.status in ["CONFIRMED", "REPORTED"] else (
            "CONFLICTING" if consensus.status == "CONFLICTING" else "UNKNOWN"
        )
        q = Question(
            user_id=user.id,
            raw_query=data.raw_query,
            parsed_category=category,
            parsed_location_id=location_id,
            status=question_status,
            answer_text=answer
        )
        saved_q = self.question_repo.create(q)

        # Serialize observations for response
        obs_reads = [ObservationRead.model_validate(obs) for obs in observations]

        return QuestionAnswerResponse(
            question_id=saved_q.id,
            user_phone=user.phone_number,
            query=data.raw_query,
            category=category,
            location_name=location_name,
            consensus_status=consensus.status,
            value_state=consensus.winning_state,
            witness_count=consensus.witness_count,
            answer=answer,
            recent_observations=obs_reads
        )
