from typing import Dict, Any
from .base_agent import BaseAgent, AgentState
from .agent_rag_templates import query_agent
import os
from dotenv import load_dotenv

class EncouragerAgent(BaseAgent):
    """Agent responsible for emotional support and positive feedback"""
    
    def __init__(self):
        super().__init__(
            name="encourager",
            description="Provides encouragement and positive feedback"
        )
        # Load environment variables
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))
    
    async def process(self, state: AgentState) -> AgentState:
        try:
            # Extract outfit recommendations
            outfit_recommendations = state.response or ""
            
            # Log received recommendations
            state = self._add_to_conversation(state, f"收到穿搭建議：{outfit_recommendations}")
            
            # Prepare user profile for RAG
            user_profile = {
                "profession": state.user_input.profession,
                "personality": state.user_input.personality,
                "gender": state.user_input.gender,
                "style_preference": state.user_input.style_preference
            }
            
            # Prepare tags for RAG based on personality and style
            tags = self._get_tags_for_encouragement(state.user_input.personality, state.user_input.style_preference)
            
            # Query encouragement using RAG
            encouragement = query_agent(
                "encourager",
                tags,
                user_profile
            )
            
            # Add encouragement to conversation
            state = self._add_to_conversation(state, "生成鼓勵訊息...")
            state.context = {
                **state.context,
                "encouragement": encouragement
            }
            state = self._add_to_conversation(state, encouragement)
            
            return state
            
        except Exception as e:
            state.error = f"生成鼓勵訊息時發生錯誤：{str(e)}"
            state = self._add_to_conversation(state, f"錯誤：{state.error}")
            return state
    
    def _get_tags_for_encouragement(self, personality: str, style_preference: list) -> Dict[str, str]:
        """Get appropriate tags based on personality and style preference"""
        personality_lower = personality.lower()
        style_lower = [s.lower() for s in style_preference]
        
        # Determine encouragement type based on personality
        if any(word in personality_lower for word in ['外向', '活潑', '熱情']):
            encouragement_type = "energetic"
        elif any(word in personality_lower for word in ['內向', '安靜', '沉穩']):
            encouragement_type = "gentle"
        elif any(word in personality_lower for word in ['自信', '堅定']):
            encouragement_type = "confident"
        else:
            encouragement_type = "general"
        
        # Determine style category
        if any(word in style_lower for word in ['專業', '正式', '商務']):
            style_category = "professional"
        elif any(word in style_lower for word in ['創意', '時尚', '個性']):
            style_category = "creative"
        elif any(word in style_lower for word in ['休閒', '舒適', '輕鬆']):
            style_category = "casual"
        else:
            style_category = "general"
        
        return {
            "encouragement_type": encouragement_type,
            "style_category": style_category
        }
    
    def _is_emotional_content(self, text: str) -> bool:
        """Check if the text contains emotional content"""
        emotional_keywords = [
            "難過", "開心", "緊張", "焦慮", "自信", "沒自信",
            "擔心", "害怕", "期待", "失望", "興奮", "疲憊"
        ]
        return any(keyword in text for keyword in emotional_keywords)
    
    def get_status(self) -> str:
        return "providing_encouragement" 