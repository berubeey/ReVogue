from typing import Dict, Any
from .base_agent import BaseAgent, AgentState
from .agent_rag_templates import query_agent
import json
import os
from dotenv import load_dotenv

class TrendAnalystAgent(BaseAgent):
    """Agent responsible for fashion trend analysis and recommendations"""
    
    def __init__(self):
        super().__init__(
            name="trend_analyst",
            description="Analyzes current fashion trends and provides trend-based recommendations"
        )
        # Load environment variables
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))
    
    async def process(self, state: AgentState) -> AgentState:
        try:
            # Extract context from previous agents
            color_analysis = state.context.get("color_analysis", "")
            style_advice = state.context.get("style_advice", "")
            image_tags = state.context.get("image_tags", {})
            
            # Log received analyses
            state = self._add_to_conversation(state, f"收到色彩分析：{color_analysis}")
            state = self._add_to_conversation(state, f"收到形象顧問建議：{style_advice}")
            
            # Prepare user profile for RAG
            user_profile = {
                "profession": state.user_input.profession,
                "style_preference": state.user_input.style_preference,
                "personality": state.user_input.personality,
                "gender": state.user_input.gender
            }
            
            # Query trend analysis using RAG
            trend_analysis = query_agent(
                "trend_analyst",
                image_tags,
                user_profile
            )
            
            # Add trend analysis to conversation
            state = self._add_to_conversation(state, "生成趨勢分析...")
            state.context = {
                **state.context,
                "trend_analysis": trend_analysis
            }
            state = self._add_to_conversation(state, trend_analysis)
            
            return state
            
        except Exception as e:
            state.error = f"生成趨勢分析時發生錯誤：{str(e)}"
            state = self._add_to_conversation(state, f"錯誤：{state.error}")
            return state
    
    def get_status(self) -> str:
        return "analyzing_trends" 