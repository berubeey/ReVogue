"""
RAG查詢系統使用示例
這個示例展示如何在您的agent中使用RAG查詢功能
"""

from rag_query_helper import RAGQueryHelper
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """獲取資料庫連接（安全方式）"""
    import psycopg2
    import os
    
    pg_password = os.getenv('PG_PASSWORD')
    if not pg_password:
        raise ValueError("❌ 未設置 PG_PASSWORD 環境變數，請檢查 .env 文件")
    
    return psycopg2.connect(
        host=os.getenv('PG_HOST', 'localhost'),
        port=int(os.getenv('PG_PORT', 5432)),
        user=os.getenv('PG_USER', 'postgres'),
        password=pg_password,
        dbname=os.getenv('PG_DB', 'fashion_rag')
    )

def example_fashion_query():
    """時尚設計查詢示例"""
    print("👗 時尚設計查詢示例")
    print("=" * 40)
    
    helper = RAGQueryHelper()
    
    try:
        # 模擬一個查詢向量（在實際使用中，這會是用戶問題的embedding）
        # 這裡我們從數據庫中獲取一個真實的向量作為示例
        import psycopg2
        import os
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 獲取一個包含"style"標籤的向量
        cur.execute("""
            SELECT embedding, text 
            FROM rag_data_enhanced 
            WHERE 'style' = ANY(tags) AND vector_dimension = 384
            LIMIT 1
        """)
        
        row = cur.fetchone()
        if row:
            query_embedding = row[0]
            original_text = row[1]
            
            print(f"🎯 查詢問題模擬: 與風格相關的時尚建議")
            print(f"原始文本範例: {original_text[:80]}...")
            print()
            
            # 1. 只在時尚設計類別中搜索
            print("📂 1. 時尚設計專業搜索:")
            results = helper.search_by_category(
                query_embedding=query_embedding,
                category='fashion_design',
                limit=3
            )
            
            for i, result in enumerate(results, 1):
                print(f"   {i}. 相似度: {result['similarity']:.3f}")
                print(f"      內容: {result['text'][:60]}...")
                print(f"      標籤: {result['tags']}")
                print()
            
            # 2. 跨類別搜索（時尚+色彩+形象）
            print("🌈 2. 綜合時尚諮詢搜索:")
            results = helper.search_multi_category(
                query_embedding=query_embedding,
                categories=['fashion_design', 'color_analysis', 'image_consulting'],
                limit=5,
                min_similarity=0.3
            )
            
            for i, result in enumerate(results, 1):
                print(f"   {i}. [{result['category']}] 相似度: {result['similarity']:.3f}")
                print(f"      內容: {result['text'][:50]}...")
                print()
            
            # 3. 按標籤精確搜索
            print("🏷️ 3. 按標籤'style'搜索:")
            results = helper.search_by_tags(
                query_embedding=query_embedding,
                tags=['style'],
                limit=3
            )
            
            for i, result in enumerate(results, 1):
                print(f"   {i}. [{result['category']}] 相似度: {result['similarity']:.3f}")
                print(f"      標籤: {result['tags']}")
                print(f"      內容: {result['text'][:50]}...")
                print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 查詢失敗: {e}")
    finally:
        helper.close()

