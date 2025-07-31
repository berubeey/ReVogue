#!/bin/bash
# PostgreSQL資料庫還原腳本
# 用於在server上還原資料庫

set -e

# 檢查參數
if [ $# -eq 0 ]; then
    echo "使用方式: $0 backup_file.sql.gz"
    echo "範例: $0 backups/revogue_db_backup_20250731_195530.sql.gz"
    exit 1
fi

BACKUP_FILE=$1

# 檢查備份檔是否存在
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 備份檔不存在: $BACKUP_FILE"
    exit 1
fi

# 載入環境變數
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 設定預設值
PG_HOST=${PG_HOST:-localhost}
PG_PORT=${PG_PORT:-5432}
PG_USER=${PG_USER:-postgres}
PG_DB=${PG_DB:-fashion_rag}

echo "準備還原資料庫..."
echo "Host: $PG_HOST"
echo "Port: $PG_PORT"
echo "Database: $PG_DB"
echo "User: $PG_USER"
echo "Backup file: $BACKUP_FILE"

# 解壓縮備份檔（如果是.gz格式）
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "解壓縮備份檔..."
    TEMP_SQL_FILE="${BACKUP_FILE%.gz}"
    gunzip -c "$BACKUP_FILE" > "$TEMP_SQL_FILE"
    SQL_FILE="$TEMP_SQL_FILE"
else
    SQL_FILE="$BACKUP_FILE"
fi

# 等待PostgreSQL啟動
echo "等待PostgreSQL啟動..."
for i in {1..30}; do
    if PGPASSWORD=$PG_PASSWORD psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
        echo "✅ PostgreSQL已啟動"
        break
    fi
    echo "等待PostgreSQL啟動... ($i/30)"
    sleep 2
done

# 執行還原
echo "開始還原資料庫..."
PGPASSWORD=$PG_PASSWORD psql \
    -h $PG_HOST \
    -p $PG_PORT \
    -U $PG_USER \
    -d $PG_DB \
    -f "$SQL_FILE" \
    --verbose

if [ $? -eq 0 ]; then
    echo "✅ 資料庫還原成功"
    
    # 驗證資料
    echo "驗證資料..."
    RECORD_COUNT=$(PGPASSWORD=$PG_PASSWORD psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DB -t -c "SELECT COUNT(*) FROM rag_data;" | xargs)
    echo "📊 rag_data表記錄數: $RECORD_COUNT"
    
    # 清理臨時檔案
    if [[ $BACKUP_FILE == *.gz ]] && [ -f "$TEMP_SQL_FILE" ]; then
        rm "$TEMP_SQL_FILE"
        echo "🗑️  已清理臨時檔案"
    fi
else
    echo "❌ 資料庫還原失敗"
    exit 1
fi