from dataclasses import dataclass
from typing import List, Optional, Dict
from collections import defaultdict
from app.models.observation import Observation
from app.core.config import settings

@dataclass
class ConsensusResult:
    status: str  # 'CONFIRMED', 'REPORTED', 'UNKNOWN', 'CONFLICTING'
    winning_state: Optional[str]
    witness_count: int
    total_reporters: int
    state_votes: Dict[str, int]

class ConsensusService:
    @staticmethod
    def calculate_consensus(observations: List[Observation]) -> ConsensusResult:
        if not observations:
            return ConsensusResult(
                status="UNKNOWN",
                winning_state=None,
                witness_count=0,
                total_reporters=0,
                state_votes={}
            )

        # De-duplicate by reporter: only count the latest observation from each independent reporter
        latest_by_reporter: Dict[int, Observation] = {}
        for obs in sorted(observations, key=lambda x: x.observed_at):
            latest_by_reporter[obs.reporter_id] = obs

        # Count independent votes per value_state
        state_votes: Dict[str, int] = defaultdict(int)
        for obs in latest_by_reporter.values():
            state_votes[obs.value_state.upper()] += 1

        total_reporters = len(latest_by_reporter)

        # If more than one distinct state has votes, check for conflict
        if len(state_votes) > 1:
            sorted_states = sorted(state_votes.items(), key=lambda item: item[1], reverse=True)
            # If top two states have conflicting reports within the window
            if sorted_states[0][1] == sorted_states[1][1]:
                return ConsensusResult(
                    status="CONFLICTING",
                    winning_state=None,
                    witness_count=sorted_states[0][1],
                    total_reporters=total_reporters,
                    state_votes=dict(state_votes)
                )
            # Or if strong disagreement exists
            return ConsensusResult(
                status="CONFLICTING",
                winning_state=sorted_states[0][0],
                witness_count=sorted_states[0][1],
                total_reporters=total_reporters,
                state_votes=dict(state_votes)
            )

        # Exactly one state reported
        winning_state, vote_count = next(iter(state_votes.items()))

        if vote_count >= settings.min_independent_witnesses_confirmed:
            status = "CONFIRMED"
        elif vote_count == 1:
            status = "REPORTED"
        else:
            status = "UNKNOWN"

        return ConsensusResult(
            status=status,
            winning_state=winning_state,
            witness_count=vote_count,
            total_reporters=total_reporters,
            state_votes=dict(state_votes)
        )
