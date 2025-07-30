import os
import psycopg2
import numpy as np
from rag_query_helper import RAGQueryHelper
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """獲取資料庫連接（安全方式）"""
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

def test_basic_data_info():
    """測試基本數據信息"""
    print("🔍 基本數據統計測試")
    print("=" * 50)
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 總數據統計
    cur.execute("SELECT COUNT(*) FROM rag_data_enhanced")
    total_count = cur.fetchone()[0]
    print(f"📊 總數據量: {total_count} 筆")
    
    # 按類別統計
    cur.execute("""
        SELECT category, vector_dimension, COUNT(*) 
        FROM rag_data_enhanced 
        GROUP BY category, vector_dimension 
        ORDER BY category
    """)
    
    print("\n📈 分類統計:")
    for category, dim, count in cur.fetchall():
        print(f"  {category} ({dim}維): {count} 筆")
    
    # 按內容類型統計
    cur.execute("""
        SELECT content_type, COUNT(*) 
        FROM rag_data_enhanced 
        GROUP BY content_type 
        ORDER BY COUNT(*) DESC
    """)
    
    print("\n📝 內容類型統計:")
    for content_type, count in cur.fetchall():
        print(f"  {content_type}: {count} 筆")
    
    # 查看一些樣本數據
    cur.execute("""
        SELECT category, content_type, LEFT(text, 100), tags
        FROM rag_data_enhanced 
        LIMIT 5
    """)
    
    print("\n📄 樣本數據:")
    for i, (category, content_type, text_preview, tags) in enumerate(cur.fetchall(), 1):
        print(f"  {i}. [{category}] {content_type}")
        print(f"     文本: {text_preview}...")
        print(f"     標籤: {tags}")
        print()
    
    cur.close()
    conn.close()

def test_vector_similarity_search():
    """測試向量相似度搜索"""
    print("🔍 向量相似度搜索測試")
    print("=" * 50)
    
    helper = RAGQueryHelper()
    
    try:
        # 獲取一個真實的向量作為查詢向量
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 獲取一個384維的向量作為測試
        cur.execute("""
            SELECT embedding, text, category
            FROM rag_data_enhanced 
            WHERE vector_dimension = 384 
            LIMIT 1
        """)
        
        row = cur.fetchone()
        if row:
            test_embedding = row[0]  # PostgreSQL會自動轉換為Python list
            original_text = row[1]
            original_category = row[2]
            
            print(f"🎯 使用測試向量來自: [{original_category}]")
            print(f"   原始文本: {original_text[:100]}...")
            print()
            
            # 測試按類別搜索
            print("📂 按類別搜索測試:")
            results = helper.search_by_category(
                query_embedding=test_embedding,
                category=original_category,
                limit=3
            )
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. 相似度: {result['similarity']:.4f}")
                print(f"     類別: {result['category']}")
                print(f"     文本: {result['text'][:80]}...")
                print(f"     標籤: {result['tags']}")
                print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 向量搜索測試失敗: {e}")
    finally:
        helper.close()

