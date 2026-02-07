
import asyncio
import httpx
from app.db.supabase import get_supabase_client
from app.services.ai_engine import generate_campaign_content

async def run_full_flow():
    client = get_supabase_client()
    restaurant_id = '4c01898c-e005-4311-a6c7-f42c444022a9'
    
    print('1. Generating AI content for Sarang (Butter Chicken)...')
    content = await generate_campaign_content(
        insight_text='Butter Chicken is trending with 67 orders!',
        restaurant_name='Sarang',
        strategy_type='BEST_SELLER',
        item_name='Butter Chicken'
    )
    
    print(f'   Caption: "{content["caption"]}"')
    print(f'   Image: {content["image_url"]}')
    
    # Save campaign
    res = client.table('campaign_suggestions').insert({
        'restaurant_id': restaurant_id,
        'strategy_type': 'BEST_SELLER',
        'insight_text': 'Butter Chicken is trending with 67 orders!',
        'generated_image_url': content['image_url'],
        'generated_caption': content['caption'],
        'status': 'PENDING'
    }).execute()
    
    campaign_id = res.data[0]['id']
    approval_link = f'http://localhost:3000/campaign/{campaign_id}'
    print(f'   Campaign ID: {campaign_id}')
    
    print('2. Sending WhatsApp notification...')
    payload = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': '919766912776',
        'type': 'image',
        'image': {
            'link': content['image_url'],
            'caption': f'{content["caption"]}\n\n👇 *Approve Campaign Here:*\n{approval_link}'
        }
    }
    
    url = 'https://graph.facebook.com/v22.0/1006215249236308/messages'
    token = 'EAAUbyAsg8yQBQpummrJ7kVAz40iWkCvThN2xFoBLKEr1ZAcbvBjjX6NtJ50K5UAUSPd1BsUyWYDl81GD0KeYjL51on3QVD5rRzwiuGPmf2jIHcLI5qe2inAVxZCsupe9inIVrZBORGbro4BKvQkDlNKtxZCqnl4RjEYx4mLwnlXE2GCi0WCziDAw6GdSFifZBzQ7cL4jB8MDvhJlfxcq27G4SSW2LxmYwFUJ0TZAnFE1og2An5KnsxwZBxlMZBQEKASGlwMKEZA7qkk226DoWepZAD'
    
    async with httpx.AsyncClient(timeout=30.0) as http:
        resp = await http.post(
            url,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json=payload
        )
        print(f'   WhatsApp Status: {resp.status_code}')

if __name__ == "__main__":
    asyncio.run(run_full_flow())
