-- 修正向量維度問題
-- 由於您的向量有不同維度，我們需要重新設計表結構

-- 1. 刪除現有的表（如果存在）
DROP TABLE IF EXISTS rag_data_enhanced CASCADE;

-- 2. 重新創建表，不固定向量維度，讓PostgreSQL自動推斷
CREATE TABLE IF NOT EXISTS rag_data_enhanced (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding vector,  -- 不指定維度，讓系統自動適應
    vector_dimension INTEGER NOT NULL,  -- 記錄向量的實際維度
    category data_category NOT NULL DEFAULT 'general',
    content_type content_type NOT NULL DEFAULT 'knowledge',
    source_file VARCHAR(255),
    metadata JSONB,
    tags TEXT[],
    language VARCHAR(10) DEFAULT 'zh-TW',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. 創建索引來優化查詢性能
CREATE INDEX IF NOT EXISTS idx_rag_data_category ON rag_data_enhanced(category);
CREATE INDEX IF NOT EXISTS idx_rag_data_content_type ON rag_data_enhanced(content_type);
CREATE INDEX IF NOT EXISTS idx_rag_data_tags ON rag_data_enhanced USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_rag_data_vector_dim ON rag_data_enhanced(vector_dimension);

-- 注意：向量索引需要在插入數據後根據實際維度創建
-- 我們將在轉換腳本中動態創建適當的向量索引