"""
Mock SendGrid Endpoint for Local Testing
Simulates email ingestion without actual SendGrid setup.
"""
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import io

from app.services.parser import parse_pos_email
from app.services.ingestion import save_records

router = APIRouter()


# Sample Petpooja-style invoice data for testing
SAMPLE_PETPOOJA_DATA = """
PETPOOJA DAILY SALES REPORT
Restaurant: Test Cafe Mumbai
Date: 2026-02-07
GSTIN: 27AABCT1234L1ZH

==================================================
ORDER SUMMARY
==================================================

Order #1001 - Dine-In (Table 5)
Customer: Rahul Sharma
Mobile: 9876543210
Items: Butter Chicken (1), Garlic Naan (2), Dal Makhani (1)
Amount: Rs. 850
Time: 12:30 PM

Order #1002 - Dine-In (Table 3)
Customer: Priya Singh  
Mobile: 8765432109
Items: Paneer Tikka (1), Roti (4), Raita (1)
Amount: Rs. 520
Time: 1:15 PM

Order #1003 - Swiggy Delivery
Customer: Swiggy Customer
Mobile: 7777000001
Items: Biryani (2)
Amount: Rs. 680
Time: 1:45 PM

Order #1004 - Dine-In (Table 7)
Customer: Amit Verma
Mobile: 9988776655
Items: Chicken Biryani (1), Butter Chicken (1), Naan (3)
Amount: Rs. 920
Time: 2:00 PM

Order #1005 - Zomato Delivery
Customer: Zomato Customer
Mobile: 8888000002
Items: Thali (1)
Amount: Rs. 350
Time: 2:30 PM

Order #1006 - Dine-In (Table 2)
Customer: Neha Gupta
Mobile: 7766554433
Items: Butter Chicken (1), Jeera Rice (1), Lassi (2)
Amount: Rs. 650
Time: 3:00 PM

Order #1007 - Dine-In (Table 4)
Customer: Vikram Reddy
Mobile: 9123456789
Items: Tandoori Chicken (1), Butter Naan (2), Dal Tadka (1)
Amount: Rs. 780
Time: 4:30 PM

Order #1008 - Dine-In (Table 1)
Customer: Sneha Patel
Mobile: 8899001122
Items: Paneer Butter Masala (1), Butter Chicken (1), Roti (4)
Amount: Rs. 720
Time: 5:45 PM

==================================================
DAILY TOTALS
==================================================
Total Dine-In Orders: 6
Total Delivery Orders: 2
Total Revenue: Rs. 5,470
Top Seller: Butter Chicken (5 orders)
"""


@router.post("/ingest-sample")
async def ingest_sample_data(restaurant_id: str):
    """
    Ingest sample Petpooja data for testing.
    This simulates what would happen when a real email comes in.
    """
    # Parse the sample data
    records = parse_pos_email(
        pdf_content=None,
        email_body=SAMPLE_PETPOOJA_DATA,
        source="Dine-In"
    )
    
    # Save to database
    saved_count = await save_records(restaurant_id, records)
    
    return {
        "status": "success",
        "message": "Sample Petpooja data ingested",
        "records_parsed": len(records),
        "records_saved": saved_count,
        "note": "Zomato/Swiggy orders were filtered out automatically"
    }


@router.post("/simulate-email")
async def simulate_email(
    restaurant_id: str = Form(...),
    email_body: str = Form(default=SAMPLE_PETPOOJA_DATA),
):
    """
    Simulate receiving an email from SendGrid.
    Use this to test the full ingestion flow.
    """
    records = parse_pos_email(
        pdf_content=None,
        email_body=email_body,
        source="Dine-In"
    )
    
    saved_count = await save_records(restaurant_id, records)
    
    return {
        "status": "success",
        "restaurant_id": restaurant_id,
        "records_processed": len(records),
        "records_saved": saved_count
    }
