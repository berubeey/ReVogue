#!/usr/bin/env python3
"""
Test script for Fashion Designer Agent RAG functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.fashion_designer_agent import FashionDesignerAgent
from agents.base_agent import AgentState, SharedUserInput

async def test_fashion_designer():
    """Test the fashion designer agent with different professions and styles"""
    
    # Create agent instance
    agent = FashionDesignerAgent()
    
    # Test cases with different professions and styles
    test_cases = [
        {
            "profession": "律師",
            "style_preference": ["專業", "正式"],
            "skin_tone": "暖膚色",
            "description": "專業法律人士"
        },
        {
            "profession": "設計師",
            "style_preference": ["創意", "個性"],
            "skin_tone": "冷膚色",
            "description": "創意工作者"
        },
        {
            "profession": "軟體工程師",
            "style_preference": ["休閒", "舒適"],
            "skin_tone": "中性膚色",
            "description": "技術專業人士"
        },
        {
            "profession": "行銷經理",
            "style_preference": ["時尚", "商務"],
            "skin_tone": "暖膚色",
            "description": "商務專業人士"
        }
    ]
    
    print("🧥 測試時尚設計師 RAG 功能")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 測試案例 {i}: {test_case['description']}")
        print("-" * 30)
        
        # Create user input
        user_input = SharedUserInput(
            user_input=f"我是{test_case['profession']}，喜歡{', '.join(test_case['style_preference'])}風格",
            profession=test_case["profession"],
            personality="外向",
            gender="女",
            height_cm=165,
            skin_tone=test_case["skin_tone"],
            style_preference=test_case["style_preference"],
            schedule_summary="週一上午有會議，下午自由時間",
            weather_summary="晴天，溫度25度",
            feedback_history=[],
            wardrobe_items=["牛仔褲", "T恤", "西裝外套"]
        )
        
        # Create initial state
        initial_state = AgentState(
            user_input=user_input,
            context={},
            response="",
            error=""
        )
        
        # Process with agent
        try:
            result_state = await agent.process(initial_state)
            
            # Print results
            print(f"職業: {test_case['profession']}")
            print(f"風格偏好: {', '.join(test_case['style_preference'])}")
            print(f"膚色: {test_case['skin_tone']}")
            print(f"穿搭建議: {result_state.context.get('recommendations', '無建議')}")
            print(f"狀態: {agent.get_status()}")
            
            if result_state.error:
                print(f"❌ 錯誤: {result_state.error}")
            else:
                print("✅ 測試成功")
                
        except Exception as e:
            print(f"❌ 測試失敗: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 時尚設計師 RAG 功能測試完成")

if __name__ == "__main__":
    asyncio.run(test_fashion_designer()) 