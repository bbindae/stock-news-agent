from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from google import genai
from langchain_ollama import ChatOllama


load_dotenv(dotenv_path="../.env")

def get_llm():
    return ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)

def get_embedding_llm():
    return GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", task_type="RETRIEVAL_DOCUMENT")

def get_ollama_llm():
    return ChatOllama(model="qwen3.5:9b", temperature=0, reasoning=False)

_client = genai.Client()

def get_exact_gemini_tokens(docs: list[Document], text: str,
                            model_name="gemini-embedding-001") -> int:
    total_tokens = 0

    if text:
        total_tokens = _client.models.count_tokens(
            model=model_name,
            contents=text
        ).total_tokens
    elif docs:
        pure_texts = [doc.page_content for doc in docs]
        total_tokens = _client.models.count_tokens(
            model=model_name,
            contents=pure_texts
        ).total_tokens
    else:
        raise ValueError(f"either text or docs parameter must be provided")

    return total_tokens