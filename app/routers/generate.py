from fastapi import APIRouter, HTTPException, Depends
from app.models.requests import GenerateRequest
from app.models.responses import GenerateResponse
from app.services.faiss_service import faiss_service
from app.services.language_service import language_service
from app.middleware.auth import verify_api_key
from app.utils.rag_utils import refine_query, format_retrieved_documents, generate_response

router = APIRouter()


@router.post("/", response_model=GenerateResponse)
async def generate_rag_response(
    request: GenerateRequest,
    api_key: str = Depends(verify_api_key)
):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    query_language = language_service.detect_language(request.query)
    
    output_language = request.output_language
    if not output_language:
        query_lower = request.query.lower()
        if "answer in english" in query_lower or "respond in english" in query_lower or "reply in english" in query_lower:
            output_language = "en"
        elif "英語で" in query_lower or "英語で答えて" in query_lower:
            output_language = "en"
        elif "answer in japanese" in query_lower or "respond in japanese" in query_lower or "日本語で" in query_lower:
            output_language = "ja"
        else:
            output_language = query_language
    
    if output_language not in language_service.SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported output_language: {output_language}. Supported: en, ja"
        )
    
    refined_query = await refine_query(request.query, query_language)
    retrieved_results = await faiss_service.search(refined_query, request.top_k or 3)
    
    if not retrieved_results:
        raise HTTPException(
            status_code=404,
            detail="No relevant documents found. Please ingest documents first."
        )
    
    context_text = await format_retrieved_documents(retrieved_results)
    context_docs = [
        {
            "id": metadata["id"],
            "text": metadata["text"][:200] + "..." if len(metadata["text"]) > 200 else metadata["text"],
            "language": metadata["language"],
            "filename": metadata["filename"],
            "similarity_score": round(similarity, 4)
        }
        for metadata, similarity in retrieved_results
    ]
    
    response = await generate_response(
        query=request.query,
        context=context_text,
        query_language=query_language,
        output_language=output_language
    )
    
    debug_info = {
        "refined_query": refined_query,
        "num_context_chunks": len(retrieved_results),
        "query_language": query_language,
        "output_language": output_language
    }
    
    return GenerateResponse(
        query=request.query,
        refined_query=refined_query,
        response=response,
        language=output_language,
        retrieved_context=context_docs,
        num_context_docs=len(context_docs),
        debug_info=debug_info
    )
