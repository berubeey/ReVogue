# StyleSage AI 虛擬穿搭顧問

StyleSage AI 是一個以多智能體（Multi-Agent）架構為核心的虛擬穿搭顧問系統。本系統旨在透過模擬與真人顧問團隊的對話體驗，為使用者提供高度個人化、結合流行趨勢與個人情境的每日穿搭建議。

## 功能特點

- 🤖 多智能體協作系統
- 👔 個人化穿搭建議
- 🎨 色彩分析
- 📸 圖片上傳與分析
- 💬 自然語言對話
- 🌟 情感陪伴

## 技術架構

### 前端
- Next.js 14
- TypeScript
- Tailwind CSS
- Framer Motion
- React Icons

### 後端
- FastAPI
- LangGraph
- Google Gemini AI
- OpenCV (色彩分析)

## 快速開始

### 環境需求
- Python 3.8+
- Node.js 18+
- Google Cloud API Key

### 安裝步驟

1. 克隆專案
```bash
git clone https://github.com/your-username/style-sage-ai.git
cd style-sage-ai
```

2. 安裝後端依賴
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. 安裝前端依賴
```bash
cd ../frontend
npm install
```

4. 設定環境變數
```bash
# backend/.env
GOOGLE_API_KEY=your_google_api_key
```

5. 啟動後端服務
```bash
cd backend
uvicorn main:app --reload
```

6. 啟動前端服務
```bash
cd frontend
npm run dev
```

## 使用方式

1. 開啟瀏覽器訪問 http://localhost:3000
2. 在聊天介面中輸入您的穿搭需求
3. 可以上傳照片進行色彩分析
4. 系統會透過多個智能體協作，提供完整的穿搭建議

## 智能體說明

- 👗 服裝設計師 (Lead Agent)：整合所有資訊並產出最終穿搭建議
- 🗓 個人秘書：分析天氣、日程與地點資訊
- 🧍‍♀️ 形象顧問：根據職業與品牌建議風格
- 🎨 色彩鑒定師：分析膚色、髮色與眼色
- 🔥 潮流分析師：提供流行趨勢與穿搭靈感
- 💬 鼓勵員：提供情感陪伴與正面回饋

## 開發指南

### 新增智能體
1. 在 `backend/agents` 目錄下創建新的智能體類別
2. 繼承 `BaseAgent` 類別
3. 實作必要的方法
4. 在 `AgentCoordinator` 中註冊新的智能體

### 修改前端介面
1. 在 `frontend/app/components` 目錄下修改或新增組件
2. 使用 Tailwind CSS 進行樣式設計
3. 確保組件具有適當的型別定義

## 貢獻指南

1. Fork 專案
2. 創建功能分支
3. 提交變更
4. 發起 Pull Request

## 授權

MIT License

# FAISS Index 使用說明

本專案採用 FAISS 作為主力向量檢索方案，所有 RAG 相關資料皆已存入 FAISS index 檔案，並由 agent 直接讀取。

## 目錄結構

- backend/rag_fashion_index/index.faiss
- backend/rag_fashion_index/index.pkl
- backend/rag_color_index/index.faiss
- backend/rag_color_index/index.pkl
- backend/rag_trend_index/index.faiss
- backend/rag_trend_index/index.pkl
- backend/rag_image_consultant_index/index.faiss
- backend/rag_image_consultant_index/index.pkl
- backend/rag_encourager_index/index.faiss
- backend/rag_encourager_index/index.pkl

## 如何在 Python 載入 FAISS index

```python
import faiss
import pickle

# 讀取 index
index = faiss.read_index('rag_fashion_index/index.faiss')
# 讀取 metadata
with open('rag_fashion_index/index.pkl', 'rb') as f:
    metadata = pickle.load(f)
```

## Docker Compose 掛載範例

請確保 docker-compose.yml 內有如下設定，將 index 目錄掛載進 container：

```yaml
services:
  backend:
    build:
      context: ./backend
    volumes:
      - ./backend/rag_fashion_index:/app/rag_fashion_index
      - ./backend/rag_color_index:/app/rag_color_index
      - ./backend/rag_trend_index:/app/rag_trend_index
      - ./backend/rag_image_consultant_index:/app/rag_image_consultant_index
      - ./backend/rag_encourager_index:/app/rag_encourager_index
```

## Index 更新方式

如需更新 index（例如新增資料），請聯絡資料維護者，或使用 backend 內的相關腳本（如 batch_image_tagging.py、setup_all_rag_indexes.py）重新產生 index.faiss 與 index.pkl。

## FAISS 轉 pgvector 腳本

如未來需將 FAISS index 轉存至 Postgres/pgvector，請參考 backend/convert_faiss_to_pgvector.py。

---

如有任何問題，請聯絡專案維護者。
