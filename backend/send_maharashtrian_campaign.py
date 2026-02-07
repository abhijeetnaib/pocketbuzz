
import asyncio
import httpx
from app.db.supabase import get_supabase_client
from app.services.ai_engine import generate_campaign_content

async def run_maharashtrian_campaign():
    client = get_supabase_client()
    restaurant_id = '4c01898c-e005-4311-a6c7-f42c444022a9'
    
    # 1. Generate AI ID Content for Sukha Mutton
    print('Generating campaign for Sukha Mutton...')
    content = await generate_campaign_content(
        insight_text='Sukha Mutton is the ultimate spicy treat for meat lovers!',
        restaurant_name='Sarang',
        strategy_type='BEST_SELLER',
        item_name='Sukha Mutton'
    )
    
    print(f'Caption: {content["caption"]}')
    print(f'Image: {content["image_url"]}')
    
    # 2. Save campaign
    res = client.table('campaign_suggestions').insert({
        'restaurant_id': restaurant_id,
        'strategy_type': 'BEST_SELLER',
        'insight_text': 'Saoji Chicken Curry promo',
        'generated_image_url': content['image_url'],
        'generated_caption': content['caption'],
        'status': 'APPROVED' # Auto-approve for this test
    }).execute()
    
    campaign_id = res.data[0]['id']
    approval_link = f'http://localhost:3000/campaign/{campaign_id}'
    
    # 3. Send to specific numbers
    phones = ['919766912776', '917276006234']
    
    url = 'https://graph.facebook.com/v22.0/1006215249236308/messages'
    token = 'EAAUbyAsg8yQBQkbiKVCDJ5eMd9A5BbQpkKIMPkmzj1RZBZBPWorMnUZBd1qqXlyX6sieZBWLoonbMGbKb7SjsvB7njMeZBfDb5p61PySdq3YkXZBIdecL6MD0YMn9lqTSla3dwzIYI0iDvvtaZAW4xt747ASv3uWf74rJH9LP9FBS43sUIVfG4m1z1TPtTDcsavK5zQpj0fpjSvtFbNZAaIoxTZCFfKfUGHTMspsZD'
    
    async with httpx.AsyncClient(timeout=30.0) as http:
        for phone in phones:
            print(f'Sending to {phone}...')
            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': phone,
                'type': 'image',
                'image': {
                    'link': content['image_url'],
                    'caption': f'{content["caption"]}\n\n👇 Order Now:\n{approval_link}'
                }
            }
            
            resp = await http.post(
                url,
                headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                json=payload
            )
            print(f'Status: {resp.status_code}')
            if resp.status_code != 200:
                print(f'Error: {resp.text}')

if __name__ == "__main__":
    asyncio.run(run_maharashtrian_campaign())
