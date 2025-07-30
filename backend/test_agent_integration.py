"""
測試agents與新PostgreSQL RAG系統的整合
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.agent_rag_templates import query_agent, query_agent_with_custom_query, generate_search_tags

def test_agent_queries():
    """測試各個agent的查詢功能"""
    print("🧪 測試agents與PostgreSQL RAG系統整合")
    print("=" * 60)
    
    # 模擬用戶資料
    mock_user_profile = {
        'occupation': '軟體工程師',
        'style_preference': ['休閒', '簡約'],
        'skin_tone': '暖色調',
        'personality': '內向',
        'gender': '女',
        'hair_color': '黑色',
        'eye_color': '棕色'
    }
    
    # 模擬單品標籤
    mock_tag = {
        'color': '藍色',
        'material': '棉質',
        'style': '休閒',
        'category': '上衣'
    }
    
    # 測試各個agent
    agents_to_test = [
        "color_analyst",
        "fashion_designer", 
        "image_consultant",
        "trend_analyst",
        # "encourager"  # 先測試前幾個
    ]
    
    for agent_type in agents_to_test:
        print(f"\n🤖 測試 {agent_type} Agent")
        print("-" * 40)
        
        try:
            # 測試搜索標籤生成
            search_tags = generate_search_tags(agent_type, mock_tag, mock_user_profile)
            print(f"📝 生成搜索標籤: {search_tags}")
            
            # 測試agent查詢
            print(f"🔍 正在查詢 {agent_type}...")
            result = query_agent(agent_type, mock_tag, mock_user_profile)
            
            if result.startswith("❌"):
                print(f"   查詢失敗: {result}")
            else:
                print(f"   ✅ 查詢成功!")
                print(f"   回應長度: {len(result)} 字符")
                print(f"   回應預覽: {result[:100]}...")
            
        except Exception as e:
            print(f"   ❌ 測試 {agent_type} 時發生錯誤: {e}")
        
        print()

def test_custom_queries():
    """測試自定義查詢功能"""
    print("\n🔍 測試自定義查詢功能")
    print("=" * 40)
    
    custom_queries = [
        ("color_analyst", "什麼顏色適合暖色調膚色？"),
        ("fashion_designer", "職場女性的穿搭建議"),
        ("trend_analyst", "2025年春夏流行趨勢")
    ]
    
    for agent_type, query in custom_queries:
        print(f"\n🎯 查詢: {agent_type} - '{query}'")
        try:
            result = query_agent_with_custom_query(agent_type, query, limit=2)
            print(f"結果:\n{result}")
        except Exception as e:
            print(f"❌ 自定義查詢失敗: {e}")

def test_search_tag_generation():
    """測試搜索標籤生成邏輯"""
    print("\n🏷️ 測試搜索標籤生成")
    print("=" * 40)
    
    test_cases = [
        {
            "agent": "color_analyst",
            "tag": {"color": "紅色", "style": "正式"},
            "profile": {"skin_tone": "冷色調"},
            "expected_tags": ["color", "matching", "undertone"]
        },
        {
            "agent": "trend_analyst", 
            "tag": {"style": "潮流"},
            "profile": {},
            "expected_tags": ["trend", "current_trend", "seasonal"]
        },
        {
            "agent": "fashion_designer",
            "tag": {"color": "黑色"},
            "profile": {"style_preference": ["正式", "專業"]},
            "expected_tags": ["color", "style", "design", "formal"]
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n測試案例 {i}: {case['agent']}")
        tags = generate_search_tags(case["agent"], case["tag"], case["profile"])
        print(f"生成標籤: {tags}")
        
        # 檢查是否包含預期標籤
        expected = set(case["expected_tags"])
        generated = set(tags)
        
        if expected.issubset(generated):
            print("✅ 標籤生成正確")
        else:
            missing = expected - generated
            print(f"⚠️ 缺少預期標籤: {missing}")

def main():
    """主測試函數"""
    print("🚀 開始Agent整合測試")
    print("=" * 60)
    
    try:
        # 1. 測試搜索標籤生成
        test_search_tag_generation()
        
        # 2. 測試agent查詢
        test_agent_queries()
        
        # 3. 測試自定義查詢
        test_custom_queries()
        
        print("\n" + "=" * 60)
        print("✅ 所有整合測試完成！")
        print("\n💡 測試結果說明:")
        print("- 如果看到 '🤖 xxx 查詢成功，找到 N 筆相關資料'，表示查詢正常")
        print("- 如果出現錯誤，請檢查PostgreSQL連接和數據")
        print("- agents現在使用新的PostgreSQL向量搜索系統")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()