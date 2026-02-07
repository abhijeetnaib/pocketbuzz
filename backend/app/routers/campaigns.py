"""
Campaign Management Router
CRUD operations for AI-generated marketing campaigns.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID

from app.models.schemas import (
    Campaign,
    CampaignCreate,
    CampaignUpdate,
    CampaignUpdate,
    CampaignApproval,
    CampaignRegenerate
)
from app.db.supabase import get_supabase_client
from app.services.whatsapp import send_campaign_blast

router = APIRouter()


@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: UUID):
    """Get a specific campaign by ID."""
    supabase = get_supabase_client()
    
    result = supabase.table("campaign_suggestions").select("*").eq(
        "id", str(campaign_id)
    ).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return result.data


@router.get("/suggestions", response_model=List[dict])
async def get_campaign_suggestions(restaurant_id: UUID):
    """
    Get AI-generated campaign suggestions based on restaurant data.
    """
    from app.services.analyzer import analyze_restaurant
    
    insights = await analyze_restaurant(str(restaurant_id))
    
    # Convert dataclass objects to dicts for JSON response
    return [
        {
            "strategy_type": i.strategy_type.value,
            "insight_text": i.insight_text,
            "target_data": i.target_data,
            "item_name": i.target_data.get("item") # Extract item name if available
        }
        for i in insights
    ]

@router.get("/restaurant/{restaurant_id}", response_model=List[Campaign])
async def get_restaurant_campaigns(
    restaurant_id: UUID,
    status: Optional[str] = None
):
    """Get all campaigns for a restaurant."""
    supabase = get_supabase_client()
    
    query = supabase.table("campaign_suggestions").select("*").eq(
        "restaurant_id", str(restaurant_id)
    )
    
    if status:
        query = query.eq("status", status)
    
    result = query.order("created_at", desc=True).execute()
    return result.data


@router.post("/{campaign_id}/approve")
async def approve_campaign(campaign_id: UUID, approval: CampaignApproval):
    """
    Approve and optionally modify a campaign before sending.
    """
    supabase = get_supabase_client()
    
    # Get the campaign
    campaign = supabase.table("campaign_suggestions").select("*").eq(
        "id", str(campaign_id)
    ).single().execute()
    
    if not campaign.data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.data["status"] != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=f"Campaign is already {campaign.data['status']}"
        )
    
    # Update with approved content
    update_data = {
        "status": "APPROVED",
        "approved_at": "now()"
    }
    
    if approval.modified_caption:
        update_data["generated_caption"] = approval.modified_caption
    
    if approval.modified_image_url:
        update_data["generated_image_url"] = approval.modified_image_url
    
    supabase.table("campaign_suggestions").update(update_data).eq(
        "id", str(campaign_id)
    ).execute()
    
    return {"status": "approved", "campaign_id": str(campaign_id)}


@router.post("/{campaign_id}/send")
async def send_campaign(campaign_id: UUID):
    """
    Send an approved campaign via WhatsApp.
    """
    supabase = get_supabase_client()
    
    # Get the campaign
    campaign = supabase.table("campaign_suggestions").select("*").eq(
        "id", str(campaign_id)
    ).single().execute()
    
    if not campaign.data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.data["status"] not in ["APPROVED", "PENDING"]:
        raise HTTPException(
            status_code=400,
            detail=f"Campaign cannot be sent (status: {campaign.data['status']})"
        )
    
    # Get target audience
    target_phones = await _get_target_audience(
        campaign.data["restaurant_id"],
        campaign.data.get("target_audience", {})
    )
    
    if not target_phones:
        raise HTTPException(status_code=400, detail="No target audience found")
    
    # Send via WhatsApp
    result = await send_campaign_blast(
        restaurant_id=campaign.data["restaurant_id"],
        phones=target_phones,
        image_url=campaign.data["generated_image_url"],
        caption=campaign.data["generated_caption"]
    )
    
    # Update status
    supabase.table("campaign_suggestions").update({
        "status": "SENT",
        "sent_at": "now()"
    }).eq("id", str(campaign_id)).execute()
    
    return {
        "status": "sent",
        "campaign_id": str(campaign_id),
        "recipients": len(target_phones),
        "result": result
    }


@router.post("/{campaign_id}/regenerate-image")
async def regenerate_campaign_image(campaign_id: UUID, request: CampaignRegenerate):
    """
    Regenerate the poster image for a campaign.
    """
    from app.services.ai_engine import ai_engine
    
    supabase = get_supabase_client()
    
    # Get campaign details
    campaign = supabase.table("campaign_suggestions").select("*").eq("id", str(campaign_id)).single().execute()
    if not campaign.data:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    data = campaign.data
    
    # Determine item name from insight text or use general term
    # Check for keywords in insight text to guess the item
    insight = data.get("insight_text", "").lower()
    item_name = "delicious food"
    
    if "saoji" in insight:
        item_name = "Saoji Chicken Curry"
    elif "butter chicken" in insight:
        item_name = "Butter Chicken"
    elif "paneer" in insight:
        item_name = "Paneer Tikka"
    elif "biryani" in insight:
        item_name = "Biryani"
        
    # Generate new image
    new_image_url = await ai_engine.generate_poster(
        caption=data.get("generated_caption", ""),
        restaurant_name="Sarang",
        item_name=item_name,
        manual_prompt=request.manual_prompt
    )
    
    # Update database
    supabase.table("campaign_suggestions").update({
        "generated_image_url": new_image_url
    }).eq("id", str(campaign_id)).execute()
    
    return {"status": "success", "image_url": new_image_url}


from datetime import datetime, timedelta

async def _get_target_audience(
    restaurant_id: str,
    target_config: dict
) -> List[str]:
    """Get list of phone numbers based on target audience config."""
    supabase = get_supabase_client()
    
    # Default: last 30 days dine-in customers
    days = target_config.get("days", 30)
    
    # Calculate cutoff date in Python
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Using gte (Greater Than or Equal)
    result = supabase.table("universal_records").select("client_phone").eq(
        "restaurant_id", restaurant_id
    ).eq("source", "Dine-In").gte(
        "visit_date", cutoff_date
    ).execute()
    
    # Deduplicate phone numbers
    phones = sorted(list(set([r["client_phone"] for r in result.data if r.get("client_phone")])))
    return phones


@router.post("/", response_model=Campaign)
async def create_campaign(campaign_data: CampaignCreate):
    """
    Create a new campaign suggestion manually.
    """
    from app.services.ai_engine import generate_campaign_content
    supabase = get_supabase_client()
    
    # Generate Content
    content = await generate_campaign_content(
        insight_text=campaign_data.insight_text,
        restaurant_name="Sarang", # Hardcoded for demo/MVP
        strategy_type=campaign_data.strategy_type,
        item_name=campaign_data.item_name
    )
    
    # Save to DB
    try:
        data_to_insert = {
            "restaurant_id": str(campaign_data.restaurant_id),
            "strategy_type": campaign_data.strategy_type.value if hasattr(campaign_data.strategy_type, 'value') else campaign_data.strategy_type,
            "insight_text": campaign_data.insight_text,
            "generated_image_url": content["image_url"],
            "generated_caption": content["caption"],
            "status": "PENDING",
            "target_audience": {"days": 30} # Default
        }
        new_campaign = supabase.table("campaign_suggestions").insert(data_to_insert).execute()
    except Exception as e:
        print(f"Campaign creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    if not new_campaign.data:
         raise HTTPException(status_code=500, detail="Failed to create campaign - no data returned from DB")
         
    return new_campaign.data[0]

@router.post("/{campaign_id}/reject")
async def reject_campaign(campaign_id: UUID):
    """Reject/dismiss a campaign suggestion."""
    supabase = get_supabase_client()
    
    supabase.table("campaign_suggestions").update({
        "status": "FAILED"  # Using FAILED as rejected status
    }).eq("id", str(campaign_id)).execute()
    
    return {"status": "rejected", "campaign_id": str(campaign_id)}
