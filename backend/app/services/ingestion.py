"""
Data Ingestion Service
Saves parsed records to Supabase with validation and deduplication.
"""
from typing import List, Dict, Any
from datetime import date

from app.db.supabase import get_supabase_client


async def save_records(
    restaurant_id: str,
    records: List[Dict[str, Any]]
) -> int:
    """
    Save customer records to the universal_records table.
    
    Args:
        restaurant_id: UUID of the restaurant
        records: List of parsed customer records
        
    Returns:
        Number of records successfully saved
    """
    supabase = get_supabase_client()
    saved_count = 0
    
    for record in records:
        try:
            # Format phone number with +91 prefix
            phone = record.get("phone", "")
            if len(phone) == 10:
                phone = f"+91{phone}"
            
            # Prepare record for insertion
            db_record = {
                "restaurant_id": restaurant_id,
                "client_phone": phone,
                "client_name": record.get("name"),
                "source": record.get("source", "Dine-In"),
                "item_ordered": record.get("items"),
                "bill_amount": record.get("bill_amount"),
                "visit_date": date.today().isoformat()
            }
            
            # Insert into database
            supabase.table("universal_records").insert(db_record).execute()
            saved_count += 1
            
        except Exception as e:
            # Log error but continue with other records
            print(f"Error saving record: {e}")
            continue
    
    return saved_count


async def get_unique_customers(
    restaurant_id: str,
    days: int = 30,
    source: str = "Dine-In"
) -> int:
    """Get count of unique customers in the given period."""
    supabase = get_supabase_client()
    
    result = supabase.rpc(
        "count_unique_customers",
        {
            "p_restaurant_id": restaurant_id,
            "p_days": days,
            "p_source": source
        }
    ).execute()
    
    return result.data if result.data else 0
