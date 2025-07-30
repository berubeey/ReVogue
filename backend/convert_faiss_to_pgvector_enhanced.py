import os
import faiss
import pickle
import psycopg2
from pathlib import Path
import json

# 數據類別映射
CATEGORY_MAPPING = {
    'rag_color_index': 'color_analysis',
    'rag_fashion_index': 'fashion_design', 
    'rag_image_consultant_index': 'image_consulting',
    'rag_trend_index': 'trend_analysis',
    'rag_encourager_index': 'encouragement'
}

# 內容類型判斷函數
def determine_content_type(text, source_file):
    """根據文本內容和來源文件判斷內容類型"""
    text_lower = text.lower()
    file_lower = source_file.lower() if source_file else ""
    
    if 'guide' in file_lower or 'instruction' in text_lower:
        return 'guide'
    elif 'quote' in file_lower or '鼓勵' in text or 'motivation' in text_lower:
        return 'quote'
    elif 'template' in file_lower or 'format' in text_lower:
        return 'template'
    elif 'example' in file_lower or '例子' in text or '範例' in text:
        return 'example'
    elif 'image' in text_lower or '圖片' in text or '影像' in text:
        return 'image_analysis'
    else:
        return 'knowledge'

# 標籤提取函數
def extract_tags(text, category):
    """根據文本內容和類別提取標籤"""
    tags = []
    text_lower = text.lower()
    
    # 基礎標籤
    if '顏色' in text or 'color' in text_lower:
        tags.append('color')
    if '搭配' in text or 'matching' in text_lower:
        tags.append('matching')
    if '風格' in text or 'style' in text_lower:
        tags.append('style')
    if '趨勢' in text or 'trend' in text_lower:
        tags.append('trend')
    if '季節' in text or 'season' in text_lower:
        tags.append('seasonal')
    
    # 類別特定標籤
    if category == 'color_analysis':
        if '膚色' in text:
            tags.append('skin_tone')
        if '冷暖' in text:
            tags.append('undertone')
    elif category == 'fashion_design':
        if '設計' in text:
            tags.append('design')
        if '材質' in text:
            tags.append('material')
    elif category == 'trend_analysis':
        if '2024' in text or '2025' in text:
            tags.append('current_trend')
    
    return tags

