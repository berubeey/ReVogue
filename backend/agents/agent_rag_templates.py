from typing import Dict, List, Any
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))

# Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize raw Gemini model for direct use
raw_gemini_model = genai.GenerativeModel("gemini-1.5-pro")

# Vector store paths for different agents
vectorstore_paths = {
    "image_consultant": "rag_image_consultant_index",
    "color_analyst": "rag_color_index",
    "fashion_designer": "rag_fashion_index",
    "trend_analyst": "rag_trend_index"
}

def build_prompt(agent_type: str, tag: Dict[str, str], user_profile: Dict[str, str], retrieved_context: str = "") -> str:
    """Build natural language prompt for each fashion agent in a roundtable discussion context."""
    base_prompt = ""

    if agent_type == "color_analyst":
        base_prompt = f"""
你是這場穿搭圓桌會議中的色彩鑑定師，專長是分析使用者的膚色、髮色與眼睛顏色，評估使用者所選單品的顏色與材質是否合適。
請以自然語氣、第一人稱提供建議，幫助服裝設計師了解你的專業觀察。

[單品資訊]
- 顏色：{tag.get('color')}
- 材質：{tag.get('material')}

[使用者特徵]
- 膚色：{user_profile.get('skin_tone')}
- 髮色：{user_profile.get('hair_color', '未提供')}
- 眼睛顏色：{user_profile.get('eye_color', '未提供')}
"""

    elif agent_type == "image_consultant":
        base_prompt = f"""
你是這場穿搭圓桌會議中的形象顧問，專責從使用者的職業、風格偏好與形象需求出發，評估使用者選擇的單品是否合適。
請根據以下資訊，以第一人稱語氣發表你的專業建議，幫助其他顧問與設計師了解你的觀點。

[單品資訊]
- 風格：{tag.get('style')}
- 分類：{tag.get('category')}

[使用者特徵]
- 職業：{user_profile.get('occupation')}
- 偏好風格：{', '.join(user_profile.get('style_preference', []))}
"""

    elif agent_type == "fashion_designer":
        base_prompt = f"""
你是這場穿搭圓桌會議的主持人——服裝設計師，負責整合其他顧問的建議，根據使用者的個人特徵與當日情境，提出三套完整的穿搭建議。
請運用你的設計經驗與整體搭配能力，針對以下資訊給出專業建議，風格具體、生動。

[單品資訊]
- 顏色：{tag.get('color')}
- 材質：{tag.get('material')}
- 風格：{tag.get('style')}
- 分類：{tag.get('category')}

[使用者特徵]
- 職業：{user_profile.get('occupation')}
- 偏好風格：{', '.join(user_profile.get('style_preference', []))}
- 膚色：{user_profile.get('skin_tone')}
"""

    elif agent_type == "trend_analyst":
        base_prompt = f"""
你是這場穿搭圓桌會議中的潮流分析師，專長是掌握最新流行趨勢，協助使用者打造符合時代感的穿搭。
請根據以下資訊，以親切自然的語氣提供你的時尚觀察，強調目前熱門元素與延伸搭配方向。

[單品資訊]
- 顏色：{tag.get('color')}
- 材質：{tag.get('material')}
- 風格：{tag.get('style')}
- 分類：{tag.get('category')}

[使用者特徵]
- 職業：{user_profile.get('profession')}
- 偏好風格：{', '.join(user_profile.get('style_preference', []))}
- 個性：{user_profile.get('personality')}
- 性別：{user_profile.get('gender')}
"""

    elif agent_type == "personal_secretary":
        base_prompt = f"""
你是這場穿搭圓桌會議的個人秘書，負責彙整使用者的行程與天氣資訊，幫助顧問們掌握當日的實際需求。
請根據以下資訊，以簡潔語氣輸出當日穿搭情境摘要，讓其他顧問能參考。

[天氣資訊 / 當日摘要]
{retrieved_context}
"""

    elif agent_type == "encourager":
        base_prompt = f"""
你是這場穿搭圓桌會議中的鼓勵員，負責在建議過程中給予使用者自信與正向回饋。
請根據使用者的個人特徵與風格選擇，產出一句富有情感的鼓勵語。

[使用者特徵]
- 性別：{user_profile.get('gender')}
- 偏好風格：{', '.join(user_profile.get('style_preference', []))}
- 職業：{user_profile.get('occupation')}
"""

    if retrieved_context:
        base_prompt += f"\n\n[參考資訊]\n{retrieved_context}"
    else:
        return "（未知代理類型，請補充提示詞模板）"
    
    return base_prompt

def query_agent(agent_type: str, tag: Dict[str, str], user_profile: Dict[str, str]) -> str:
    """Query agent using RAG"""
    # Load corresponding vector store
    vs_dir_name = vectorstore_paths.get(agent_type)
    if not vs_dir_name:
        return f"❌ 找不到 {agent_type} 對應的向量庫"

    full_vs_path = os.path.join(os.path.dirname(__file__), vs_dir_name)
    print(f"Attempting to load vector store from: {full_vs_path}")
    if not os.path.exists(full_vs_path):
        return f"❌ 向量庫路徑不存在：{full_vs_path}"

    try:
        vectorstore = FAISS.load_local(
            full_vs_path,
            embeddings=embedding_model,
            allow_dangerous_deserialization=True
        )
        
        # Get relevant documents based on the prompt for the LLM
        query_for_retrieval = build_prompt(agent_type, tag, user_profile)
        relevant_docs = vectorstore.as_retriever().invoke(query_for_retrieval)
        
        context_text = "\n".join([doc.page_content for doc in relevant_docs])

        # Construct the final message for the LLM, including retrieved context
        final_prompt_content = build_prompt(agent_type, tag, user_profile, retrieved_context=context_text)
        
        # Invoke the raw Gemini model directly
        response = raw_gemini_model.generate_content(final_prompt_content)
        
        # Debugging: Print the full response object
        print(f"LLM Raw Response: {response}")
        
        # Post-process the response content to remove 'thought' and other unwanted text
        processed_content = response.text
        # Remove 'thought' and anything after it
        processed_content = re.split(r'\n\s*thought', processed_content, 1)[0].strip()
        # Remove any leading/trailing markdown code block fences if present (e.g., ```json or ```)
        processed_content = re.sub(r'^(```json|```|json)\n*', '', processed_content, flags=re.MULTILINE)
        processed_content = re.sub(r'\n*(```)$', '', processed_content, flags=re.MULTILINE)

        return processed_content
        
    except Exception as e:
        return f"❌ 查詢 {agent_type} 時發生錯誤：{str(e)}"

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