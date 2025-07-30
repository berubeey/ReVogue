#!/usr/bin/env python3
"""
Test script for complete Fashion Designer Agent functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.fashion_designer_agent import FashionDesignerAgent
from agents.base_agent import AgentState, SharedUserInput

async def test_complete_fashion_designer():
    """Test the complete fashion designer agent with full user profile"""
    
    # Create agent instance
    agent = FashionDesignerAgent()
    
    # Test cases with complete user profiles
    test_cases = [
        {
            "name": "專業律師",
            "user_input": SharedUserInput(
                user_input="我是律師，喜歡專業正式風格，需要適合法庭的穿搭",
                profession="律師",
                personality="外向",
                gender="女",
                height_cm=165,
                skin_tone="暖膚色",
                style_preference=["專業", "正式"],
                schedule_summary="週一上午有法庭辯護，下午客戶會議",
                weather_summary="晴天，溫度22度",
                feedback_history=["希望更專業一些", "顏色搭配很好"],
                wardrobe_items=["黑色西裝外套", "白色襯衫", "黑色高跟鞋", "灰色西裝褲"]
            )
        },
        {
            "name": "創意設計師",
            "user_input": SharedUserInput(
                user_input="我是設計師，喜歡創意個性風格，需要適合工作室的穿搭",
                profession="設計師",
                personality="內向",
                gender="女",
                height_cm=160,
                skin_tone="冷膚色",
                style_preference=["創意", "個性"],
                schedule_summary="週一上午設計會議，下午自由創作時間",
                weather_summary="陰天，溫度18度",
                feedback_history=["希望更有創意", "風格很獨特"],
                wardrobe_items=["寬鬆毛衣", "牛仔褲", "帆布鞋", "彩色圍巾"]
            )
        },
        {
            "name": "休閒工程師",
            "user_input": SharedUserInput(
                user_input="我是軟體工程師，喜歡休閒舒適風格，需要適合辦公室的穿搭",
                profession="軟體工程師",
                personality="自信",
                gender="男",
                height_cm=175,
                skin_tone="中性膚色",
                style_preference=["休閒", "舒適"],
                schedule_summary="週一上午程式開發，下午團隊會議",
                weather_summary="多雲，溫度20度",
                feedback_history=["希望更舒適", "風格很實用"],
                wardrobe_items=["牛仔褲", "T恤", "運動鞋", "連帽衫"]
            )
        }
    ]
    
    print("🎨 測試完整時尚設計師功能")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 測試案例 {i}: {test_case['name']}")
        print("-" * 30)
        
        # Create initial state
        initial_state = AgentState(
            user_input=test_case["user_input"],
            context={},
            response="",
            error="",
            conversation=[]
        )
        
        # Process with fashion designer agent
        try:
            result_state = await agent.process(initial_state)
            
            if result_state.error:
                print(f"❌ 錯誤: {result_state.error}")
                continue
            
            # Print results
            print(f"👤 職業: {test_case['user_input'].profession}")
            print(f"🎭 個性: {test_case['user_input'].personality}")
            print(f"🎨 風格偏好: {', '.join(test_case['user_input'].style_preference)}")
            print(f"👕 膚色: {test_case['user_input'].skin_tone}")
            print(f"📏 身高: {test_case['user_input'].height_cm}cm")
            
            # Print recommendations
            recommendations = result_state.context.get('recommendations', '無建議')
            print(f"\n💡 穿搭建議:")
            print(recommendations)
            
            # Print matching photos
            matching_photos = result_state.context.get('matching_photos', [])
            if matching_photos:
                print(f"\n📸 推薦穿搭範本照 ({len(matching_photos)} 套):")
                for photo in matching_photos:
                    print(f"\n  第 {photo['rank']} 套:")
                    print(f"  📷 照片: {photo['photo_path']}")
                    print(f"  ⭐ 匹配度: {photo['score']}/10")
                    print(f"  🏷️ 標籤: {_format_tags_simple(photo['tags'])}")
                    if photo.get('item_description'):
                        print(f"  📝 描述: {photo['item_description'][:100]}...")
            else:
                print("\n❌ 沒有找到匹配的穿搭範本照")
            
            print(f"\n✅ 狀態: {agent.get_status()}")
            
        except Exception as e:
            print(f"❌ 測試失敗: {str(e)}")
        
        print("\n" + "=" * 50)

def _format_tags_simple(tags: dict) -> str:
    """Format tags for simple display"""
    formatted = []
    for key, value in tags.items():
        if isinstance(value, list):
            formatted.append(f"{key}: {', '.join(value[:2])}")  # Show first 2 items
        else:
            formatted.append(f"{key}: {value}")
    return " | ".join(formatted[:3])  # Show first 3 tags

if __name__ == "__main__":
    asyncio.run(test_complete_fashion_designer()) 