
import base64
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_menu(image_path):
    base64_image = encode_image(image_path)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract the menu items and prices (in INR) from this image. Return ONLY a JSON object where keys are item names and values are prices (integer). Ignore headers or non-food text. Example: {\"Butter Chicken\": 350, \"Naan\": 40}"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/webp;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )
    
    print(f"Processed {image_path}")
    return response.choices[0].message.content

def main():
    image_files = [
        "c:\\Users\\abhis\\OneDrive\\Desktop\\pocketbuzz\\2026-01-31.webp",
        "c:\\Users\\abhis\\OneDrive\\Desktop\\pocketbuzz\\2026-01-31 (1).webp",
        "c:\\Users\\abhis\\OneDrive\\Desktop\\pocketbuzz\\2026-01-31 (2).webp",
        "c:\\Users\\abhis\\OneDrive\\Desktop\\pocketbuzz\\2026-01-31 (3).webp",
        "c:\\Users\\abhis\\OneDrive\\Desktop\\pocketbuzz\\2026-01-31 (4).webp"
    ]
    
    full_menu = {}
    
    for img in image_files:
        if os.path.exists(img):
            try:
                res = extract_menu(img)
                # Clean up markdown code blocks if present
                clean_res = res.replace("```json", "").replace("```", "").strip()
                menu_data = json.loads(clean_res)
                full_menu.update(menu_data)
            except Exception as e:
                print(f"Error processing {img}: {e}")
        else:
            print(f"File not found: {img}")
            
    # Save to file
    with open("extracted_menu.json", "w") as f:
        json.dump(full_menu, f, indent=4)
        
    print(f"Extracted {len(full_menu)} items. Saved to extracted_menu.json")

if __name__ == "__main__":
    main()
