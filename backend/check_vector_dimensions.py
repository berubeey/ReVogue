import faiss
import os

def check_index_dimensions():
    """檢查所有FAISS索引的向量維度"""
    index_paths = [
        'rag_fashion_index/index.faiss',
        'rag_color_index/index.faiss',
        'rag_trend_index/index.faiss',
        'rag_image_consultant_index/index.faiss',
        'rag_encourager_index/index.faiss',
        'faiss_image_claim_index/index.faiss',
        'image_fashion_index/index.faiss'
    ]
    
    print("🔍 檢查所有FAISS索引的向量維度：\n")
    
    for path in index_paths:
        if os.path.exists(path):
            try:
                index = faiss.read_index(path)
                print(f"📁 {path}")
                print(f"   維度: {index.d}")
                print(f"   向量數量: {index.ntotal}")
                print(f"   索引類型: {type(index).__name__}")
                print()
            except Exception as e:
                print(f"❌ {path}: 讀取失敗 - {e}")
                print()
        else:
            print(f"⚠️  {path}: 文件不存在")
            print()

if __name__ == "__main__":
    check_index_dimensions()