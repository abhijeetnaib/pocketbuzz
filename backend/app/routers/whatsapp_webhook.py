"""
WhatsApp Webhook - Receives incoming messages and sends auto-replies
"""
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse
import logging
import json
from pathlib import Path
import httpx

from app.config import get_settings
from app.services.ai_engine import ai_engine

settings = get_settings()
router = APIRouter()
logger = logging.getLogger(__name__)

# Verification token for WhatsApp webhook setup
VERIFY_TOKEN = "pocketbuzz_webhook_verify_token"


@router.get("/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    WhatsApp webhook verification endpoint.
    Meta sends a GET request to verify the webhook.
    """
    if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully")
        return PlainTextResponse(content=hub_challenge)
    
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/whatsapp")
async def receive_whatsapp_message(request: Request):
    """
    Receives incoming WhatsApp messages and sends auto-replies.
    """
    try:
        body = await request.json()
        logger.info(f"Received WhatsApp webhook: {body}")
        
        # Extract message details
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        for message in messages:
            from_number = message.get("from")
            msg_type = message.get("type")
            
            if msg_type == "text":
                text = message.get("text", {}).get("body", "").lower()
                
                # Load menu from extracted_menu.json
                menu_text = ""
                try:
                    menu_path = Path(__file__).resolve().parent.parent.parent / "extracted_menu.json"
                    if menu_path.exists():
                        with open(menu_path, "r") as f:
                            menu_data = json.load(f)
                            menu_text = "\n".join([f"- {item}: Rs {price}" for item, price in menu_data.items()])
                    else:
                        logger.warning(f"Menu file not found at {menu_path}")
                        menu_text = "Menu currently unavailable."
                except Exception as ex:
                    logger.error(f"Error loading menu: {ex}")
                    menu_text = "Menu currently unavailable."

                # Use OpenAI to generate a human-like response
                system_prompt = f"""
                You are the friendly AI Manager of 'Sarang', an Indian restaurant.
                Your goal is to be helpful, warm, and encourage orders.
                
                Restaurant Info:
                - Name: Sarang
                - Full Menu:
                {menu_text}
                - Special Offer: 10% off if they order now via phone
                - Contact: 9766912776 for orders
                
                Guidelines:
                - Keep replies short (under 50 words) and conversational (Hinglish allowed).
                - Don't just list the menu, recommend items based on what they ask.
                - If they want to order, ask for their address or tell them to call.
                - Be witty and use emojis 🍛🥘.
                """
                
                reply_text = "Sorry boss, thoda busy hoon! 😅 Call karein: 9766912776"
                
                try:
                    # Check if OpenAI client is available
                    if ai_engine.openai_client:
                        response = ai_engine.openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": text}
                            ],
                            max_tokens=100
                        )
                        reply_text = response.choices[0].message.content
                    else:
                        logger.warning("OpenAI client not initialized")
                        reply_text = "Namaste from Sarang! 🙏 Call us at 9766912776 for orders."
                        
                except Exception as ai_error:
                    logger.error(f"OpenAI Error: {ai_error}")

                await send_auto_reply(from_number, reply_text)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        return {"status": "error", "message": str(e)}


async def send_auto_reply(to_phone: str, message: str):
    """Send an auto-reply message via WhatsApp"""
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {"body": message}
    }
    
    url = f"https://graph.facebook.com/v22.0/{settings.whatsapp_phone_number_id}/messages"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {settings.whatsapp_access_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            logger.info(f"Auto-reply sent to {to_phone}: {response.status_code}")
            return response.status_code == 200
    except Exception as ex:
        logger.error(f"Failed to send auto-reply: {ex}")
        return False
