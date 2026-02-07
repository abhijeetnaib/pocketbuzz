"""
WhatsApp Business API Integration
Sends campaign messages via Meta Cloud API.
"""
import httpx
from typing import List, Optional

from app.config import get_settings

settings = get_settings()

WHATSAPP_API_URL = "https://graph.facebook.com/v22.0"


async def send_campaign_blast(
    restaurant_id: str,
    phones: List[str],
    image_url: str,
    caption: str
) -> dict:
    """
    Send a campaign message to multiple recipients via WhatsApp.
    
    Args:
        restaurant_id: For logging/tracking
        phones: List of phone numbers (+91 format)
        image_url: URL of the campaign poster
        caption: Marketing message text
        
    Returns:
        Summary of send results
    """
    if not settings.whatsapp_access_token or not settings.whatsapp_phone_number_id:
        return {
            "status": "error",
            "message": "WhatsApp API not configured",
            "sent": 0,
            "failed": len(phones)
        }
    
    results = {"sent": 0, "failed": 0, "errors": []}
    
    for phone in phones:
        try:
            success = await send_single_message(
                to_phone=phone,
                image_url=image_url,
                caption=caption
            )
            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(str(e))
    
    return results


async def send_single_message(
    to_phone: str,
    image_url: str,
    caption: str
) -> bool:
    """
    Send a single WhatsApp message with image and caption.
    
    Uses the WhatsApp Business API to send a media message.
    """
    # Clean phone number
    phone = to_phone.replace("+", "").replace(" ", "").replace("-", "")
    if not phone.startswith("91"):
        phone = f"91{phone}"
    
    # Build message payload
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{WHATSAPP_API_URL}/{settings.whatsapp_phone_number_id}/messages",
                headers={
                    "Authorization": f"Bearer {settings.whatsapp_access_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"WhatsApp API error: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"WhatsApp send error: {e}")
        return False


async def send_notification(
    to_phone: str,
    message: str,
    magic_link: Optional[str] = None
) -> bool:
    """
    Send a text notification to the restaurant owner.
    Used for alerting them about new campaign suggestions.
    """
    phone = to_phone.replace("+", "").replace(" ", "").replace("-", "")
    if not phone.startswith("91"):
        phone = f"91{phone}"
    
    # Build full message with magic link
    full_message = message
    if magic_link:
        full_message += f"\n\n👉 Dekho yahan: {magic_link}"
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "text",
        "text": {
            "preview_url": True,
            "body": full_message
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{WHATSAPP_API_URL}/{settings.whatsapp_phone_number_id}/messages",
                headers={
                    "Authorization": f"Bearer {settings.whatsapp_access_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            return response.status_code == 200
                
    except Exception as e:
        print(f"WhatsApp notification error: {e}")
        return False
