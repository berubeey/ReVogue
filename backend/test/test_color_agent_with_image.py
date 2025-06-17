import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.color_analyst_agent import ColorAnalystAgent
from agents.analyze_image_with_gemini import GeminiImageAnalyzer
from agents.agent_rag_templates import setup_rag_index
from agents.base_agent import AgentState, SharedUserInput
from langchain.schema import Document
import asyncio
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the absolute path to the test image
TEST_IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test", "test_selfie.jpeg")
print(f"Test image path: {TEST_IMAGE_PATH}")

async def test_color_analyst_agent():
    """Test the color analyst agent with image analysis"""
    # Initialize agent
    agent = ColorAnalystAgent()
    
    # Create test user input
    user_input = SharedUserInput(
        user_input="測試色彩分析",
        profession="teacher",
        personality="outgoing",
        gender="male",
        height_cm=175,
        skin_tone="warm",
        style_preference=["casual", "elegant"],
        schedule_summary="9 AM to 5 PM",
        weather_summary="Sunny, 25°C",
        feedback_history=[],
        wardrobe_items=["dark suit", "white shirt", "black shoes"],
        selfie_path=TEST_IMAGE_PATH
    )
    
    # Create initial state
    state = AgentState(
        user_input=user_input,
        context={},
        conversation_history=[],
        error=None
    )
    
    # Process the state
    result_state = await agent.process(state)
    
    # Print results
    print("\n=== Test Results ===")
    print(f"Error: {result_state.error}")
    print("\nConversation History:")
    for msg in result_state.conversation_history:
        print(f"- {msg}")
    print("\nContext:")
    print(json.dumps(result_state.context, indent=2, ensure_ascii=False))

async def test_gemini_image_analyzer():
    """Test the Gemini image analyzer directly"""
    analyzer = GeminiImageAnalyzer()
    result = analyzer.analyze_image(TEST_IMAGE_PATH)
    print("\n=== Image Analysis Results ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))

def test_setup_rag_indexes():
    """Test setting up RAG indexes with sample data"""
    # Sample documents for each agent type
    color_docs = [
        Document(page_content="Warm skin tones look best in earthy colors like olive green and terracotta."),
        Document(page_content="Cool skin tones are complemented by jewel tones like sapphire blue and emerald green.")
    ]
    
    image_docs = [
        Document(page_content="Teachers should maintain a professional yet approachable appearance."),
        Document(page_content="Casual style emphasizes comfort while maintaining a put-together look.")
    ]
    
    fashion_docs = [
        Document(page_content="Elegant style combines classic pieces with modern touches."),
        Document(page_content="Professional attire should be clean, well-fitted, and appropriate for the workplace.")
    ]
    
    # Setup indexes
    setup_rag_index("color_analyst", color_docs)
    setup_rag_index("image_consultant", image_docs)
    setup_rag_index("fashion_designer", fashion_docs)

if __name__ == "__main__":
    # First setup RAG indexes
    test_setup_rag_indexes()
    
    # Then run the tests
    asyncio.run(test_gemini_image_analyzer())
    asyncio.run(test_color_analyst_agent()) 