from typing import Dict, Any
from .base_agent import BaseAgent, AgentState
import json

class EncouragerAgent(BaseAgent):
    """Agent responsible for emotional support and positive feedback"""
    
    def __init__(self):
        super().__init__(
            name="encourager",
            description="Provides encouragement and positive feedback"
        )
    
    async def process(self, state: AgentState) -> AgentState:
        try:
            # Extract outfit recommendations
            outfit_recommendations = state.response or ""
            
            # Log received recommendations
            state = self._add_to_conversation(state, f"收到穿搭建議：{outfit_recommendations}")
            
            # Construct encouragement message
            encouragement = f"""
            親愛的用戶，看到您為重要場合精心準備，我感到非常欣慰！

            您選擇的穿搭方案展現了您對細節的關注和對專業形象的追求。作為一位{state.user_input.profession}，
            您的{state.user_input.personality}特質將在這些精心搭配的服飾中得到完美展現。

            記住，自信是最好的配飾。無論您選擇哪套穿搭，都請帶著自信和從容出席。
            您的專業素養和個人魅力一定會給在場的每個人留下深刻印象。

            祝您一切順利！
            """
            
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
    
    def _is_emotional_content(self, text: str) -> bool:
        """Check if the text contains emotional content"""
        emotional_keywords = [
            "難過", "開心", "緊張", "焦慮", "自信", "沒自信",
            "擔心", "害怕", "期待", "失望", "興奮", "疲憊"
        ]
        return any(keyword in text for keyword in emotional_keywords)
    
    def get_status(self) -> str:
        return "providing_encouragement" 