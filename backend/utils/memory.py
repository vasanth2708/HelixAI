import logging
import boto3
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import Chroma
from config import Config
import asyncio
logger = logging.getLogger(__name__)

async def get_vector_store() -> Chroma:
    embeddings = BedrockEmbeddings(
        client=boto3.client("bedrock-runtime", region_name=Config.AWS_REGION),
        model_id="amazon.titan-embed-text-v2:0"
    )
    vector_store = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    return vector_store

def store_conversation_embedding(session_id: str, conversation_text: str) -> None:
    """Store conversation text in ChromaDB with session metadata."""
    try:
        vector_store = asyncio.run(get_vector_store())
        vector_store.add_texts([conversation_text], metadatas=[{"session_id": session_id}])
    except Exception as e:
        logger.error(f"Error storing conversation embedding: {e}")

def retrieve_context(session_id: str, query: str, k: int = 3) -> str:
    """Retrieve relevant conversation context from ChromaDB."""
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search(query, k=k)
        return "\n".join([doc.page_content for doc in results])
    except Exception as e:
        return ""
