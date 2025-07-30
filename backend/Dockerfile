# 基礎映像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements
COPY requirements.txt ./

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製 agent 代碼（不包含 index 資料夾，讓 index 用 volume 掛載）
COPY agents/ ./agents/
COPY rag_system/ ./rag_system/
COPY output_tags.json ./

# 建立 index 目錄（讓 volume 掛載進來）
RUN mkdir -p rag_fashion_index rag_color_index rag_trend_index rag_image_consultant_index

# 預設啟動指令（可依需求調整）
CMD ["python", "agents/fashion_designer_agent.py"] 