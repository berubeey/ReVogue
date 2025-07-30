from typing import Dict, Any
from .base_agent import BaseAgent, AgentState
from .analyze_image_with_gemini import GeminiImageAnalyzer
from .agent_rag_templates import query_agent
import json
import os
from dotenv import load_dotenv

class ColorAnalystAgent(BaseAgent):
    """Agent responsible for color analysis and recommendations"""
    
    def __init__(self):
        super().__init__(
            name="color_analyst",
            description="Analyzes color combinations and provides color recommendations"
        )
        # Load environment variables
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))
        
        # Initialize Gemini image analyzer
        self.image_analyzer = GeminiImageAnalyzer()
    
    async def process(self, state: AgentState) -> AgentState:
        try:
            # Extract context from previous agents
            secretary_summary = state.context.get("secretary_summary", "")
            style_advice = state.context.get("style_advice", "")
            
            # Log received analyses
            state = self._add_to_conversation(state, f"收到個人秘書分析：{secretary_summary}")
            state = self._add_to_conversation(state, f"收到形象顧問建議：{style_advice}")
            
            # Analyze image if selfie is provided
            image_description = ""
            image_tags = {}
            if hasattr(state.user_input, "selfie_path") and state.user_input.selfie_path:
                print(f"Selfie path found: {state.user_input.selfie_path}")
                image_analysis_result = self.image_analyzer.analyze_image(
                    state.user_input.selfie_path
                )
                image_description = image_analysis_result["description"]
                image_tags = image_analysis_result["tags"]
                state = self._add_to_conversation(
                    state,
                    f"圖片分析結果：{image_description} (標籤: {image_tags})"
                )
            
            # Prepare user profile for RAG
            user_profile = {
                "skin_tone": state.user_input.skin_tone,
                "occupation": state.user_input.profession,
                "style_preference": state.user_input.style_preference
            }
            
            # Query color analysis using RAG
            color_analysis = query_agent(
                "color_analyst",
                image_tags,
                user_profile
            )
            
            # Add color analysis to conversation
            state = self._add_to_conversation(state, "生成色彩分析...")
            state.context = {
                **state.context,
                "color_analysis": color_analysis,
                "image_description": image_description,
                "image_tags": image_tags
            }
            state = self._add_to_conversation(state, color_analysis)
            
            return state
            
        except Exception as e:
            state.error = f"生成色彩分析時發生錯誤：{str(e)}"
            state = self._add_to_conversation(state, f"錯誤：{state.error}")
            return state
    
    def get_status(self) -> str:
        return "analyzing_colors" 