from typing import Optional
from app.services.consensus_service import ConsensusResult

class ResponseService:
    @staticmethod
    def format_answer(
        category: str,
        location_name: str,
        consensus: ConsensusResult,
        max_age_minutes: int
    ) -> str:
        cat_lower = category.lower()
        
        if consensus.status == "CONFIRMED":
            return (
                f"Confirmed: {consensus.winning_state} {cat_lower} near {location_name} "
                f"(verified by {consensus.witness_count} independent reports in the last {max_age_minutes} minutes)."
            )
        elif consensus.status == "REPORTED":
            return (
                f"Reported: {consensus.winning_state} {cat_lower} near {location_name} "
                f"(reported by 1 observer in the last {max_age_minutes} minutes, unconfirmed)."
            )
        elif consensus.status == "CONFLICTING":
            details = ", ".join(f"{state}: {votes}" for state, votes in consensus.state_votes.items())
            return (
                f"Conflicting reports near {location_name} for {cat_lower} ({details}). "
                f"Conditions may be changing rapidly."
            )
        else:  # UNKNOWN
            return (
                f"No recent reports for {cat_lower} near {location_name} in the last {max_age_minutes} minutes."
            )
