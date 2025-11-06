from fastapi import APIRouter, HTTPException, Depends
from app.models.requests import RetrieveRequest
from app.models.responses import RetrieveResponse, RetrievedDocument
from app.services.faiss_service import faiss_service
from app.middleware.auth import verify_api_key

router = APIRouter()


@router.post("/", response_model=RetrieveResponse)
async def retrieve_documents(
    request: RetrieveRequest,
    api_key: str = Depends(verify_api_key)
):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = await faiss_service.search(request.query, request.top_k or 3)
    
    retrieved_docs = [
        RetrievedDocument(
            id=metadata["id"],
            text=metadata["text"],
            language=metadata["language"],
            filename=metadata["filename"],
            similarity_score=round(similarity, 4)
        )
        for metadata, similarity in results
    ]
    
    return RetrieveResponse(
        query=request.query,
        results=retrieved_docs,
        total_results=len(retrieved_docs)
    )
