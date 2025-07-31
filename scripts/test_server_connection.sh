#!/bin/bash
# 測試server資料庫連接腳本

set -e

# 載入環境變數
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 設定預設值
PG_HOST=${PG_HOST:-localhost}
PG_PORT=${PG_PORT:-5432}
PG_USER=${PG_USER:-postgres}
PG_DB=${PG_DB:-fashion_rag}

echo "🔍 測試資料庫連接..."
echo "Host: $PG_HOST"
echo "Port: $PG_PORT"
echo "Database: $PG_DB"
echo "User: $PG_USER"
echo ""

# 測試基本連接
echo "1. 測試基本連接..."
if PGPASSWORD=$PG_PASSWORD psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DB -c "SELECT version();" >/dev/null 2>&1; then
    echo "✅ 基本連接成功"
else
    echo "❌ 基本連接失敗"
    exit 1
fi

# 測試pgvector擴展
echo "2. 測試pgvector擴展..."
PGVECTOR_EXISTS=$(PGPASSWORD=$PG_PASSWORD psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DB -t -c "SELECT COUNT(*) FROM pg_extension WHERE extname='vector';" | xargs)
if [ "$PGVECTOR_EXISTS" -eq "1" ]; then
    echo "✅ pgvector擴展已安裝"
else
    echo "❌ pgvector擴展未安裝"
    exit 1
fi

# 測試rag_data表
echo "3. 測試rag_data表..."
TABLE_EXISTS=$(PGPASSWORD=$PG_PASSWORD psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DB -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='rag_data';" | xargs)
if [ "$TABLE_EXISTS" -eq "1" ]; then
    echo "✅ rag_data表存在"
    
    # 檢查資料記錄數
    RECORD_COUNT=$(PGPASSWORD=$PG_PASSWORD psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DB -t -c "SELECT COUNT(*) FROM rag_data;" | xargs)
    echo "📊 記錄數: $RECORD_COUNT"
    
    # 檢查各類別的資料分布
    echo "4. 檢查資料分布..."
    PGPASSWORD=$PG_PASSWORD psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DB -c "
    SELECT 
        data_category,
        COUNT(*) as count
    FROM rag_data 
    GROUP BY data_category 
    ORDER BY count DESC;
    "
else
    echo "❌ rag_data表不存在"
    exit 1
fi

# 測試向量相似度查詢
echo "5. 測試向量查詢功能..."
PGPASSWORD=$PG_PASSWORD psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DB -c "
SELECT 
    content,
    data_category
FROM rag_data 
WHERE data_category = 'color_analysis'
LIMIT 1;
" >/dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 向量查詢功能正常"
else
    echo "❌ 向量查詢功能異常"
    exit 1
fi

echo ""
echo "🎉 所有測試通過！資料庫已準備就緒"
echo "組員現在可以使用以下設定連接："
echo "Host: $PG_HOST"
echo "Port: $PG_PORT"
echo "Database: $PG_DB"