import os
from langchain.docstore.document import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

# Initialize embedding model
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Define vector store paths (only directory names)
vectorstore_paths = {
    "image_consultant": "rag_image_consultant_index",
    "color_analyst": "rag_color_index",
    "fashion_designer": "rag_fashion_index"
}

def setup_rag_index(agent_type: str, documents: list) -> bool:
    """Setup RAG index for an agent"""
    try:
        vs_dir_name = vectorstore_paths.get(agent_type)
        if not vs_dir_name:
            print(f"❌ 找不到 {agent_type} 對應的向量庫目錄名稱")
            return False

        # Construct the full path within the agents directory
        full_path = os.path.join(os.path.dirname(__file__), "agents", vs_dir_name)
        os.makedirs(full_path, exist_ok=True)

        # Create vector store
        vectorstore = FAISS.from_documents(
            documents,
            embedding_model
        )
        
        # Save vector store
        vectorstore.save_local(full_path)
        print(f"✅ {agent_type} 向量庫建立成功在 {full_path}")

        # Verify if files exist after saving
        faiss_file = os.path.join(full_path, "index.faiss")
        pkl_file = os.path.join(full_path, "index.pkl")
        if os.path.exists(faiss_file) and os.path.exists(pkl_file):
            print(f"✅ 檔案存在：{faiss_file} 和 {pkl_file}")
        else:
            print(f"❌ 檔案不存在：{faiss_file} 或 {pkl_file}")

        return True
        
    except Exception as e:
        print(f"❌ 建立 {agent_type} 向量庫時發生錯誤：{str(e)}")
        return False

def main():
    print("\n=== Setting up All RAG Indexes ===")
    
    # Sample documents for Color Analyst
    color_docs = [
        Document(page_content="暖膚色適合穿著橙色、黃色、棕色系衣服。"),
        Document(page_content="冷膚色適合穿著藍色、紫色、綠色系衣服。"),
        Document(page_content="中性膚色適合各種顏色，可以大膽嘗試。")
    ]
    setup_rag_index("color_analyst", color_docs)

    # Sample documents for Image Consultant
    image_consultant_docs = [
        Document(page_content="商務專業人士適合剪裁合身、顏色沉穩的西裝。", metadata={"occupation": "business"}),
        Document(page_content="創意工作者可以嘗試更多元的顏色和款式。", metadata={"occupation": "creative"}),
        Document(page_content="休閒風格偏好者可以選擇寬鬆舒適的服飾。", metadata={"style_preference": "casual"})
    ]
    setup_rag_index("image_consultant", image_consultant_docs)

    # Sample documents for Fashion Designer
    fashion_designer_docs = [
        Document(page_content="日常穿搭建議：牛仔褲搭配T恤，休閒舒適。", metadata={"occasion": "daily"}),
        Document(page_content="晚宴穿搭建議：小禮服搭配高跟鞋，優雅大方。", metadata={"occasion": "evening"}),
        Document(page_content="運動穿搭建議：運動服飾搭配運動鞋，輕便透氣。", metadata={"occasion": "sport"})
    ]
    setup_rag_index("fashion_designer", fashion_designer_docs)

    print("\n=== RAG Index Setup Completed ===")

if __name__ == "__main__":
    main() 