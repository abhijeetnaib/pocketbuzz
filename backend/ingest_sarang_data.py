
import asyncio
import random
from datetime import date, timedelta
from app.db.supabase import get_supabase_client

# Sarang Restaurant (Authentic Maharashtrian Menu from Images)
MENU = {
    "Tawa Fry Pomfret": 700,
    "Tawa Fry Prawns": 680,
    "Fish Koliwada": 680,
    "Prawns Koliwada": 680,
    "Zunka": 200,
    "Pithla": 200,
    "Bharli Masala Vangi": 250,
    "Shev Bhaji": 250,
    "Patodi Rassa": 250,
    "Chana Rassa": 250,
    "Wangyacha Bharit": 250,
    "Poli": 15,
    "Jowari Bhakri": 40,
    "Bajri Bhakri": 40,
    "Tandul Bhakri": 45,
    "Dupodi": 100,
    "Telache Parathe": 100,
    "Ghavan": 100,
    "Poori Basket": 150,
    "Steam Rice": 200,
    "Jeera Rice": 250,
    "Jeera Garlic Rice": 250,
    "Masale Bhat": 300,
    "Fodnicha Waran": 200,
    "Dal Fry": 250,
    "Dal Tadka": 250,
    "Dal Bhaji": 290,
    "Grated Kakdi Koshimbir": 80,
    "Gajarachi Koshimbir": 80,
    "Dahi Kakdi Koshimbir": 80,
    "Masala Papad": 100,
    "Papad Basket": 150,
    "Tomato Saar": 200,
    "Chicken Alani": 250,
    "Bhajji Platter": 200,
    "Mini Batata Vada": 220,
    "Vangyachi Kaap": 220,
    "Matar Pattice": 250,
    "Sukha Chicken": 400,
    "Khardha Chicken": 400,
    "Mutton Ukad": 400,
    "Sukha Mutton": 580,
    "Khema Pattice": 580,
    "Kharda Chicken": 400
}

NAMES = [
    "Rahul Sharma", "Amit Patil", "Priya Deshmukh", "Sandeep Gupta", "Neha Verma",
    "Vikram Singh", "Anjali Rao", "Rohan Mehta", "Kavita Joshi", "Rajesh Kumar",
    "Sneha Patel", "Arjun Nair", "Pooja Reddy", "Manish Tiwari", "Divya Agarwal"
]

PHONES = [
    "+919876543210", "+919988776655", "+919123456789", "+919000000000", "+919766912776"
]

async def ingest_data():
    client = get_supabase_client()
    restaurant_id = '4c01898c-e005-4311-a6c7-f42c444022a9'
    
    print("Creating mock data using Menu from Trimurti Nagar...")
    
    records = []
    
    # Generate 1000 orders
    for i in range(1000):
        # Weighted random choice for items (make some more popular)
        item_name = random.choices(list(MENU.keys()), k=1)[0]
        price = MENU[item_name]
        
        # Quantity usually 1 or 2
        qty = random.choices([1, 2, 3], weights=[70, 20, 10], k=1)[0]
        total_bill = price * qty
        
        # Random date in last 3 months
        days_ago = random.randint(0, 90)
        visit_date = (date.today() - timedelta(days=days_ago)).isoformat()
        
        # Random customer
        name = random.choice(NAMES)
        phone = random.choice(PHONES)
        
        # If it's your number, use it more often for testing
        if random.random() < 0.1:
            phone = "+919766912776"
            name = "Abhijeet (Test)"
            
        record = {
            'restaurant_id': restaurant_id,
            'client_phone': phone,
            'client_name': name,
            'source': 'Dine-In',
            'item_ordered': item_name,
            'bill_amount': total_bill,
            'visit_date': visit_date
        }
        records.append(record)

    # Insert in batches
    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        client.table('universal_records').insert(batch).execute()
        print(f"Inserted batch {i//batch_size + 1}/{len(records)//batch_size}")
        
    print("Done! 1000 authentic menu orders inserted.")

if __name__ == "__main__":
    asyncio.run(ingest_data())
