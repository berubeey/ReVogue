#!/usr/bin/env python3
"""
Test script for Encourager Agent RAG functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.encourager_agent import EncouragerAgent
from agents.base_agent import AgentState, SharedUserInput

async def test_encourager():
    """Test the encourager agent with different personalities and styles"""
    
    # Create agent instance
    agent = EncouragerAgent()
    
    # Test cases with different personalities and styles
    test_cases = [
        {
            "profession": "律師",
            "personality": "外向",
            "style_preference": ["專業", "正式"],
            "description": "外向的專業人士"
        },
        {
            "profession": "設計師",
            "personality": "內向",
            "style_preference": ["創意", "個性"],
            "description": "內向的創意工作者"
        },
        {
            "profession": "工程師",
            "personality": "自信",
            "style_preference": ["休閒", "舒適"],
            "description": "自信的技術人員"
        },
        {
            "profession": "行銷經理",
            "personality": "活潑",
            "style_preference": ["時尚", "商務"],
            "description": "活潑的商務人士"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== 測試案例 {i}: {test_case['description']} ===")
        
        # Create user input
        user_input = SharedUserInput(
            user_input=f"我是{test_case['profession']}，需要鼓勵",
            profession=test_case["profession"],
            style_preference=test_case["style_preference"],
            skin_tone="中性膚色",
            personality=test_case["personality"],
            gender="女性",
            height_cm=165,
            schedule_summary="工作場合",
            weather_summary="晴天",
            feedback_history=[],
            wardrobe_items=[]
        )
        
        # Create agent state
        state = AgentState(
            user_input=user_input,
            context={
                "outfit_recommendations": f"為{test_case['profession']}推薦的穿搭方案"
            },
            response="這是一套適合的穿搭建議"
        )
        
        try:
            # Process with agent
            result_state = await agent.process(state)
            
            # Print results
            print(f"職業: {test_case['profession']}")
            print(f"個性: {test_case['personality']}")
            print(f"風格偏好: {', '.join(test_case['style_preference'])}")
            print(f"鼓勵訊息: {result_state.context.get('encouragement', '無鼓勵')}")
            print(f"狀態: {agent.get_status()}")
            
        except Exception as e:
            print(f"❌ 測試失敗: {str(e)}")

if __name__ == "__main__":
    print("開始測試鼓勵員代理...")
    asyncio.run(test_encourager())
    print("\n測試完成！") 