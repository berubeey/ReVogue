import os
import psycopg2
from typing import List, Dict, Optional, Tuple
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RAGQueryHelper:
    """增強的RAG查詢助手，支持分類標籤篩選"""
    
    def __init__(self):
        # 從環境變數獲取資料庫連接參數
        pg_password = os.getenv('PG_PASSWORD')
        if not pg_password:
            raise ValueError("❌ 未設置 PG_PASSWORD 環境變數，請檢查 .env 文件")
        
        self.conn = psycopg2.connect(
            host=os.getenv('PG_HOST', 'localhost'),
            port=int(os.getenv('PG_PORT', 5432)),
            user=os.getenv('PG_USER', 'postgres'),
            password=pg_password,
            dbname=os.getenv('PG_DB', 'fashion_rag')
        )
    
    def search_by_category(
        self, 
        query_embedding: List[float], 
        category: str, 
        limit: int = 5,
        content_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict]:
        """根據類別搜索相似向量"""
        
        cur = self.conn.cursor()
        
        # 構建查詢條件
        conditions = ["category = %s"]
        params = [category]
        
        if content_type:
            conditions.append("content_type = %s")
            params.append(content_type)
            
        if tags:
            conditions.append("tags && %s")  # 數組重疊操作符
            params.append(tags)
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT id, text, category, content_type, source_file, tags, metadata,
                   1 - (embedding <=> %s::vector) as similarity
            FROM rag_data_enhanced 
            WHERE {where_clause}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        
        params = [query_embedding] + params + [query_embedding, limit]
        cur.execute(query, params)
        
        results = []
        for row in cur.fetchall():
            results.append({
                'id': row[0],
                'text': row[1],
                'category': row[2],
                'content_type': row[3],
                'source_file': row[4],
                'tags': row[5],
                'metadata': row[6],
                'similarity': row[7]
            })
        
        cur.close()
        return results
    
    def search_multi_category(
        self,
        query_embedding: List[float],
        categories: List[str],
        limit: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict]:
        """跨多個類別搜索"""
        
        cur = self.conn.cursor()
        
        # 使用IN操作符而不是ANY來處理枚舉類型
        placeholders = ','.join(['%s'] * len(categories))
        query = f"""
            SELECT id, text, category, content_type, source_file, tags, metadata,
                   1 - (embedding <=> %s::vector) as similarity
            FROM rag_data_enhanced 
            WHERE category::text IN ({placeholders}) AND (1 - (embedding <=> %s::vector)) >= %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        
        params = [query_embedding] + categories + [query_embedding, min_similarity, query_embedding, limit]
        cur.execute(query, params)
        
        results = []
        for row in cur.fetchall():
            results.append({
                'id': row[0],
                'text': row[1],
                'category': row[2],
                'content_type': row[3],
                'source_file': row[4],
                'tags': row[5],
                'metadata': row[6],
                'similarity': row[7]
            })
        
        cur.close()
        return results
    
    def get_category_stats(self) -> Dict[str, int]:
        """獲取各類別的數據統計"""
        cur = self.conn.cursor()
        
        cur.execute("""
            SELECT category, content_type, COUNT(*) 
            FROM rag_data_enhanced 
            GROUP BY category, content_type 
            ORDER BY category, content_type
        """)
        
        stats = {}
        for row in cur.fetchall():
            category = row[0]
            content_type = row[1]
            count = row[2]
            
            if category not in stats:
                stats[category] = {}
            stats[category][content_type] = count
        
        cur.close()
        return stats
    
    def get_popular_tags(self, category: Optional[str] = None, limit: int = 20) -> List[Tuple[str, int]]:
        """獲取熱門標籤"""
        cur = self.conn.cursor()
        
        if category:
            query = """
                SELECT tag, COUNT(*) as frequency
                FROM (
                    SELECT unnest(tags) as tag 
                    FROM rag_data_enhanced 
                    WHERE category = %s
                ) t
                GROUP BY tag
                ORDER BY frequency DESC
                LIMIT %s
            """
            cur.execute(query, [category, limit])
        else:
            query = """
                SELECT tag, COUNT(*) as frequency
                FROM (
                    SELECT unnest(tags) as tag 
                    FROM rag_data_enhanced
                ) t
                GROUP BY tag
                ORDER BY frequency DESC
                LIMIT %s
            """
            cur.execute(query, [limit])
        
        results = cur.fetchall()
        cur.close()
        return results
    
    def search_by_tags(
        self,
        query_embedding: List[float],
        tags: List[str],
        limit: int = 5,
        match_all: bool = False
    ) -> List[Dict]:
        """根據標籤搜索"""
        cur = self.conn.cursor()
        
        if match_all:
            # 必須包含所有標籤
            condition = "tags @> %s"
        else:
            # 包含任一標籤
            condition = "tags && %s"
        
        query = f"""
            SELECT id, text, category, content_type, source_file, tags, metadata,
                   1 - (embedding <=> %s::vector) as similarity
            FROM rag_data_enhanced 
            WHERE {condition}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        
        cur.execute(query, [query_embedding, tags, query_embedding, limit])
        
        results = []
        for row in cur.fetchall():
            results.append({
                'id': row[0],
                'text': row[1],
                'category': row[2],
                'content_type': row[3],
                'source_file': row[4],
                'tags': row[5],
                'metadata': row[6],
                'similarity': row[7]
            })
        
        cur.close()
        return results
    
    def close(self):
        """關閉資料庫連接"""
        if self.conn:
            self.conn.close()

# 使用示例函數
def example_usage():
    """使用示例"""
    helper = RAGQueryHelper()
    
    try:
        # 獲取統計信息
        stats = helper.get_category_stats()
        print("數據統計:", stats)
        
        # 獲取熱門標籤
        popular_tags = helper.get_popular_tags(limit=10)
        print("熱門標籤:", popular_tags)
        
        # 假設的查詢向量（實際使用時需要從embedding模型獲取）
        dummy_embedding = [0.1] * 1536
        
        # 按類別搜索
        results = helper.search_by_category(
            query_embedding=dummy_embedding,
            category='color_analysis',
            limit=3
        )
        print("色彩分析結果:", len(results))
        
        # 按標籤搜索
        tag_results = helper.search_by_tags(
            query_embedding=dummy_embedding,
            tags=['color', 'style'],
            limit=3
        )
        print("標籤搜索結果:", len(tag_results))
        
    finally:
        helper.close()

if __name__ == "__main__":
    example_usage()