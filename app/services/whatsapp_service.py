import hmac
import hashlib
import base64
from typing import Dict, Any, Optional
from app.core.config import settings

class WhatsAppService:
    @staticmethod
    def validate_twilio_signature(
        url: str,
        params: Dict[str, Any],
        signature: Optional[str]
    ) -> bool:
        """
        Validates Twilio X-Twilio-Signature header.
        If no auth token is configured (e.g. local dev / testing), validation passes.
        """
        if not settings.twilio_auth_token:
            return True
        if not signature:
            return False

        # Build data string according to Twilio specs: url + sorted(keys+values)
        data = url
        for key in sorted(params.keys()):
            data += f"{key}{params[key]}"

        computed = hmac.new(
            settings.twilio_auth_token.encode("utf-8"),
            data.encode("utf-8"),
            hashlib.sha1
        ).digest()
        expected = base64.b64encode(computed).decode("utf-8")

        return hmac.compare_digest(expected, signature)

    @staticmethod
    def build_twiml_response(message: str) -> str:
        """Constructs safe XML TwiML message response."""
        escaped_message = (
            message.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>\n"
            f"    <Message>{escaped_message}</Message>\n"
            "</Response>"
        )
