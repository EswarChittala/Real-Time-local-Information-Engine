from fastapi import APIRouter, Depends, Form, Header, Request, Response, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.services.whatsapp_service import WhatsAppService
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/webhooks/whatsapp", tags=["WhatsApp"])

@router.post("", response_class=Response)
async def twilio_whatsapp_webhook(
    request: Request,
    From: str = Form(..., description="Sender phone number, e.g. whatsapp:+919876543210"),
    Body: str = Form(..., description="Message text sent by the user"),
    x_twilio_signature: Optional[str] = Header(None, alias="X-Twilio-Signature"),
    db: Session = Depends(get_db)
):
    # Strip 'whatsapp:' prefix if present
    sender_phone = From.replace("whatsapp:", "").strip()

    # Conversation handling
    conv_service = ConversationService(db)
    reply_text = conv_service.handle_incoming_message(sender_phone=sender_phone, message_body=Body)

    # Return valid TwiML response
    twiml = WhatsAppService.build_twiml_response(reply_text)
    return Response(content=twiml, media_type="application/xml")
