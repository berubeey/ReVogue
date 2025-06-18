import os
import json
import base64
import google.generativeai as genai
from pathlib import Path
from typing import Dict
from PIL import Image

# 設定 Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# 輸出格式轉中文 key
FIELD_TRANSLATION = {
    "gender": "性別",
    "style": "風格",
    "material": "材質",
    "category": "分類",
    "color": "顏色",
    "occasion": "場合",
    "mood": "情緒",
    "suitable_skin_tones": "適合膚色",
    "item_description": "服裝單品描述"
}

def analyze_image(image_path: str) -> Dict:
    try:
        image = Image.open(image_path)
        
        prompt = """
        Analyze this fashion image and return structured JSON only with the following keys:

        - "item_description": A detailed description of the clothing items and their features.
        - "tags": An object that includes:
            - "gender": The target gender for this outfit (e.g., male, female, unisex).
            - "style": The overall style (e.g., casual, minimal, retro).
            - "material": The materials used (e.g., cotton, denim, chiffon).
            - "category": The clothing types (e.g., shirt, dress, coat).
            - "color": The visible colors (e.g., navy, beige, white).
            - "occasion" : The likely occasions or use cases (e.g., meeting, weekend, party).
            - "mood" : The mood this outfit evokes or suits (e.g., relaxed, confident, playful).
            - "suitable_skin_tones" : Skin tone types that match this outfit (e.g., warm, cool, neutral).

        Respond strictly in JSON format. DO NOT include any extra explanation or commentary. Only return the JSON object.
        """


        response = model.generate_content(
            [prompt, image],
            stream=False
        )

        try:
            # Clean the response text to extract only the JSON part
            response_text = response.text
            # Find the first occurrence of { and last occurrence of }
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                print(f"❌ No valid JSON found in response for {image_path}")
                return {}
                
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            return result
        except Exception as e:
            print(f"❌ Failed to parse JSON for {image_path}: {e}")
            print(f"Raw response: {response.text}")
            return {}
    except Exception as e:
        print(f"❌ Failed to open image {image_path}: {e}")
        return {}

def process_image_folder(folder_path: str, output_path: str = "output_tags.json"):
    all_results = {}
    folder = Path(folder_path)
    image_files = list(folder.glob("*.jpeg"))

    print(f"📸 共偵測到 {len(image_files)} 張圖片，開始處理...")

    for image_path in image_files:
        print(f"➡️ 分析中：{image_path.name}")
        tags = analyze_image(str(image_path))
        if tags:
            all_results[image_path.name] = tags

    # 儲存 JSON 檔
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 完成！分析結果儲存在 {output_path}")

# 🧪 執行
if __name__ == "__main__":
    process_image_folder("/Users/chinju/agent2/fashion_dataset")  # 使用絕對路徑