def example_color_analysis():
    """色彩分析查詢示例"""
    print("🎨 色彩分析查詢示例")
    print("=" * 40)
    
    helper = RAGQueryHelper()
    
    try:
        # 獲取色彩分析相關的統計
        stats = helper.get_category_stats()
        if 'color_analysis' in stats:
            print(f"📊 色彩分析數據: {sum(stats['color_analysis'].values())} 筆")
            for content_type, count in stats['color_analysis'].items():
                print(f"   - {content_type}: {count} 筆")
        
        # 模擬色彩相關查詢
        import psycopg2
        import os
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT embedding
            FROM rag_data_enhanced 
            WHERE category = 'color_analysis' AND vector_dimension = 384
            LIMIT 1
        """)
        
        row = cur.fetchone()
        if row:
            query_embedding = row[0]
            
            print(f"\n🎯 查詢: 色彩搭配建議")
            
            # 色彩分析專業搜索
            results = helper.search_by_category(
                query_embedding=query_embedding,
                category='color_analysis',
                limit=3
            )
            
            for i, result in enumerate(results, 1):
                print(f"   {i}. 相似度: {result['similarity']:.3f}")
                print(f"      類型: {result['content_type']}")
                print(f"      內容: {result['text'][:70]}...")
                print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 色彩查詢失敗: {e}")
    finally:
        helper.close()

def example_trend_analysis():
    """趨勢分析查詢示例"""
    print("📈 趨勢分析查詢示例")
    print("=" * 40)
    
    helper = RAGQueryHelper()
    
    try:
        # 獲取趨勢相關的熱門標籤
        trend_tags = helper.get_popular_tags(category='trend_analysis', limit=5)
        print("🏷️ 趨勢分析熱門標籤:")
        for tag, frequency in trend_tags:
            print(f"   - {tag}: {frequency} 次")
        
        print(f"\n🎯 查詢: 當前時尚趨勢")
        
        # 模擬趨勢查詢
        import psycopg2
        import os
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT embedding
            FROM rag_data_enhanced 
            WHERE category = 'trend_analysis' AND 'current_trend' = ANY(tags)
            LIMIT 1
        """)
        
        row = cur.fetchone()
        if row:
            query_embedding = row[0]
            
            # 搜索當前趨勢
            results = helper.search_by_tags(
                query_embedding=query_embedding,
                tags=['current_trend'],
                limit=3
            )
            
            for i, result in enumerate(results, 1):
                print(f"   {i}. [{result['category']}] 相似度: {result['similarity']:.3f}")
                print(f"      標籤: {result['tags']}")
                print(f"      內容: {result['text'][:60]}...")
                print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 趨勢查詢失敗: {e}")
    finally:
        helper.close()

def example_agent_integration():
    """展示如何在agent中集成RAG查詢"""
    print("🤖 Agent集成示例")
    print("=" * 40)
    
    # 這是一個簡化的agent類示例
    class FashionAgent:
        def __init__(self):
            self.rag_helper = RAGQueryHelper()
        
        def get_fashion_advice(self, user_query_embedding, query_type="general"):
            """根據用戶查詢提供時尚建議"""
            
            if query_type == "color":
                # 專注於色彩分析
                results = self.rag_helper.search_by_category(
                    query_embedding=user_query_embedding,
                    category='color_analysis',
                    limit=3
                )
            elif query_type == "trend":
                # 關注趨勢分析
                results = self.rag_helper.search_by_tags(
                    query_embedding=user_query_embedding,
                    tags=['trend', 'current_trend'],
                    limit=3
                )
            else:
                # 綜合搜索
                results = self.rag_helper.search_multi_category(
                    query_embedding=user_query_embedding,
                    categories=['fashion_design', 'color_analysis', 'image_consulting'],
                    limit=5,
                    min_similarity=0.4
                )
            
            return results
        
        def close(self):
            self.rag_helper.close()
    
    # 使用示例
    agent = FashionAgent()
    
    try:
        # 獲取測試數據
        import psycopg2
        import os
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT embedding FROM rag_data_enhanced 
            WHERE vector_dimension = 384 LIMIT 1
        """)
        
        row = cur.fetchone()
        if row:
            test_embedding = row[0]
            
            print("💬 模擬用戶查詢: '請給我一些色彩搭配建議'")
            results = agent.get_fashion_advice(test_embedding, "color")
            
            print("🎨 Agent回應:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. [{result['category']}] 相似度: {result['similarity']:.3f}")
                print(f"      建議: {result['text'][:80]}...")
                print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Agent測試失敗: {e}")
    finally:
        agent.close()

def main():
    """主函數 - 運行所有示例"""
    print("🚀 RAG查詢系統使用示例")
    print("=" * 60)
    print()
    
    # 1. 時尚查詢示例
    example_fashion_query()
    print("\n" + "="*60 + "\n")
    
    # 2. 色彩分析示例
    example_color_analysis()
    print("\n" + "="*60 + "\n")
    
    # 3. 趨勢分析示例
    example_trend_analysis()
    print("\n" + "="*60 + "\n")
    
    # 4. Agent集成示例
    example_agent_integration()
    
    print("\n" + "="*60)
    print("✅ 所有示例完成！")
    print("\n💡 使用提示:")
    print("- 在實際使用中，query_embedding 應該來自用戶問題的向量化")
    print("- 可以根據對話上下文選擇不同的搜索策略")
    print("- 建議根據相似度閾值過濾結果")
    print("- 記住關閉RAGQueryHelper連接以釋放資源")

if __name__ == "__main__":
    main()