from typing import Dict, Any
from .base_agent import BaseAgent, AgentState
from .agent_rag_templates import query_agent
import os
from dotenv import load_dotenv

class ImageConsultantAgent(BaseAgent):
    """Agent responsible for image consulting and style recommendations"""
    
    def __init__(self):
        super().__init__(
            name="image_consultant",
            description="Provides style and image consulting advice"
        )
        # Load environment variables
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))
    
    async def process(self, state: AgentState) -> AgentState:
        try:
            # Extract context from previous agents
            secretary_summary = state.context.get("secretary_summary", "")
            
            # Log received analyses
            state = self._add_to_conversation(state, f"收到個人秘書分析：{secretary_summary}")
            
            # Prepare user profile for RAG
            user_profile = {
                "occupation": state.user_input.profession,
                "style_preference": state.user_input.style_preference
            }
            
            # Prepare tags for RAG based on profession
            tags = self._get_tags_for_profession(state.user_input.profession)
            
            # Query style advice using RAG
            style_advice = query_agent(
                "image_consultant",
                tags,
                user_profile
            )
            
            # Add style advice to conversation
            state = self._add_to_conversation(state, "生成形象建議...")
            state.context = {
                **state.context,
                "style_advice": style_advice
            }
            state = self._add_to_conversation(state, style_advice)
            
            return state
            
        except Exception as e:
            state.error = f"生成形象建議時發生錯誤：{str(e)}"
            state = self._add_to_conversation(state, f"錯誤：{state.error}")
            return state
    
    def _get_tags_for_profession(self, profession: str) -> Dict[str, str]:
        """Get appropriate tags based on profession"""
        profession_lower = profession.lower()
        
        if any(word in profession_lower for word in ['law', 'legal', 'lawyer', 'attorney']):
            return {"style": "business_formal", "category": "legal"}
        elif any(word in profession_lower for word in ['design', 'creative', 'art', 'fashion']):
            return {"style": "creative_professional", "category": "design"}
        elif any(word in profession_lower for word in ['engineer', 'technical', 'tech']):
            return {"style": "business_casual", "category": "engineering"}
        elif any(word in profession_lower for word in ['marketing', 'advertising', 'sales']):
            return {"style": "smart_casual", "category": "marketing"}
        elif any(word in profession_lower for word in ['startup', 'software', 'it', 'programmer']):
            return {"style": "business_casual", "category": "tech"}
        else:
            return {"style": "professional", "category": "general"}
    
    def get_status(self) -> str:
        return "analyzing_style" 