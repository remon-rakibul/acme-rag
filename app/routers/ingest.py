from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from app.models.responses import IngestResponse, IngestedDocument
from app.services.faiss_service import faiss_service
from app.services.language_service import language_service
from app.services.logging_service import logger
from app.middleware.auth import verify_api_key
from langchain_text_splitters import RecursiveCharacterTextSplitter

router = APIRouter()


@router.post("/", response_model=IngestResponse)
async def ingest_documents(
    files: List[UploadFile] = File(...),
    chunk_size: int = 500,
    api_key: str = Depends(verify_api_key)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    ingested_docs = []
    errors = []
    
    for file in files:
        try:
            if not file.filename or not file.filename.endswith('.txt'):
                errors.append(f"{file.filename}: Only .txt files are supported")
                continue
            
            content = await file.read()
            text = content.decode('utf-8')
            
            if not text.strip():
                errors.append(f"{file.filename}: Empty file")
                continue
            
            try:
                language = language_service.detect_language(text)
                logger.info(f"Detected language '{language}' for {file.filename}")
            except Exception as e:
                errors.append(f"{file.filename}: Language detection failed - {str(e)}")
                continue
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=50
            )
            documents = text_splitter.create_documents(
                [text],
                metadatas=[{"language": language, "filename": file.filename}]
            )
            
            if documents:
                await faiss_service.add_documents_from_langchain(documents)
                ingested_docs.append(IngestedDocument(
                    filename=file.filename,
                    language=language,
                    chunks=len(documents),
                    size=len(text)
                ))
        
        except UnicodeDecodeError:
            errors.append(f"{file.filename}: Unable to decode file. Please ensure it's UTF-8 encoded.")
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {e}")
            errors.append(f"{file.filename}: Error processing file - {str(e)}")
    
    total_docs = faiss_service.get_stats().get("total_documents", 0)
    
    return IngestResponse(
        status="success",
        ingested=len(ingested_docs),
        documents=ingested_docs,
        errors=errors if errors else None,
        total_documents_in_index=total_docs
    )