def convert_single_index(index_path, pkl_path, category, cur):
    """轉換單個FAISS索引到PostgreSQL"""
    print(f"正在處理 {category} 類別...")
    
    # 讀取 FAISS index
    if not os.path.exists(index_path):
        print(f"警告：找不到索引文件 {index_path}")
        return 0
        
    try:
        index = faiss.read_index(index_path)
        vector_dim = index.d
        print(f"  向量維度: {vector_dim}, 向量數量: {index.ntotal}")
    except Exception as e:
        print(f"錯誤：無法讀取索引文件 {index_path} - {e}")
        return 0
    
    # 讀取 metadata
    try:
        with open(pkl_path, 'rb') as f:
            metadata = pickle.load(f)
            docstore = metadata[0]
            id_map = metadata[1]
            doc_ids = list(id_map.values())
            docs = [docstore._dict[doc_id] for doc_id in doc_ids]
    except Exception as e:
        print(f"錯誤：無法讀取metadata文件 {pkl_path} - {e}")
        return 0
    
    # 取得所有向量
    try:
        vectors = index.reconstruct_n(0, index.ntotal)
    except Exception as e:
        print(f"錯誤：無法提取向量 - {e}")
        return 0
    
    inserted_count = 0
    failed_count = 0
    
    for i, vec in enumerate(vectors):
        try:
            # 開始新的交易
            cur.execute("BEGIN")
            
            text = docs[i].page_content
            source_file = getattr(docs[i], 'source', None) if hasattr(docs[i], 'source') else None
            
            # 判斷內容類型
            content_type = determine_content_type(text, source_file)
            
            # 提取標籤
            tags = extract_tags(text, category)
            
            # 準備metadata
            metadata_json = {
                'original_index': os.path.basename(index_path),
                'doc_index': i,
                'vector_dimension': vector_dim
            }
            if source_file:
                metadata_json['source_file'] = source_file
            
            py_vec = [float(x) for x in vec]
            
            cur.execute("""
                INSERT INTO rag_data_enhanced 
                (text, embedding, vector_dimension, category, content_type, source_file, metadata, tags, language) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                text, 
                py_vec,
                vector_dim,
                category, 
                content_type,
                source_file,
                json.dumps(metadata_json),
                tags,
                'zh-TW'
            ))
            
            cur.execute("COMMIT")
            inserted_count += 1
            
            # 每處理50個記錄顯示一次進度
            if (i + 1) % 50 == 0:
                print(f"  已處理 {i + 1}/{len(vectors)} 個向量")
            
        except Exception as e:
            cur.execute("ROLLBACK")
            failed_count += 1
            if failed_count <= 3:  # 只顯示前3個錯誤
                print(f"  處理第 {i} 筆數據時出錯: {e}")
            elif failed_count == 4:
                print(f"  ... (更多錯誤被省略)")
            continue
    
    return inserted_count

# 主程序
if __name__ == "__main__":
    # 資料庫連線參數 (從環境變數讀取)
    PG_HOST = os.getenv('PG_HOST', 'localhost')
    PG_PORT = int(os.getenv('PG_PORT', 5432))
    PG_USER = os.getenv('PG_USER', 'postgres')
    PG_PASSWORD = os.getenv('PG_PASSWORD')
    PG_DB = os.getenv('PG_DB', 'fashion_rag')
    
    # 檢查必要的環境變數
    if not PG_PASSWORD:
        print("❌ 錯誤：未設置 PG_PASSWORD 環境變數")
        print("   請在 .env 文件中設置：PG_PASSWORD=your_password")
        exit(1)

    # 連線到 Postgres
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DB
        )
        cur = conn.cursor()
        print("成功連接到PostgreSQL")
        
        # 檢查表是否存在
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'rag_data_enhanced'
            );
        """)
        
        if not cur.fetchone()[0]:
            print("❌ 錯誤：請先執行以下命令創建表結構：")
            print("   psql -h localhost -U postgres -d fashion_rag -f create_enhanced_rag_table.sql")
            print("   psql -h localhost -U postgres -d fashion_rag -f fix_vector_dimensions.sql")
            exit(1)
        
        # 清空現有數據
        cur.execute("DELETE FROM rag_data_enhanced")
        conn.commit()
        print("🧹 清空現有數據")
        
        total_inserted = 0
        
        # 遍歷所有RAG索引目錄
        for index_dir, category in CATEGORY_MAPPING.items():
            index_path = f"agents/{index_dir}/index.faiss"
            pkl_path = f"agents/{index_dir}/index.pkl"
            
            if os.path.exists(index_path) and os.path.exists(pkl_path):
                count = convert_single_index(index_path, pkl_path, category, cur)
                total_inserted += count
                print(f"  ✅ {category} 類別完成，插入 {count} 筆數據")
            else:
                print(f"跳過 {category} 類別（找不到索引文件）")
        
        # 也處理根目錄的索引
        root_indexes = [
            ('rag_fashion_index/index.faiss', 'rag_fashion_index/index.pkl', 'fashion_design'),
            ('rag_color_index/index.faiss', 'rag_color_index/index.pkl', 'color_analysis'),
            ('rag_trend_index/index.faiss', 'rag_trend_index/index.pkl', 'trend_analysis'),
            ('rag_image_consultant_index/index.faiss', 'rag_image_consultant_index/index.pkl', 'image_consulting')
        ]
        
        for index_path, pkl_path, category in root_indexes:
            if os.path.exists(index_path) and os.path.exists(pkl_path):
                count = convert_single_index(index_path, pkl_path, category, cur)
                total_inserted += count
                print(f"  ✅ 根目錄 {category} 類別完成，插入 {count} 筆數據")
        
        conn.commit()
        print(f"\n✅ 轉換完成！總共插入 {total_inserted} 筆數據到 PostgreSQL")
        
        # 顯示統計信息
        cur.execute("""
            SELECT category, vector_dimension, COUNT(*) 
            FROM rag_data_enhanced 
            GROUP BY category, vector_dimension 
            ORDER BY category, vector_dimension
        """)
        
        stats = cur.fetchall()
        print("\n📊 數據分布統計：")
        for category, dim, count in stats:
            print(f"  {category} ({dim}維): {count} 筆")
            
    except Exception as e:
        print(f"錯誤：{e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()