-- 創建增強的RAG數據表，支持分類標籤
-- 使用這個腳本來升級您的現有表結構

-- 首先啟用pgvector擴展
CREATE EXTENSION IF NOT EXISTS vector;

-- 創建枚舉類型來定義數據分類
CREATE TYPE data_category AS ENUM (
    'color_analysis',     -- 色彩分析
    'fashion_design',     -- 時尚設計
    'image_consulting',   -- 形象顧問
    'trend_analysis',     -- 趨勢分析
    'encouragement',      -- 鼓勵語
    'general'            -- 通用類型
);

-- 創建內容類型枚舉
CREATE TYPE content_type AS ENUM (
    'knowledge',         -- 知識文檔
    'guide',            -- 指導手冊
    'quote',            -- 引用/格言
    'template',         -- 模板
    'example',          -- 示例
    'image_analysis'    -- 圖片分析
);

-- 創建新的增強表結構
CREATE TABLE IF NOT EXISTS rag_data_enhanced (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding vector(1536),  -- 假設使用OpenAI embeddings的維度
    category data_category NOT NULL DEFAULT 'general',
    content_type content_type NOT NULL DEFAULT 'knowledge',
    source_file VARCHAR(255),  -- 來源文件名
    metadata JSONB,           -- 額外的元數據
    tags TEXT[],             -- 標籤陣列
    language VARCHAR(10) DEFAULT 'zh-TW',  -- 語言標識
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 創建索引來優化查詢性能
CREATE INDEX IF NOT EXISTS idx_rag_data_category ON rag_data_enhanced(category);
CREATE INDEX IF NOT EXISTS idx_rag_data_content_type ON rag_data_enhanced(content_type);
CREATE INDEX IF NOT EXISTS idx_rag_data_tags ON rag_data_enhanced USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_rag_data_embedding ON rag_data_enhanced USING ivfflat (embedding vector_cosine_ops);

-- 創建更新時間觸發器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_rag_data_updated_at 
    BEFORE UPDATE ON rag_data_enhanced 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 如果您有現有的rag_data表，可以遷移數據
-- INSERT INTO rag_data_enhanced (text, embedding, category)
-- SELECT text, embedding, 'general' FROM rag_data;

-- 創建視圖來方便查詢不同類別的數據
CREATE OR REPLACE VIEW color_analysis_data AS
SELECT * FROM rag_data_enhanced WHERE category = 'color_analysis';

CREATE OR REPLACE VIEW fashion_design_data AS
SELECT * FROM rag_data_enhanced WHERE category = 'fashion_design';

CREATE OR REPLACE VIEW image_consulting_data AS
SELECT * FROM rag_data_enhanced WHERE category = 'image_consulting';

CREATE OR REPLACE VIEW trend_analysis_data AS
SELECT * FROM rag_data_enhanced WHERE category = 'trend_analysis';

CREATE OR REPLACE VIEW encouragement_data AS
SELECT * FROM rag_data_enhanced WHERE category = 'encouragement';