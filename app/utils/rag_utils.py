from typing import List, Dict, Tuple
from app.services.logging_service import logger
from app.services.language_service import language_service

try:
    from app.services.translation_service import translation_service
    if translation_service.translator is None:
        translation_service = None
except Exception:
    translation_service = None


async def refine_query(query: str, language: str = "en") -> str:
    return query.strip()


async def format_retrieved_documents(documents: List[Tuple[Dict, float]]) -> str:
    if not documents:
        return ""
    
    formatted_parts = []
    for i, (metadata, score) in enumerate(documents, 1):
        text = metadata.get('text', '')
        filename = metadata.get('filename', 'unknown')
        language = metadata.get('language', 'en')
        
        formatted_parts.append(
            f"[Document {i} - Source: {filename}, Language: {language}, Relevance: {score:.2f}]\n"
            f"{text}\n"
        )
    
    return "\n".join(formatted_parts)


async def generate_response(
    query: str,
    context: str,
    query_language: str,
    output_language: str
) -> str:
    max_context_length = 2000
    formatted_context = context[:max_context_length]
    if len(context) > max_context_length:
        formatted_context += "...\n[Context truncated]"
    
    context_summary = formatted_context[:1000]
    
    if output_language == "en":
        response = f"""Based on the retrieved medical guidelines and research documents, here is the answer to your question:

{context_summary}

Please note that this information is based on the available documents. For personalized medical advice, please consult with a healthcare professional."""
    else:
        response = f"""取得した医療ガイドラインと研究資料に基づいて、以下のように説明できます：

{context_summary}

この情報は利用可能な資料に基づいています。個別の医療アドバイスについては、医療専門家に相談してください。"""
    
    if output_language != query_language and translation_service:
        try:
            response = translation_service.translate(
                response,
                target_lang=output_language,
                source_lang=query_language
            )
        except Exception as e:
            logger.warning(f"Translation error: {e}. Returning original response.")
    
    return response

