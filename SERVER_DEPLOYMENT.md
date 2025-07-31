# ReVogue Server部署指南

本文檔說明如何將ReVogue系統部署到實驗室server，供組員共同使用PostgreSQL資料庫。

## 🏗️ 部署架構

```
實驗室Server
├── PostgreSQL (pgvector) - 端口5432
├── 共享資料庫：fashion_rag  
└── 364筆向量資料記錄

組員本機
├── Next.js前端 - 端口3000
├── FastAPI後端 - 端口8000
└── 連接到server PostgreSQL
```

## 📋 部署前準備

### Server需求
- Ubuntu/CentOS Linux
- Docker & Docker Compose
- 至少2GB RAM
- 10GB可用磁碟空間
- 開放5432端口（內網）

### 組員本機需求
- 能連接到實驗室內網
- Python 3.9+
- Node.js 18+

## 🚀 Server部署步驟

### 1. 在Server上複製專案
```bash
git clone https://github.com/berubeey/ReVogue.git
cd ReVogue
```

### 2. 設定Server環境變數
```bash
# 複製並編輯環境設定
cp .env.example .env
nano .env
```

設定內容：
```bash
# PostgreSQL Database Configuration
PG_HOST=0.0.0.0  # 允許外部連接
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_strong_server_password
PG_DB=fashion_rag

# Google AI API (可選，主要在client端使用)
GOOGLE_API_KEY=your_google_api_key
```

### 3. 啟動PostgreSQL Server
```bash
# 使用server專用配置
docker-compose -f docker-compose.server.yml up -d

# 檢查狀態
docker-compose -f docker-compose.server.yml ps
docker logs revogue-pgvector-server
```

### 4. 還原資料庫（從本機備份）
```bash
# 從本機傳輸備份檔到server
scp backups/revogue_db_backup_*.sql.gz user@server:/path/to/ReVogue/

# 在server上還原
./scripts/restore_database.sh backups/revogue_db_backup_*.sql.gz
```

### 5. 驗證部署
```bash
# 測試資料庫連接
./scripts/test_server_connection.sh

# 檢查資料
docker exec revogue-pgvector-server psql -U postgres -d fashion_rag -c "SELECT COUNT(*) FROM rag_data;"
```

## 👥 組員本機設定

### 1. 更新環境變數
每位組員在本機`.env`檔案中設定：
```bash
# 連接到實驗室server
PG_HOST=實驗室server的IP地址
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=server上設定的密碼
PG_DB=fashion_rag

# 本機API金鑰
GOOGLE_API_KEY=your_personal_api_key
```

### 2. 測試連接
```bash
cd backend
python test_query_system.py
```

### 3. 啟動本機開發環境
```bash
# 後端
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py

# 前端
npm install
npm run dev
```

## 🔒 安全設定

### Server端
```bash
# 設定防火牆（僅允許實驗室內網）
sudo ufw allow from 192.168.1.0/24 to any port 5432
sudo ufw enable

# 定期備份
crontab -e
# 每日凌晨2點備份
0 2 * * * cd /path/to/ReVogue && ./scripts/backup_database.sh
```

### 組員端
- 使用強密碼
- 不要將`.env`檔案提交到git
- 僅在實驗室內網使用

## 📊 監控和維護

### 查看系統狀態
```bash
# 資料庫連接數
docker exec revogue-pgvector-server psql -U postgres -d fashion_rag -c "SELECT count(*) FROM pg_stat_activity;"

# 資料庫大小
docker exec revogue-pgvector-server psql -U postgres -d fashion_rag -c "SELECT pg_size_pretty(pg_database_size('fashion_rag'));"

# 系統資源
docker stats revogue-pgvector-server
```

### 日誌檢查
```bash
# PostgreSQL日誌
docker logs revogue-pgvector-server

# 系統日誌
journalctl -u docker
```

## 🆘 故障排除

### 常見問題

1. **連接被拒絕**
   ```bash
   # 檢查防火牆
   sudo ufw status
   # 檢查PostgreSQL是否監聽外部連接
   docker exec revogue-pgvector-server netstat -ln | grep 5432
   ```

2. **權限錯誤**
   ```bash
   # 檢查PostgreSQL用戶權限
   docker exec revogue-pgvector-server psql -U postgres -c "\du"
   ```

3. **資料不同步**
   ```bash
   # 重新同步資料
   ./scripts/backup_database.sh  # 在有最新資料的機器
   ./scripts/restore_database.sh backup_file.sql.gz  # 在需要同步的機器
   ```

## 📞 聯絡資訊

如有部署問題，請聯絡：
- 專案負責人：[your-contact]
- 技術支援：[tech-support]

---

*部署完成後，所有組員都能共享同一個PostgreSQL資料庫，提高協作效率！* 🚀