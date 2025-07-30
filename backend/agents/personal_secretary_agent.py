from typing import Dict, Any
from .base_agent import BaseAgent, AgentState
import json

class PersonalSecretaryAgent(BaseAgent):
    """Agent responsible for analyzing context and gathering information"""
    
    def __init__(self):
        super().__init__(
            name="personal_secretary",
            description="Analyzes user context and provides situation summary"
        )
    
    async def process(self, state: AgentState) -> AgentState:
        try:
            # Log received input
            state = self._add_to_conversation(state, f"收到用戶輸入：{state.user_input.user_input}")
            
            # Construct situation summary
            secretary_summary = f"""
            基於您的需求，以下是情境分析：

            1. 場合分析：
            - 地點：{state.user_input.user_input.split('在')[1].split('的')[0] if '在' in state.user_input.user_input else '未指定'}
            - 活動類型：{state.user_input.user_input.split('的')[1].split('，')[0] if '的' in state.user_input.user_input else '未指定'}
            - 時間：{state.user_input.schedule_summary if state.user_input.schedule_summary else '未指定'}

            2. 環境因素：
            - 天氣狀況：{state.user_input.weather_summary if state.user_input.weather_summary else '未指定'}
            - 室內/室外：{'室內' if '會議' in state.user_input.user_input else '未指定'}
            - 活動時長：{'全天' if '會議' in state.user_input.user_input else '未指定'}

            3. 個人特徵：
            - 職業：{state.user_input.profession}
            - 性格：{state.user_input.personality}
            - 身高：{state.user_input.height_cm}cm
            - 風格偏好：{', '.join(state.user_input.style_preference)}

            4. 特殊需求：
            - 衣櫃物品：{', '.join(state.user_input.wardrobe_items) if state.user_input.wardrobe_items else '未指定'}
            - 歷史反饋：{', '.join(state.user_input.feedback_history) if state.user_input.feedback_history else '無'}
            """
            
            # Add summary to conversation
            state = self._add_to_conversation(state, "生成情境分析...")
            state.context = {
                "secretary_summary": secretary_summary
            }
            state = self._add_to_conversation(state, secretary_summary)
            
            return state
            
        except Exception as e:
            state.error = f"生成情境分析時發生錯誤：{str(e)}"
            state = self._add_to_conversation(state, f"錯誤：{state.error}")
            return state
    
    def get_status(self) -> str:
        return "analyzing_context" 