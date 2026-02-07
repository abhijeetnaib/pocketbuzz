"""
SendGrid Inbound Parse Webhook
Receives and processes POS report emails from restaurants.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import io

from app.services.parser import parse_pos_email
from app.services.ingestion import save_records
from app.db.supabase import get_supabase_client

router = APIRouter()


@router.post("")
async def receive_email(
    from_: str = Form(..., alias="from"),
    to: str = Form(...),
    subject: str = Form(default=""),
    text: str = Form(default=""),
    html: str = Form(default=""),
    attachments: Optional[int] = Form(alias="attachments", default=0),
    attachment1: Optional[UploadFile] = File(default=None),
):
    """
    SendGrid Inbound Parse webhook endpoint.
    
    Receives emails sent to [restaurant-id]@parse.pocketbuzz.in
    and extracts customer data from attached POS reports.
    """
    try:
        # Extract restaurant ID from the email address
        # Format: cafe123@parse.pocketbuzz.in
        to_address = to.lower()
        if "@parse.pocketbuzz.in" not in to_address:
            raise HTTPException(status_code=400, detail="Invalid recipient address")
        
        restaurant_email = to_address.split(",")[0].strip()
        restaurant_id = _extract_restaurant_id(restaurant_email)
        
        if not restaurant_id:
            raise HTTPException(status_code=400, detail="Could not identify restaurant")
        
        # Process attachments (PDF reports)
        records = []
        
        if attachment1 and attachment1.filename:
            content = await attachment1.read()
            if attachment1.filename.lower().endswith(".pdf"):
                records = parse_pos_email(
                    pdf_content=io.BytesIO(content),
                    email_body=text or html,
                    source="email"
                )
        
        # If no PDF, try to parse from email body
        if not records and (text or html):
            records = parse_pos_email(
                pdf_content=None,
                email_body=text or html,
                source="email"
            )
        
        # Save valid records to database
        if records:
            saved_count = await save_records(restaurant_id, records)
            return {
                "status": "success",
                "restaurant_id": restaurant_id,
                "records_processed": len(records),
                "records_saved": saved_count
            }
        
        return {
            "status": "success",
            "restaurant_id": restaurant_id,
            "records_processed": 0,
            "message": "No valid data found in email"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error but return 200 to prevent SendGrid retries
        print(f"Webhook processing error: {e}")
        return {"status": "error", "message": str(e)}


def _extract_restaurant_id(email: str) -> Optional[str]:
    """Extract restaurant identifier from email address."""
    try:
        local_part = email.split("@")[0]
        return local_part
    except Exception:
        return None


@router.post("/test")
async def test_webhook():
    """Test endpoint to verify webhook is accessible."""
    return {"status": "ok", "message": "Webhook endpoint is working"}
