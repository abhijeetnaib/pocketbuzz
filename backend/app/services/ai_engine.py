"""
AI Creative Engine
Generates marketing copy (GPT-4o-mini) and visuals (Fal.ai Flux.1).
"""
import httpx
from typing import Optional
from openai import OpenAI

from app.config import get_settings

settings = get_settings()


class AIEngine:
    """AI-powered content generation for marketing campaigns."""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    
    async def generate_campaign(
        self,
        insight_text: str,
        restaurant_name: str,
        strategy_type: str,
        item_name: Optional[str] = None
    ) -> dict:
        """
        Generate complete campaign assets: poster image + caption.
        
        Args:
            insight_text: The analytical insight (e.g., "Tuesday is slow")
            restaurant_name: Name of the restaurant
            strategy_type: Type of campaign (BEST_SELLER, SLOW_DAY, etc.)
            item_name: Specific menu item if applicable
            
        Returns:
            dict with 'image_url' and 'caption'
        """
        # Generate caption first
        caption = await self.generate_caption(
            insight_text=insight_text,
            restaurant_name=restaurant_name,
            strategy_type=strategy_type,
            item_name=item_name
        )
        
        # Generate poster image
        image_url = await self.generate_poster(
            caption=caption,
            restaurant_name=restaurant_name,
            item_name=item_name
        )
        
        return {
            "caption": caption,
            "image_url": image_url
        }
    
    async def generate_caption(
        self,
        insight_text: str,
        restaurant_name: str,
        strategy_type: str,
        item_name: Optional[str] = None
    ) -> str:
        """
        Generate WhatsApp-friendly Hinglish caption using GPT-4o-mini.
        
        Requirements from spec:
        - Hinglish (Hindi + English mix)
        - Short (under 20 words)
        - WhatsApp friendly (emojis welcome)
        """
        if not self.openai_client:
            return self._get_fallback_caption(strategy_type, restaurant_name, item_name)
        
        prompt = f"""You are a creative marketer for Indian restaurants.
Generate a WhatsApp marketing caption for {restaurant_name}.

Context: {insight_text}
Strategy: {strategy_type}
{"Featured Item: " + item_name if item_name else ""}

STRICT REQUIREMENTS:
1. Write in Hinglish (mix of Hindi and English, use Roman script)
2. Maximum 20 words
3. Include 1-2 relevant emojis
4. Must have a clear call-to-action
5. Sound casual and friendly, like a text from a friend
6. Include urgency (limited time, today only, etc.)

Examples of good Hinglish captions:
- "Aaj ka special! 🔥 Butter Chicken pe flat 20% off, sirf aaj. Kab aa rahe?"
- "Bhai Tuesday ko kuch plan nahi? Humara Happy Hour try karo! 🍺 4-7pm"
- "Miss kar rahe ho? 😢 Wapas aao, pehli visit pe 15% off gift hai tumhare liye!"

Generate ONE caption only, no quotes around it:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._get_fallback_caption(strategy_type, restaurant_name, item_name)
    
    async def generate_poster(
        self,
        caption: str,
        restaurant_name: str,
        item_name: Optional[str] = None,
        manual_prompt: Optional[str] = None
    ) -> str:
        """
        Generate marketing poster using Fal.ai Flux.1.
        """
        if not settings.fal_api_key:
            return self._get_placeholder_image()
        
        # If manual prompt is provided, use it directly (with some style enforcing)
        if manual_prompt:
            prompt = f"""{manual_prompt}
            Professional food photography, cinematic lighting, 8K quality.
            Restaurant ambiance in background.
            Photorealistic style."""
        else:
            # Build the image prompt
            food_subject = item_name if item_name else "delicious Indian food spread"
            
            # Custom visual descriptors for specific cuisines
            visual_style = ""
            if "saoji" in food_subject.lower():
                visual_style = "Authentic Nagpur Saoji style, dark red spicy gravy with floating oil (tarri), spicy and rich texture, freshly chopped coriander garnish."
            elif "biryani" in food_subject.lower():
                visual_style = "Layered basmati rice, saffron strands, caramelized onions, served in a clay pot (handi)."
            elif "sukha" in food_subject.lower() or "sukka" in food_subject.lower() or "dry" in food_subject.lower():
                visual_style = "Dry spicy masala fry, coated with rich dark roasted coconut spices, garnished with curry leaves and coriander, served with slice of lime and onion rings."
                
            prompt = f"""Professional food photography of {food_subject} at an Indian restaurant.
            {visual_style}
            Cinematic lighting, shallow depth of field, steam rising from hot food.
            Warm golden tones, 8K quality, appetizing presentation.
            Dark moody background with dramatic side lighting.
            Restaurant ambiance visible in soft bokeh background.
            Photorealistic, commercial food photography style."""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://fal.run/fal-ai/flux/schnell",
                    headers={
                        "Authorization": f"Key {settings.fal_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "prompt": prompt,
                        "image_size": "landscape_16_9",
                        "num_images": 1,
                        "enable_safety_checker": True
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    images = data.get("images", [])
                    if images:
                        return images[0].get("url", self._get_placeholder_image())
                
                print(f"Fal.ai API error: {response.status_code} - {response.text}")
                return self._get_placeholder_image()
                
        except Exception as e:
            print(f"Fal.ai request error: {e}")
            return self._get_placeholder_image()
    
    def _get_fallback_caption(
        self,
        strategy_type: str,
        restaurant_name: str,
        item_name: Optional[str]
    ) -> str:
        """Fallback captions when API is unavailable."""
        captions = {
            "BEST_SELLER": f"🔥 {item_name or 'Humara special'} sab ka favorite hai! Aao try karo at {restaurant_name}!",
            "SLOW_DAY": f"🎉 Mid-week special at {restaurant_name}! Extra discounts sirf aaj. Miss mat karna!",
            "CHURN_RECOVERY": f"😊 Bahut din ho gaye! {restaurant_name} pe wapas aao, special surprise hai tumhare liye!",
            "DEAD_STOCK": f"🆕 Something new to try at {restaurant_name}! Pehle 20 orders pe special price!"
        }
        return captions.get(strategy_type, f"Visit {restaurant_name} for amazing food! 😋")
    
    def _get_placeholder_image(self) -> str:
        """Placeholder image URL when generation fails."""
        return "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800"


# Global instance
ai_engine = AIEngine()


async def generate_campaign_content(
    insight_text: str,
    restaurant_name: str,
    strategy_type: str,
    item_name: Optional[str] = None
) -> dict:
    """Convenience function to generate campaign content."""
    return await ai_engine.generate_campaign(
        insight_text=insight_text,
        restaurant_name=restaurant_name,
        strategy_type=strategy_type,
        item_name=item_name
    )
