#!/bin/bash
# PostgreSQL資料庫備份腳本
# 用於將本地資料庫遷移到server

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

# 建立備份目錄
mkdir -p backups

# 取得時間戳記
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backups/revogue_db_backup_${TIMESTAMP}.sql"

echo "開始備份資料庫..."
echo "Host: $PG_HOST"
echo "Port: $PG_PORT"
echo "Database: $PG_DB"
echo "User: $PG_USER"

# 執行備份
PGPASSWORD=$PG_PASSWORD pg_dump \
    -h $PG_HOST \
    -p $PG_PORT \
    -U $PG_USER \
    -d $PG_DB \
    --verbose \
    --clean \
    --no-owner \
    --no-privileges \
    > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ 備份成功：$BACKUP_FILE"
    echo "📊 備份檔案大小：$(ls -lh $BACKUP_FILE | awk '{print $5}')"
    
    # 壓縮備份檔
    gzip $BACKUP_FILE
    echo "🗜️  已壓縮：${BACKUP_FILE}.gz"
else
    echo "❌ 備份失敗"
    exit 1
fi