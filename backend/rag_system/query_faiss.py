import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# 載入環境變數
load_dotenv()

# 設定參數
TOP_K = 5  # 顯示前 5 個最相關的結果
DOCS_PATH = "faiss_image_claim_index"
API_KEY = os.getenv("GOOGLE_API_KEY")  # 從環境變數讀取 API key
if not API_KEY:
    raise ValueError("請設置 GOOGLE_API_KEY 環境變數")
LLM_MODEL_ID = "gemini-1.5-flash"

# 初始化 embedding 模型
embedding_model = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")

# 載入 FAISS 向量資料庫
vectorstore = FAISS.load_local(DOCS_PATH, embedding_model, allow_dangerous_deserialization=True)

# 設定 LLM
llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL_ID,
    google_api_key=API_KEY,
    temperature=0.7
)

# 設定 prompt template
template = """你是一個專業的圖片分析助手。請根據以下圖片資訊，回答使用者的問題。
如果找不到完全符合的圖片，請提供最相關的資訊。

圖片資訊:
{context}

使用者問題: {question}

請提供一個詳細且專業的回答，包含：
1. 直接回答使用者的問題
2. 列出相關的圖片及其特徵
3. 如果有需要，提供額外的分析或建議

回答:"""

QA_CHAIN_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=template,
)

# 建立 QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": TOP_K}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
)

def display_results(docs, question):
    print("\n" + "="*50)
    print(f"搜尋結果 (問題: {question})")
    print("="*50)
    
    for i, doc in enumerate(docs, 1):
        print(f"\n結果 {i}:")
        print("-"*30)
        print(f"圖片名稱: {doc.metadata['image_name']}")
        print(f"描述: {doc.metadata['description']}")
        if doc.metadata['style']:
            print(f"風格: {doc.metadata['style']}")
        if doc.metadata['material']:
            print(f"材質: {doc.metadata['material']}")
        if doc.metadata['category']:
            print(f"分類: {doc.metadata['category']}")
        if doc.metadata['color']:
            print(f"顏色: {doc.metadata['color']}")
        if doc.metadata['occasion']:
            print(f"場合: {doc.metadata['occasion']}")
        if doc.metadata['mood']:
            print(f"情緒: {doc.metadata['mood']}")
        if doc.metadata['suitable_skin_tones']:
            print(f"適合膚色: {doc.metadata['suitable_skin_tones']}")
        print("-"*30)

def main():
    print("歡迎使用圖片搜尋系統！")
    print("請輸入您的問題，或輸入 'exit' 結束程式。")
    
    while True:
        question = input("\n請輸入您的問題: ").strip()
        
        if question.lower() == 'exit':
            print("感謝使用，再見！")
            break
            
        if not question:
            print("請輸入有效的問題！")
            continue
            
        try:
            # 使用 retriever 獲取相關文件
            docs = vectorstore.similarity_search(question, k=TOP_K)
            
            # 顯示搜尋結果
            display_results(docs, question)
            
            # 生成回答
            try:
                result = qa_chain.invoke({"query": question})
                if result and "result" in result:
                    print("\n" + "="*50)
                    print("AI 分析結果:")
                    print("="*50)
                    print(result["result"])
                else:
                    print("\n注意：AI 分析結果為空，但已顯示相關圖片資訊。")
            except Exception as e:
                print(f"\n注意：生成 AI 分析結果時發生錯誤 ({str(e)})，但已顯示相關圖片資訊。")
                
        except Exception as e:
            print(f"發生錯誤: {str(e)}")

if __name__ == "__main__":
    main() 