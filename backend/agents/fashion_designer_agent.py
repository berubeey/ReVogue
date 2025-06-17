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
            user_profile = {
                "occupation": state.user_input.profession,
                "style_preference": state.user_input.style_preference,
                "skin_tone": state.user_input.skin_tone
            }
            
            # Get image tags from color analysis
            image_tags = state.context.get("image_tags", {})
            
            # Query fashion designer for final recommendations
            recommendations = query_agent(
                "fashion_designer",
                image_tags,
                user_profile
            )
            
            # Add recommendations to context
            state.context["recommendations"] = recommendations
            state = self._add_to_conversation(state, "生成最終穿搭建議...")
            state = self._add_to_conversation(state, recommendations)
            
            return state
            
        except Exception as e:
            state.error = f"生成穿搭建議時發生錯誤：{str(e)}"
            state = self._add_to_conversation(state, f"錯誤：{state.error}")
            return state
    
    def get_status(self) -> str:
        return "generating_recommendations" 