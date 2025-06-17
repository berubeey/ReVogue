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
    content = f"圖片描述: {data.get('description', '')}\n"
    if 'tags' in data:
        tags = data['tags']
        content += f"風格: {tags.get('style', '')}\n"
        content += f"材質: {tags.get('material', '')}\n"
        content += f"分類: {tags.get('category', '')}\n"
        content += f"顏色: {tags.get('color', '')}\n"
        content += f"場合: {tags.get('occasion', '')}\n"
        content += f"情緒: {tags.get('mood', '')}\n"
        content += f"適合膚色: {tags.get('suitable_skin_tones', '')}"
    
    # 建立更豐富的元數據
    metadata = {
        "image_name": image_name,
        "description": data.get('description', ''),
        "style": tags.get('style', '') if 'tags' in data else '',
        "material": tags.get('material', '') if 'tags' in data else '',
        "category": tags.get('category', '') if 'tags' in data else '',
        "color": tags.get('color', '') if 'tags' in data else '',
        "occasion": tags.get('occasion', '') if 'tags' in data else '',
        "mood": tags.get('mood', '') if 'tags' in data else '',
        "suitable_skin_tones": tags.get('suitable_skin_tones', '') if 'tags' in data else ''
    }
    
    doc = Document(page_content=content, metadata=metadata)
    documents.append(doc)

# 建立 FAISS 向量資料庫
vectorstore = FAISS.from_documents(documents, embedding_model)

# 儲存 FAISS 資料庫到本地
vectorstore.save_local("faiss_image_claim_index")

print("✅ FAISS 資料庫建立並儲存完成") 