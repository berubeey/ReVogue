import os
from langchain.docstore.document import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from typing import Dict, List, Any
import re
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

# Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Vector store paths for different agents
vectorstore_paths = {
    "image_consultant": "rag_image_consultant_index",
    "color_analyst": "rag_color_index",
    "fashion_designer": "rag_fashion_index",
    "trend_analyst": "rag_trend_index",
    "encourager": "rag_encourager_index"
}

def setup_rag_index(agent_type: str, documents: list) -> bool:
    """Setup RAG index for an agent"""
    try:
        vs_dir_name = vectorstore_paths.get(agent_type)
        if not vs_dir_name:
            print(f"❌ 找不到 {agent_type} 對應的向量庫路徑")
            return False

        # Create vector store directory if it doesn't exist
        full_path = os.path.join(os.path.dirname(__file__), vs_dir_name)
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

def read_color_analysis_knowledge() -> List[Document]:
    """Read and process color_analysis_knowledge.md into Document objects"""
    try:
        # Read the markdown file
        knowledge_path = os.path.join(os.path.dirname(__file__), "agents/color_analysis_knowledge.md")
        with open(knowledge_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split content into sections based on headers
        sections = re.split(r'^#+\s+', content, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        # Create Document objects for each section
        documents = []
        for section in sections:
            # Skip empty sections
            if not section.strip():
                continue
                
            # Create metadata based on the first line (header)
            header = section.split('\n')[0].strip()
            metadata = {
                "section": header,
                "type": "color_analysis"
            }
            
            # Create Document object
            doc = Document(
                page_content=section,
                metadata=metadata
            )
            documents.append(doc)

        print(f"✅ 成功讀取 {len(documents)} 個色彩分析知識段落")
        return documents

    except Exception as e:
        print(f"❌ 讀取色彩分析知識時發生錯誤：{str(e)}")
        return []

def read_trend_guide_knowledge() -> List[Document]:
    """Read and process trend_guide.md into Document objects"""
    try:
        # Read the markdown file
        knowledge_path = os.path.join(os.path.dirname(__file__), "agents/trend_guide.md")
        with open(knowledge_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split content into sections based on headers
        sections = re.split(r'^#+\s+', content, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        # Create Document objects for each section
        documents = []
        for section in sections:
            # Skip empty sections
            if not section.strip():
                continue
                
            # Create metadata based on the first line (header)
            header = section.split('\n')[0].strip()
            metadata = {
                "section": header,
                "type": "trend_analysis"
            }
            
            # Create Document object
            doc = Document(
                page_content=section,
                metadata=metadata
            )
            documents.append(doc)

        print(f"✅ 成功讀取 {len(documents)} 個趨勢分析知識段落")
        return documents

    except Exception as e:
        print(f"❌ 讀取趨勢分析知識時發生錯誤：{str(e)}")
        return []

def read_image_consulting_knowledge() -> List[Document]:
    """Read and process image_consulting_guide.md into Document objects"""
    try:
        # Read the markdown file
        knowledge_path = os.path.join(os.path.dirname(__file__), "agents/image_consulting_guide.md")
        with open(knowledge_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split content into sections based on headers
        sections = re.split(r'^#+\s+', content, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        # Create Document objects for each section
        documents = []
        for section in sections:
            # Skip empty sections
            if not section.strip():
                continue
                
            # Create metadata based on the first line (header)
            header = section.split('\n')[0].strip()
            metadata = {
                "section": header,
                "type": "image_consulting"
            }
            
            # Create Document object
            doc = Document(
                page_content=section,
                metadata=metadata
            )
            documents.append(doc)

        print(f"✅ 成功讀取 {len(documents)} 個形象顧問知識段落")
        return documents

    except Exception as e:
        print(f"❌ 讀取形象顧問知識時發生錯誤：{str(e)}")
        return []

def read_encouragement_quotes() -> List[Document]:
    """Read and process encouragement_quotes.md into Document objects"""
    try:
        # Read the markdown file
        knowledge_path = os.path.join(os.path.dirname(__file__), "agents/encouragement_quotes.md")
        with open(knowledge_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split content into sections based on headers
        sections = re.split(r'^#+\s+', content, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        # Create Document objects for each section
        documents = []
        for section in sections:
            # Skip empty sections
            if not section.strip():
                continue
                
            # Create metadata based on the first line (header)
            header = section.split('\n')[0].strip()
            metadata = {
                "section": header,
                "type": "encouragement"
            }
            
            # Create Document object
            doc = Document(
                page_content=section,
                metadata=metadata
            )
            documents.append(doc)

        print(f"✅ 成功讀取 {len(documents)} 個鼓勵語錄段落")
        return documents

    except Exception as e:
        print(f"❌ 讀取鼓勵語錄時發生錯誤：{str(e)}")
        return []

def read_fashion_designer_guide() -> List[Document]:
    """Read and process fashion_designer_guide.md into Document objects"""
    try:
        # Read the markdown file
        knowledge_path = os.path.join(os.path.dirname(__file__), "agents/fashion_designer_guide.md")
        with open(knowledge_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split content into sections based on headers
        sections = re.split(r'^#+\s+', content, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        # Create Document objects for each section
        documents = []
        for section in sections:
            # Skip empty sections
            if not section.strip():
                continue
                
            # Create metadata based on content
            metadata = {
                "source": "fashion_designer_guide.md",
                "section": section.split('\n')[0][:50] + "..." if len(section.split('\n')[0]) > 50 else section.split('\n')[0],
                "content_type": "fashion_design_guide"
            }
            
            # Create Document object
            doc = Document(
                page_content=section,
                metadata=metadata
            )
            documents.append(doc)
        
        print(f"✅ 成功讀取 fashion_designer_guide.md，共 {len(documents)} 個知識段落")
        return documents
        
    except Exception as e:
        print(f"❌ 讀取 fashion_designer_guide.md 時發生錯誤：{str(e)}")
        return []

def main():
    print("\n=== Setting up All RAG Indexes ===")
    
    # Read color analysis knowledge
    color_docs = read_color_analysis_knowledge()
    
    # Add basic color knowledge if the file reading failed
    if not color_docs:
        print("⚠️ 使用基本色彩知識作為備用")
        color_docs = [
            Document(page_content="暖膚色適合穿著橙色、黃色、棕色系衣服。"),
            Document(page_content="冷膚色適合穿著藍色、紫色、綠色系衣服。"),
            Document(page_content="中性膚色適合各種顏色，可以大膽嘗試。")
        ]
    
    # Setup color analyst index
    setup_rag_index("color_analyst", color_docs)

    # Read trend guide knowledge
    trend_docs = read_trend_guide_knowledge()
    
    # Add basic trend knowledge if the file reading failed
    if not trend_docs:
        print("⚠️ 使用基本趨勢知識作為備用")
        trend_docs = [
            Document(page_content="2025年春季流行寬鬆剪裁和自然色調。"),
            Document(page_content="浪漫風格和實用主義是2025年的主要趨勢。"),
            Document(page_content="粉末粉紅色和大地色調是2025年的主打色彩。")
        ]
    
    # Setup trend analyst index
    setup_rag_index("trend_analyst", trend_docs)

    # Read image consulting knowledge
    image_consulting_docs = read_image_consulting_knowledge()
    
    # Add basic image consulting knowledge if the file reading failed
    if not image_consulting_docs:
        print("⚠️ 使用基本形象顧問知識作為備用")
        image_consulting_docs = [
            Document(page_content="商務專業人士適合剪裁合身、顏色沉穩的西裝。", metadata={"occupation": "business"}),
            Document(page_content="創意工作者可以嘗試更多元的顏色和款式。", metadata={"occupation": "creative"}),
            Document(page_content="休閒風格偏好者可以選擇寬鬆舒適的服飾。", metadata={"style_preference": "casual"})
        ]
    
    # Setup image consultant index
    setup_rag_index("image_consultant", image_consulting_docs)

    # Read encouragement quotes
    encouragement_docs = read_encouragement_quotes()
    
    # Add basic encouragement knowledge if the file reading failed
    if not encouragement_docs:
        print("⚠️ 使用基本鼓勵語錄作為備用")
        encouragement_docs = [
            Document(page_content="自信就是最好的時尚配件。", metadata={"type": "confidence"}),
            Document(page_content="穿搭是種無聲的自我介紹。", metadata={"type": "self_expression"}),
            Document(page_content="找到你的個人風格，然後擁有它。", metadata={"type": "personal_style"})
        ]
    
    # Setup encourager index
    setup_rag_index("encourager", encouragement_docs)

    # Read fashion designer guide knowledge
    fashion_designer_docs = read_fashion_designer_guide()
    
    # Add basic fashion designer knowledge if the file reading failed
    if not fashion_designer_docs:
        print("⚠️ 使用基本時尚設計師知識作為備用")
        fashion_designer_docs = [
            Document(page_content="日常穿搭建議：牛仔褲搭配T恤，休閒舒適。", metadata={"occasion": "daily"}),
            Document(page_content="晚宴穿搭建議：小禮服搭配高跟鞋，優雅大方。", metadata={"occasion": "evening"}),
            Document(page_content="運動穿搭建議：運動服飾搭配運動鞋，輕便透氣。", metadata={"occasion": "sport"})
        ]
    
    # Setup fashion designer index
    setup_rag_index("fashion_designer", fashion_designer_docs)

    print("\n=== RAG Index Setup Completed ===")

if __name__ == "__main__":
    main() 