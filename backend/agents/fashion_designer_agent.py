from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentState
from .personal_secretary_agent import PersonalSecretaryAgent
from .image_consultant_agent import ImageConsultantAgent
from .color_analyst_agent import ColorAnalystAgent
from .agent_rag_templates import query_agent
import json
import os
from dotenv import load_dotenv

class FashionDesignerAgent(BaseAgent):
    """Lead Agent responsible for coordinating other agents and generating final recommendations"""
    
    def __init__(self):
        super().__init__(
            name="fashion_designer",
            description="Coordinates fashion recommendations from multiple agents"
        )
        # Load environment variables
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))
        
        # Initialize other agents
        self.personal_secretary = PersonalSecretaryAgent()
        self.image_consultant = ImageConsultantAgent()
        self.color_analyst = ColorAnalystAgent()
        
        # Load fashion dataset tags
        self.fashion_tags = self._load_fashion_tags()
    
    def _load_fashion_tags(self) -> Dict[str, Any]:
        """Load fashion dataset tags from output_tags.json"""
        try:
            tags_path = os.path.join(os.path.dirname(__file__), '../output_tags.json')
            with open(tags_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 載入穿搭標籤時發生錯誤：{str(e)}")
            return {}
    
    async def process(self, state: AgentState) -> AgentState:
        try:
            # Step 1: Get schedule and weather information
            state = await self.personal_secretary.process(state)
            if state.error:
                return state
            
            # Step 2: Get style advice
            state = await self.image_consultant.process(state)
            if state.error:
                return state
            
            # Step 3: Get color analysis
            state = await self.color_analyst.process(state)
            if state.error:
                return state
            
            # Step 4: Generate final recommendations using RAG
            user_profile = self._build_complete_user_profile(state)
            
            # Get image tags from color analysis
            image_tags = state.context.get("image_tags", {})
            
            # Query fashion designer for final recommendations
            recommendations = query_agent(
                "fashion_designer",
                image_tags,
                user_profile
            )
            
            # Step 5: Find matching fashion photos
            matching_photos = self._find_matching_fashion_photos(user_profile, image_tags)
            
            # Add recommendations and photos to context
            state.context["recommendations"] = recommendations
            state.context["matching_photos"] = matching_photos
            state = self._add_to_conversation(state, "生成最終穿搭建議...")
            state = self._add_to_conversation(state, recommendations)
            
            # Add photo recommendations
            if matching_photos:
                photo_recommendations = self._format_photo_recommendations(matching_photos)
                state = self._add_to_conversation(state, photo_recommendations)
            
            return state
            
        except Exception as e:
            state.error = f"生成穿搭建議時發生錯誤：{str(e)}"
            state = self._add_to_conversation(state, f"錯誤：{state.error}")
            return state
    
    def _build_complete_user_profile(self, state: AgentState) -> Dict[str, Any]:
        """Build complete user profile from all available information"""
        user_input = state.user_input
        
        profile = {
            # Basic personal info
            "gender": user_input.gender,
            "height_cm": user_input.height_cm,
            "skin_tone": user_input.skin_tone,
            "personality": user_input.personality,
            
            # Professional info
            "occupation": user_input.profession,
            "style_preference": user_input.style_preference,
            
            # Schedule and context
            "schedule_summary": user_input.schedule_summary,
            "weather_summary": user_input.weather_summary,
            
            # Wardrobe and feedback
            "wardrobe_items": user_input.wardrobe_items,
            "feedback_history": user_input.feedback_history,
            
            # Additional context from other agents
            "color_analysis": state.context.get("color_analysis", ""),
            "style_advice": state.context.get("style_advice", ""),
            "image_tags": state.context.get("image_tags", {})
        }
        
        return profile
    
    def _find_matching_fashion_photos(self, user_profile: Dict[str, Any], image_tags: Dict[str, str]) -> List[Dict[str, Any]]:
        """Find matching fashion photos based on user profile and image tags"""
        if not self.fashion_tags:
            return []
        
        matching_photos = []
        user_tags = self._get_tags_for_fashion_design(user_profile)
        user_gender = user_profile.get("gender", "").lower()
        
        # 轉換中文性別為英文
        gender_mapping = {
            "女": "female",
            "男": "male",
            "female": "female",
            "male": "male"
        }
        user_gender_en = gender_mapping.get(user_gender, user_gender)
        
        # Score each photo based on tag matching
        photo_scores = []
        
        for photo_id, photo_data in self.fashion_tags.items():
            score = 0
            photo_tags = photo_data.get("tags", {})
            photo_gender = photo_tags.get("gender", "").lower()
            
            # 性別匹配是最重要的條件，給予最高權重
            if user_gender_en and photo_gender:
                if user_gender_en == photo_gender:
                    score += 10  # 性別完全匹配，給予最高分
                elif photo_gender == "unisex":
                    score += 5   # 中性服裝，給予中等分數
                else:
                    # 性別不匹配，跳過這張照片
                    continue
            elif not user_gender_en or not photo_gender:
                # 如果沒有性別資訊，給予基礎分數
                score += 2
            
            # Score based on style matching
            if user_tags.get("style") and photo_tags.get("style"):
                if user_tags["style"] in photo_tags["style"]:
                    score += 3
            
            # Score based on occasion matching
            if user_tags.get("occasion") and photo_tags.get("occasion"):
                if user_tags["occasion"] in photo_tags["occasion"]:
                    score += 3
            
            # Score based on formality matching
            if user_tags.get("formality") and photo_tags.get("mood"):
                if user_tags["formality"] in photo_tags["mood"]:
                    score += 2
            
            # Score based on color palette matching
            if user_tags.get("color_palette") and photo_tags.get("color"):
                if user_tags["color_palette"] in photo_tags["color"]:
                    score += 2
            
            # Score based on skin tone matching
            if user_profile.get("skin_tone") and photo_tags.get("suitable_skin_tones"):
                if user_profile["skin_tone"] in photo_tags["suitable_skin_tones"]:
                    score += 2
            
            # Score based on occupation matching
            if user_profile.get("occupation") and photo_tags.get("category"):
                if user_profile["occupation"] in photo_tags["category"]:
                    score += 1
            
            # 只有有分數的照片才會被加入候選列表
            if score > 0:
                photo_scores.append({
                    "photo_id": photo_id,
                    "photo_data": photo_data,
                    "score": score
                })
        
        # Sort by score and return top 3
        photo_scores.sort(key=lambda x: x["score"], reverse=True)
        
        for i, photo_score in enumerate(photo_scores[:3]):
            matching_photos.append({
                "rank": i + 1,
                "photo_id": photo_score["photo_id"],
                "photo_path": f"fashion_dataset/{photo_score['photo_id']}",
                "tags": photo_score["photo_data"]["tags"],
                "score": photo_score["score"],
                "item_description": photo_score["photo_data"].get("item_description", "")
            })
        
        return matching_photos
    
    def _format_photo_recommendations(self, matching_photos: List[Dict[str, Any]]) -> str:
        """Format photo recommendations as text"""
        if not matching_photos:
            return ""
        
        photo_text = "\n\n📸 **推薦穿搭範本照：**\n"
        
        for photo in matching_photos:
            photo_text += f"\n**第 {photo['rank']} 套推薦：**\n"
            photo_text += f"📷 照片：{photo['photo_path']}\n"
            photo_text += f"🏷️ 標籤：{self._format_tags(photo['tags'])}\n"
            if photo.get('item_description'):
                photo_text += f"📝 描述：{photo['item_description']}\n"
            photo_text += f"⭐ 匹配度：{photo['score']}/10\n"
        
        return photo_text
    
    def _format_tags(self, tags: Dict[str, Any]) -> str:
        """Format tags for display"""
        formatted_tags = []
        for key, value in tags.items():
            if isinstance(value, list):
                formatted_tags.append(f"{key}: {', '.join(value)}")
            else:
                formatted_tags.append(f"{key}: {value}")
        return " | ".join(formatted_tags)
    
    def _get_tags_for_fashion_design(self, user_profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate tags for fashion design queries based on user profile"""
        tags = {}
        
        # Add occupation-based tags
        occupation = user_profile.get("occupation", "")
        if occupation:
            if "律師" in occupation or "醫生" in occupation or "會計師" in occupation:
                tags["style"] = "professional"
                tags["occasion"] = "business"
            elif "設計師" in occupation or "藝術家" in occupation or "創意" in occupation:
                tags["style"] = "creative"
                tags["occasion"] = "casual"
            elif "工程師" in occupation or "技術" in occupation:
                tags["style"] = "casual"
                tags["occasion"] = "daily"
            else:
                tags["style"] = "versatile"
                tags["occasion"] = "general"
        
        # Add style preference tags
        style_prefs = user_profile.get("style_preference", [])
        if style_prefs:
            if "正式" in style_prefs or "專業" in style_prefs:
                tags["formality"] = "formal"
            elif "休閒" in style_prefs or "舒適" in style_prefs:
                tags["formality"] = "casual"
            elif "時尚" in style_prefs or "潮流" in style_prefs:
                tags["formality"] = "trendy"
            else:
                tags["formality"] = "balanced"
        
        # Add skin tone tags
        skin_tone = user_profile.get("skin_tone", "")
        if skin_tone:
            if "暖" in skin_tone:
                tags["color_palette"] = "warm"
            elif "冷" in skin_tone:
                tags["color_palette"] = "cool"
            else:
                tags["color_palette"] = "neutral"
        
        # Add personality tags
        personality = user_profile.get("personality", "")
        if personality:
            if "外向" in personality:
                tags["mood"] = "confident"
            elif "內向" in personality:
                tags["mood"] = "elegant"
            elif "自信" in personality:
                tags["mood"] = "powerful"
            elif "活潑" in personality:
                tags["mood"] = "energetic"
        
        return tags
    
    def get_status(self) -> str:
        return "generating_recommendations" 