def test_category_and_tag_filtering():
    """測試分類和標籤篩選"""
    print("🔍 分類和標籤篩選測試")
    print("=" * 50)
    
    helper = RAGQueryHelper()
    
    try:
        # 測試統計功能
        print("📊 各類別統計:")
        stats = helper.get_category_stats()
        for category, content_types in stats.items():
            print(f"  {category}:")
            for content_type, count in content_types.items():
                print(f"    - {content_type}: {count} 筆")
        
        print("\n🏷️ 熱門標籤 (前10個):")
        popular_tags = helper.get_popular_tags(limit=10)
        for tag, frequency in popular_tags:
            print(f"  {tag}: {frequency} 次")
        
        # 測試按標籤搜索
        if popular_tags:
            # 使用最熱門的標籤進行測試
            top_tag = popular_tags[0][0]
            print(f"\n🔖 按標籤 '{top_tag}' 搜索測試:")
            
            # 獲取一個測試向量
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT embedding 
                FROM rag_data_enhanced 
                WHERE %s = ANY(tags) AND vector_dimension = 384
                LIMIT 1
            """, (top_tag,))
            
            row = cur.fetchone()
            if row:
                test_embedding = row[0]
                
                results = helper.search_by_tags(
                    query_embedding=test_embedding,
                    tags=[top_tag],
                    limit=3
                )
                
                for i, result in enumerate(results, 1):
                    print(f"  {i}. 相似度: {result['similarity']:.4f}")
                    print(f"     類別: {result['category']}")
                    print(f"     標籤: {result['tags']}")
                    print(f"     文本: {result['text'][:60]}...")
                    print()
            
            cur.close()
            conn.close()
        
    except Exception as e:
        print(f"❌ 分類和標籤測試失敗: {e}")
    finally:
        helper.close()

def test_multi_category_search():
    """測試多類別搜索"""
    print("🔍 多類別搜索測試")
    print("=" * 50)
    
    helper = RAGQueryHelper()
    
    try:
        # 獲取測試向量
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT embedding 
            FROM rag_data_enhanced 
            WHERE vector_dimension = 384
            LIMIT 1
        """)
        
        row = cur.fetchone()
        if row:
            test_embedding = row[0]
            
            # 測試跨多個類別搜索
            categories = ['color_analysis', 'fashion_design', 'trend_analysis']
            print(f"🎯 跨類別搜索: {', '.join(categories)}")
            
            results = helper.search_multi_category(
                query_embedding=test_embedding,
                categories=categories,
                limit=5,
                min_similarity=0.5
            )
            
            print(f"📝 找到 {len(results)} 個結果:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. [{result['category']}] 相似度: {result['similarity']:.4f}")
                print(f"     文本: {result['text'][:70]}...")
                print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 多類別搜索測試失敗: {e}")
    finally:
        helper.close()

def test_performance():
    """測試查詢性能"""
    print("🔍 性能測試")
    print("=" * 50)
    
    import time
    
    helper = RAGQueryHelper()
    
    try:
        # 獲取測試向量
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT embedding 
            FROM rag_data_enhanced 
            WHERE vector_dimension = 384
            LIMIT 1
        """)
        
        row = cur.fetchone()
        if row:
            test_embedding = row[0]
            
            # 測試單類別搜索性能
            start_time = time.time()
            results = helper.search_by_category(
                query_embedding=test_embedding,
                category='fashion_design',
                limit=10
            )
            end_time = time.time()
            
            print(f"⚡ 單類別搜索 (10個結果): {(end_time - start_time)*1000:.2f}ms")
            print(f"   找到 {len(results)} 個結果")
            
            # 測試多類別搜索性能
            start_time = time.time()
            results = helper.search_multi_category(
                query_embedding=test_embedding,
                categories=['color_analysis', 'fashion_design', 'trend_analysis'],
                limit=10
            )
            end_time = time.time()
            
            print(f"⚡ 多類別搜索 (10個結果): {(end_time - start_time)*1000:.2f}ms")
            print(f"   找到 {len(results)} 個結果")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 性能測試失敗: {e}")
    finally:
        helper.close()

def main():
    """主測試函數"""
    print("🚀 開始RAG查詢系統全面測試")
    print("=" * 60)
    print()
    
    try:
        # 1. 基本數據信息測試
        test_basic_data_info()
        print("\n" + "="*60 + "\n")
        
        # 2. 向量相似度搜索測試
        test_vector_similarity_search()
        print("\n" + "="*60 + "\n")
        
        # 3. 分類和標籤篩選測試
        test_category_and_tag_filtering()
        print("\n" + "="*60 + "\n")
        
        # 4. 多類別搜索測試
        test_multi_category_search()
        print("\n" + "="*60 + "\n")
        
        # 5. 性能測試
        test_performance()
        
        print("\n" + "="*60)
        print("✅ 所有測試完成！")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()