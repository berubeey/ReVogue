#!/usr/bin/env python3
"""
Test script for Image Consultant Agent RAG functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.image_consultant_agent import ImageConsultantAgent
from agents.base_agent import AgentState, SharedUserInput

async def test_image_consultant():
    """Test the image consultant agent with different professions"""
    
    # Create agent instance
    agent = ImageConsultantAgent()
    
    # Test cases with different professions
    test_cases = [
        {
            "profession": "律師",
            "style_preference": ["專業", "正式"],
            "description": "法律專業人士"
        },
        {
            "profession": "軟體工程師",
            "style_preference": ["休閒", "舒適"],
            "description": "科技行業工作者"
        },
        {
            "profession": "時尚設計師",
            "style_preference": ["創意", "時尚"],
            "description": "創意行業工作者"
        },
        {
            "profession": "行銷經理",
            "style_preference": ["商務", "時尚"],
            "description": "行銷專業人士"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== 測試案例 {i}: {test_case['description']} ===")
        
        # Create user input
        user_input = SharedUserInput(
            user_input=f"我是{test_case['profession']}，需要形象建議",
            profession=test_case["profession"],
            style_preference=test_case["style_preference"],
            skin_tone="中性膚色",
            personality="外向",
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
                "secretary_summary": f"今日天氣晴朗，適合{test_case['profession']}的工作場合穿著。"
            }
        )
        
        try:
            # Process with agent
            result_state = await agent.process(state)
            
            # Print results
            print(f"職業: {test_case['profession']}")
            print(f"風格偏好: {', '.join(test_case['style_preference'])}")
            print(f"形象建議: {result_state.context.get('style_advice', '無建議')}")
            print(f"狀態: {agent.get_status()}")
            
        except Exception as e:
            print(f"❌ 測試失敗: {str(e)}")

if __name__ == "__main__":
    print("開始測試形象顧問代理...")
    asyncio.run(test_image_consultant())
    print("\n測試完成！") 