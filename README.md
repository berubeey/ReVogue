# ReVogue - AI時尚穿搭顧問系統

一個基於多智能體架構的AI時尚穿搭顧問系統，結合PostgreSQL向量資料庫與RAG技術，為使用者提供個人化的時尚建議。

## ✨ 核心特色

- 🤖 **多智能體協作**：五個專業AI代理協同工作
- 🗄️ **PostgreSQL向量資料庫**：使用pgvector進行高效向量相似度搜尋
- 🎨 **個人化分析**：色彩分析、風格建議、趨勢預測
- 📱 **現代化介面**：基於Next.js的響應式聊天介面
- 🔍 **RAG檢索增強**：智能知識檢索與生成
- 🐳 **容器化部署**：完整的Docker支援

## 🏗️ 系統架構

### 前端
- **Next.js 14** - React框架
- **TypeScript** - 型別安全
- **Tailwind CSS** - 樣式框架
- **Framer Motion** - 動畫效果

### 後端
- **FastAPI** - Python Web框架
- **PostgreSQL + pgvector** - 向量資料庫
- **LangChain** - RAG框架
- **Google Gemini** - AI模型
- **Docker** - 容器化部署

### AI代理系統
| 代理名稱 | 職責 | 專業領域 |
|---------|------|----------|
| 🎨 色彩分析師 | 分析膚色、髮色與單品色彩搭配 | 色彩理論、膚色匹配 |
| 👔 形象顧問 | 根據職業與場合建議風格 | 商務穿搭、形象管理 |
| ✂️ 服裝設計師 | 整合建議並提出完整穿搭方案 | 服裝搭配、設計美學 |
| 📈 潮流分析師 | 提供最新流行趨勢資訊 | 時尚趨勢、市場分析 |
| 💪 鼓勵員 | 提供情感支持與自信建議 | 心理輔導、正向激勵 |

## 🚀 快速開始

### 環境需求
- Python 3.9+
- Node.js 18+
- PostgreSQL 13+
- Docker & Docker Compose

### 1. 複製專案
```bash
git clone https://github.com/berubeey/ReVogue.git
cd ReVogue
```

### 2. 環境變數設定
創建 `.env` 檔案：
```bash
# Google AI
GOOGLE_API_KEY=your_google_api_key

# PostgreSQL Database
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_password
PG_DB=fashion_rag
```

### 3. 使用Docker Compose啟動
```bash
# 確保已設定環境變數
export PG_PASSWORD=your_secure_password
docker-compose up -d
```

### 4. 手動安裝（開發環境）

#### 後端設置
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 前端設置
```bash
npm install
npm run dev
```

#### PostgreSQL設置
```bash
# 建立資料庫和擴展
psql -U postgres
CREATE DATABASE fashion_rag;
\c fashion_rag
CREATE EXTENSION vector;
```

#### 資料庫初始化
```bash
cd backend
python convert_faiss_to_pgvector_enhanced.py  # 從FAISS遷移資料
python test_query_system.py  # 測試系統
```

## 📂 專案結構

```
ReVogue/
├── app/                          # Next.js前端應用
│   ├── components/              # React組件
│   ├── globals.css             # 全域樣式
│   └── page.tsx                # 主頁面
├── backend/                     # Python後端
│   ├── agents/                 # AI代理系統
│   │   ├── agent_rag_templates.py    # RAG查詢模板
│   │   ├── color_analyst_agent.py    # 色彩分析代理
│   │   ├── fashion_designer_agent.py # 服裝設計代理
│   │   └── ...                 # 其他代理
│   ├── convert_faiss_to_pgvector_enhanced.py  # 資料遷移工具
│   ├── rag_query_helper.py     # RAG查詢助手
│   ├── create_enhanced_rag_table.sql  # 資料庫架構
│   └── main.py                 # FastAPI主程式
├── docker-compose.yml          # Docker編排文件
└── README.md                   # 專案說明
```

## 🎯 功能使用

### 1. 基本穿搭諮詢
```
使用者："我明天要參加商務會議，該穿什麼？"
系統：根據場合、天氣、個人風格提供建議
```

### 2. 色彩分析
```
使用者：上傳個人照片
系統：分析膚色調性，推薦適合的色彩搭配
```

### 3. 趨勢查詢
```
使用者："今年秋季流行什麼顏色？"
系統：提供最新流行趨勢分析和建議
```

## 🗄️ 資料庫架構

PostgreSQL向量資料庫包含：
- **文本內容**：時尚知識、搭配建議
- **向量嵌入**：384維度語義向量
- **分類標籤**：內容類型、代理類別
- **元數據**：來源、標籤、創建時間

```sql
CREATE TABLE rag_data (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    data_category data_category_enum NOT NULL,
    content_type content_type_enum NOT NULL,
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 測試

```bash
# 系統整體測試
cd backend
python test_query_system.py

# 代理整合測試
python test_agent_integration.py

# 個別代理測試
cd test/
python test_color_agent_with_image.py
python test_fashion_designer.py
```

## 🔧 開發指南

### 新增AI代理
1. 繼承 `BaseAgent` 類別
2. 實作必要方法
3. 在 `agent_rag_templates.py` 中新增提示詞模板
4. 更新資料庫分類枚舉

### 新增RAG內容
1. 準備知識內容
2. 使用 `convert_faiss_to_pgvector_enhanced.py` 工具
3. 更新分類標籤和元數據

### 前端開發
1. 遵循TypeScript最佳實踐
2. 使用Tailwind CSS設計系統
3. 確保響應式設計

## 📊 系統效能

- **查詢響應時間**：1-2ms
- **向量搜尋精度**：cosine similarity > 0.8
- **資料庫記錄數**：364筆專業時尚知識
- **支援並發**：多使用者同時查詢

## 🛠️ 部署

### 生產環境
```bash
# 構建和部署
docker-compose -f docker-compose.prod.yml up -d

# 資料庫備份
pg_dump fashion_rag > backup.sql

# 擴展部署
kubectl apply -f k8s/
```

### 環境變數
確保生產環境設定：
- 安全的資料庫密碼
- API金鑰保護
- HTTPS配置
- 日誌監控

## 🤝 貢獻

歡迎提交問題和功能請求！

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

MIT License - 詳見 [LICENSE](LICENSE) 檔案

## 📞 聯絡

專案連結：[https://github.com/berubeey/ReVogue](https://github.com/berubeey/ReVogue)

---
