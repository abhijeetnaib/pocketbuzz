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
            # Generate a detailed photographic description using LLM
            # Focus on anatomy, lighting, and authentic regional context
            visual_prompt_helper = f"""Describe a professional commercial food photograph of: {item_name or 'a delicious Indian dish'}.
            Campaign Offer: "{caption}"
            
            DIRECTIONS:
            - If it's Wada Pav: Describe it as a rustic deep-fried yellow potato fritter inside a square, hand-pulled soft white 'pav' (square bread). NOT a burger bun.
            - If it's Chicken Malvani: Describe it as a dark-brown, thick coconut-based curry with visible spices, served in a traditional Maharashtrian stainless steel thali with soft Bhakri or Kombdi Vade.
            - Setting: Authentic context (vibrant Indian street or a rustic-modern Maharashtrian restaurant).
            - Details: Steam rising, fresh coriander garnish, dramatic warm lighting, 8k resolution.
            
            Return ONLY a single paragraph of descriptive prose for a professional photographer."""
            
            visual_description = ""
            if self.openai_client:
                try:
                    llm_response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "You are a specialist in culinary anatomy and lighting. You describe food by its shapes, textures, and traditional serving style to ensure 100% accuracy."},
                                  {"role": "user", "content": visual_prompt_helper}],
                        max_tokens=400
                    )
                    visual_description = llm_response.choices[0].message.content.strip()
                except Exception as e:
                    print(f"Error generating visual prompt: {e}")
            
            if not visual_description:
                visual_description = f"Professional commercial food photography of {item_name or 'Indian food'}, highly appetizing, regional authentic presentation."

            prompt = f"{visual_description} Photorealistic, cinematic lighting, food advertising style, high fidelity, 16k."

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Shifting back to Flux Pro 1.1 but FORCING JPEG for WhatsApp compatibility
                model_endpoint = "https://fal.run/fal-ai/flux-pro/v1.1" 
                
                response = await client.post(
                    model_endpoint,
                    headers={
                        "Authorization": f"Key {settings.fal_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "prompt": prompt,
                        "image_size": "landscape_16_9",
                        "output_format": "jpeg"  # Crucial for WhatsApp delivery!
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
