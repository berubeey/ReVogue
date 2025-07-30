import os
import faiss
import pickle
import psycopg2

# 參數
FAISS_INDEX_PATH = 'my-app/backend/rag_fashion_index/index.faiss'
PKL_PATH = 'my-app/backend/rag_fashion_index/index.pkl'
PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASSWORD = os.getenv('PG_PASSWORD', 'postgres')
PG_DB = os.getenv('PG_DB', 'postgres')
TABLE_NAME = 'rag_data'

# 1. 讀取 FAISS index
index = faiss.read_index(FAISS_INDEX_PATH)

# 2. 讀取 metadata
with open(PKL_PATH, 'rb') as f:
    metadata = pickle.load(f)
    docstore = metadata[0]
    id_map = metadata[1]
    doc_ids = list(id_map.values())
    docs = [docstore._dict[doc_id] for doc_id in doc_ids]

# 3. 取得所有向量
vectors = index.reconstruct_n(0, index.ntotal)  # shape: (N, dim)

# 4. 連線到 Postgres
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    user='postgres',
    password='revogue2025',
    dbname='fashion_rag'
)
cur = conn.cursor()

# 5. 啟用 pgvector extension
cur.execute('CREATE EXTENSION IF NOT EXISTS vector;')

# 6. 建立 table（假設向量維度與 index 相同）
vector_dim = vectors.shape[1]
cur.execute(f'''
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id SERIAL PRIMARY KEY,
    text TEXT,
    embedding vector({vector_dim})
);
''')

# 7. 批次寫入
for i, vec in enumerate(vectors):
    text = docs[i].page_content  # 或 docs[i].get('text', '')，視你的 Document 結構
    py_vec = [float(x) for x in vec]  # 轉成 Python float
    cur.execute(
        f"INSERT INTO {TABLE_NAME} (text, embedding) VALUES (%s, %s)",
        (text, py_vec)
    )

conn.commit()
cur.close()
conn.close()

print('FAISS 向量與 metadata 已匯入 pgvector！') 