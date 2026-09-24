import json
import logging
from typing import Optional
from pydantic import BaseModel, Field
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIParsedIntent(BaseModel):
    category: str = Field(default="GENERAL", description="TRAFFIC, SHOP, ROAD, WATER, POWER, GENERAL")
    location: Optional[str] = Field(default=None, description="Extracted location or landmark name")
    value_state: Optional[str] = Field(default=None, description="HEAVY, CLEAR, OPEN, CLOSED, BLOCKED, etc.")
    is_report: bool = Field(default=False, description="True if statement of fact/report, False if question")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)

class AIService:
    @staticmethod
    def parse_with_heuristics(text: str) -> AIParsedIntent:
        """
        Built-in parser for regional multilingual queries (Telugu-English transliteration, slang).
        Handles: 'Begumpet lo traffic unda?', 'ration dukanam open aa?', 'traffic baga undi'
        """
        text_lower = text.lower()
        
        # Category detection
        category = "GENERAL"
        if any(k in text_lower for k in ["traffic", "jaam", "vehicles", "gaadi"]):
            category = "TRAFFIC"
        elif any(k in text_lower for k in ["shop", "dukanam", "angadi", "ration", "store"]):
            category = "SHOP"
        elif any(k in text_lower for k in ["road", "daari", "raasta", "bridge", "flyover"]):
            category = "ROAD"
        elif any(k in text_lower for k in ["water", "neellu", "tanker"]):
            category = "WATER"
        elif any(k in text_lower for k in ["power", "current", "karentu", "karant"]):
            category = "POWER"

        # Determine if it's a question or report
        # Question indicators in Romanized Telugu/Hindi/English: 'unda', 'undi aa', 'open aa', '?', 'ela undi', 'kya hai'
        is_question = (
            "?" in text
            or any(q in text_lower for q in ["unda", "ela undi", "open aa", "closed aa", "kya", "hai kya", "available aa"])
        )
        is_report = not is_question

        # Value state detection
        value_state = None
        heavy_keywords = ["baga", "heavy", "ekkuva", "chala", "jaam", "jam"]
        clear_keywords = ["clear", "smooth", "khali", "free", "normal"]
        open_keywords = ["open", "terichi", "khula"]
        closed_keywords = ["close", "closed", "musisi", "bandh"]
        blocked_keywords = ["blocked", "block", "aapesaru", "roka"]

        if any(w in text_lower for w in heavy_keywords):
            value_state = "HEAVY"
        elif any(w in text_lower for w in clear_keywords):
            value_state = "CLEAR"
        elif any(w in text_lower for w in open_keywords):
            value_state = "OPEN"
        elif any(w in text_lower for w in closed_keywords):
            value_state = "CLOSED"
        elif any(w in text_lower for w in blocked_keywords):
            value_state = "BLOCKED"

        # Location extraction (e.g. "Begumpet lo" -> "Begumpet", "Ameerpet daggara" -> "Ameerpet")
        import re
        location = None
        loc_match = re.search(r'\b([A-Za-z0-9\-]+)\s+(?:lo|la|daggara|near|at|mein)\b', text, re.IGNORECASE)
        if loc_match:
            location = loc_match.group(1).capitalize()

        return AIParsedIntent(
            category=category,
            location=location,
            value_state=value_state,
            is_report=is_report,
            confidence=0.85
        )

    @classmethod
    async def parse_natural_language(cls, text: str) -> AIParsedIntent:
        """
        Calls Groq/Llama if API key is provided; otherwise uses built-in regional parser.
        Strictly advisory: output is validated against AIParsedIntent schema.
        """
        if not settings.groq_api_key:
            return cls.parse_with_heuristics(text)

        prompt = (
            "You are a parser for a hyperlocal information engine. "
            "Extract structured information from this Indian English/transliterated message. "
            "Return ONLY valid JSON with keys: category (TRAFFIC/SHOP/ROAD/WATER/POWER/GENERAL), "
            "location (string or null), value_state (string or null), is_report (boolean), confidence (float between 0 and 1).\n"
            f"Message: {text}"
        )

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.groq_api_key}"},
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.0
                    }
                )
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    return AIParsedIntent(**parsed)
        except Exception as e:
            logger.warning(f"Groq API call failed or timed out: {e}. Falling back to heuristics.")

        return cls.parse_with_heuristics(text)
