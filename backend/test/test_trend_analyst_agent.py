import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.trend_analyst_agent import TrendAnalystAgent
from agents.base_agent import AgentState, SharedUserInput
from agents.agent_rag_templates import setup_rag_index
from langchain.schema import Document
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_trend_analyst_agent():
    """Test the trend analyst agent"""
    # Initialize agent
    agent = TrendAnalystAgent()
    
    # Create test user input
    user_input = SharedUserInput(
        user_input="測試趨勢分析",
        profession="designer",
        personality="creative",
        gender="female",
        height_cm=165,
        skin_tone="warm",
        style_preference=["minimal", "vintage"],
        schedule_summary="9 AM to 6 PM",
        weather_summary="Sunny, 25°C",
        feedback_history=[],
        wardrobe_items=["white shirt", "denim jeans", "sneakers"],
        selfie_path=None
    )
    
    # Create initial state with context from other agents
    state = AgentState(
        user_input=user_input,
        context={
            "color_analysis": "這件衣服的顏色很適合你的膚色",
            "style_advice": "這件衣服的風格符合你的職業需求",
            "image_tags": {
                "style": "casual",
                "material": "cotton",
                "category": "shirt",
                "color": "white"
            }
        },
        conversation_history=[],
        error=None
    )
    
    # Process the state
    result_state = await agent.process(state)
    
    # Print results
    print("\n=== Trend Analyst Test Results ===")
    print(f"Error: {result_state.error}")
    print("\nConversation History:")
    for msg in result_state.conversation_history:
        print(f"- {msg}")
    print("\nContext:")
    print(json.dumps(result_state.context, indent=2, ensure_ascii=False))

def test_setup_trend_rag_index():
    """Test setting up RAG index for trend analyst"""
    # Sample documents for trend analyst
    trend_docs = [
        Document(page_content="2025年春季流行寬鬆剪裁和自然色調。"),
        Document(page_content="浪漫風格和實用主義是2025年的主要趨勢。"),
        Document(page_content="粉末粉紅色和大地色調是2025年的主打色彩。")
    ]
    
    # Setup index
    setup_rag_index("trend_analyst", trend_docs)

if __name__ == "__main__":
    # First setup RAG index
    test_setup_trend_rag_index()
    
    # Then run the test
    asyncio.run(test_trend_analyst_agent()) 