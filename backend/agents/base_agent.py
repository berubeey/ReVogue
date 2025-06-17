from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

class SharedUserInput(BaseModel):
    """Shared input schema for all agents"""
    user_input: str
    profession: str
    personality: str
    gender: str
    height_cm: int
    skin_tone: str
    style_preference: List[str]
    schedule_summary: str
    weather_summary: str
    feedback_history: List[str]
    user_reply: Optional[str] = None
    wardrobe_items: List[str]
    selfie_path: Optional[str] = None

class AgentState(BaseModel):
    """Base state model for all agents"""
    user_input: SharedUserInput
    context: Optional[Dict[str, Any]] = None
    response: Optional[str] = None
    error: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None

    class Config:
        arbitrary_types_allowed = True

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """Process the current state and return updated state"""
        pass
    
    def can_handle(self, state: AgentState) -> bool:
        """Determine if this agent can handle the current state"""
        return True
    
    def get_status(self) -> str:
        """Get the current status of the agent"""
        return "idle"
    
    def _add_to_conversation(self, state: AgentState, message: str) -> AgentState:
        """Add a message to the conversation history"""
        if state.conversation_history is None:
            state.conversation_history = []
        state.conversation_history.append({
            "agent": self.name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        return state 