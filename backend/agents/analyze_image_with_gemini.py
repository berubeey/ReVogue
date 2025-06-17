import base64
import os
import google.generativeai as genai
from typing import Dict, Any
import json
import re
from dotenv import load_dotenv

class GeminiImageAnalyzer:
    def __init__(self):
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def _encode_image(self, image_path: str) -> bytes:
        with open(image_path, "rb") as image_file:
            return image_file.read()

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        content = ""
        try:
            image_bytes = self._encode_image(image_path)
            print(f"Analyzing image from path: {image_path}")
            
            prompt_text = """你是一位時尚分析專家。請分析這張圖片並提供詳細的描述和結構化的標籤。

請用中文回答，並使用以下 JSON 格式：
{
    "description": "對圖片中人物/衣物的詳細中文描述",
    "tags": {
        "style": "服裝風格（例如：休閒、正式、運動）",
        "material": "材質類型",
        "category": "服裝類別（例如：襯衫、洋裝、褲子）",
        "color": "主要顏色"
    }
}

重要提示：
1. 只返回 JSON 格式的內容
2. 不要包含任何其他文字或解釋
3. 確保回應是有效的 JSON 格式
4. 如果無法確定某個屬性，請使用 "unknown" 作為值
5. 所有文字都必須使用中文"""
            
            print(f"Sending prompt to Gemini API...")

            response = self.model.generate_content(
                [
                    {
                        "parts": [{
                            "text": prompt_text
                        }, {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_bytes
                            }
                        }]
                    }
                ]
            )
            
            content = response.text
            print(f"Raw response from Gemini API: {content}")

            # Try to extract JSON from the response
            try:
                # First try: direct JSON parsing
                parsed_content = json.loads(content)
            except json.JSONDecodeError:
                try:
                    # Second try: extract JSON from markdown code block
                    json_match = re.search(r"```(?:json)?\n([\s\S]*?)\n```", content)
                    if json_match:
                        json_string = json_match.group(1)
                        parsed_content = json.loads(json_string)
                    else:
                        # Third try: find any JSON-like structure
                        json_match = re.search(r"\{[\s\S]*\}", content)
                        if json_match:
                            json_string = json_match.group(0)
                            parsed_content = json.loads(json_string)
                        else:
                            raise ValueError("No valid JSON found in response")
                except Exception as e:
                    print(f"Error parsing JSON: {e}")
                    print(f"Raw content: {content}")
                    return {
                        "description": "圖片分析失敗：JSON 解析錯誤",
                        "tags": {
                            "style": "unknown",
                            "material": "unknown",
                            "category": "unknown",
                            "color": "unknown"
                        }
                    }

            # Validate and extract required fields
            description = parsed_content.get("description", "圖片分析失敗")
            tags = parsed_content.get("tags", {})
            
            # Ensure all required tag fields exist
            required_tags = ["style", "material", "category", "color"]
            for tag in required_tags:
                if tag not in tags:
                    tags[tag] = "unknown"
            
            return {
                "description": description,
                "tags": tags
            }
            
        except Exception as e:
            print(f"An unexpected error occurred during image analysis: {e}")
            print(f"Raw content: {content}")
            return {
                "description": f"圖片分析失敗：{str(e)}",
                "tags": {
                    "style": "unknown",
                    "material": "unknown",
                    "category": "unknown",
                    "color": "unknown"
                }
            }

if __name__ == "__main__":
    # Example usage
    analyzer = GeminiImageAnalyzer()
    image_path = "../../images/fashion_style_1.jpeg"
    
    if os.path.exists(image_path):
        result = analyzer.analyze_image(image_path)
        print("Image Analysis Result:")
        print(f"Description: {result['description']}")
        print(f"Tags: {result['tags']}")
    else:
        print(f"Image not found at {image_path}") 