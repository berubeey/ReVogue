import os
import json
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings

# 設定 embedding 模型
embedding_model = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")

# 檔案路徑
TAGS_FILE = "output_tags.json"  # 修改為正確的相對路徑

# 檢查檔案是否存在
if not os.path.exists(TAGS_FILE):
    raise FileNotFoundError(f"{TAGS_FILE} 不存在，請先執行 batch_image_tagging.py 生成標籤檔案")

# 讀取 JSON 檔案內容
with open(TAGS_FILE, "r", encoding="utf-8") as f:
    tags_data = json.load(f)

# 建立 Documents，將描述和標籤組合
documents = []
for image_name, data in tags_data.items():
    # 組合描述和標籤
    content = f"圖片描述: {data.get('item_description', '')}\n"
    content += f"風格: {', '.join(data.get('tags', {}).get('style', []))}\n"
    content += f"材質: {', '.join(data.get('tags', {}).get('material', []))}\n"
    content += f"分類: {', '.join(data.get('tags', {}).get('category', []))}\n"
    content += f"顏色: {', '.join(data.get('tags', {}).get('color', []))}\n"
    content += f"場合: {', '.join(data.get('tags', {}).get('occasion', []))}\n"
    content += f"情緒: {', '.join(data.get('tags', {}).get('mood', []))}\n"
    content += f"適合膚色: {', '.join(data.get('tags', {}).get('suitable_skin_tones', []))}"
    
    # Create document
    doc = Document(
        page_content=content,
        metadata={
            "photo_id": image_name,
            "item_description": data.get('item_description', ''),
            "style": data.get('tags', {}).get('style', []),
            "material": data.get('tags', {}).get('material', []),
            "category": data.get('tags', {}).get('category', []),
            "color": data.get('tags', {}).get('color', []),
            "occasion": data.get('tags', {}).get('occasion', []),
            "mood": data.get('tags', {}).get('mood', []),
            "suitable_skin_tones": data.get('tags', {}).get('suitable_skin_tones', [])
        }
    )
    documents.append(doc)

# 建立 FAISS 向量資料庫
vectorstore = FAISS.from_documents(documents, embedding_model)

# 儲存 FAISS 資料庫到本地
vectorstore.save_local("faiss_image_claim_index")

print("✅ FAISS 資料庫建立並儲存完成") 