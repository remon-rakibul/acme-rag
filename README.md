# Healthcare Knowledge Assistant - RAG System

A RAG-powered backend system for retrieving medical guidelines and research summaries in English and Japanese. Built with FastAPI, LangChain, FAISS, and sentence-transformers.

## Features

- Multilingual support: English and Japanese document ingestion and querying
- Document ingestion with automatic language detection
- Vector search using FAISS for semantic document retrieval
- Mock LLM response generation with bilingual output
- Optional translation between English and Japanese
- API key authentication
- Docker support
- CI/CD pipeline with GitHub Actions

## Setup

### Prerequisites

- Python 3.11+
- pip
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd acme-RAG
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env to set your API key (optional - defaults are provided)
```

5. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Docker Setup

Build and run:
```bash
docker build -t healthcare-rag:latest .
docker run -d -p 8000:8000 \
  -e API_KEY=acme-ai-secret-key-2025 \
  -v $(pwd)/data:/app/data \
  --name healthcare-rag \
  healthcare-rag:latest
```

## API Endpoints

### Health Check
**GET** `/health`

### Ingest Documents
**POST** `/ingest`
- Accepts .txt files in English or Japanese
- Headers: `X-API-Key: <your-api-key>`
- Request: Multipart form data with file uploads

### Retrieve Documents
**POST** `/retrieve`
- Returns top-k relevant documents with similarity scores
- Headers: `X-API-Key: <your-api-key>`
- Request body: `{"query": "your query", "top_k": 3}`

### Generate Response
**POST** `/generate`
- Combines retrieved docs + query into mock LLM response
- Headers: `X-API-Key: <your-api-key>`
- Request body: `{"query": "your query", "output_language": "en", "top_k": 3}`

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Design Notes

### Scalability

The current implementation uses FAISS with a flat index for exact similarity search. For production at scale, consider:

1. **Index Optimization**: Upgrade to FAISS IndexIVF or HNSW for faster approximate search
2. **Distributed Storage**: Move FAISS index to cloud storage (S3, Azure Blob) for multi-instance deployments
3. **Caching Layer**: Implement Redis for caching frequently accessed queries
4. **Load Balancing**: Use nginx or cloud load balancers for horizontal scaling
5. **Database Backend**: Replace in-memory metadata storage with PostgreSQL or MongoDB
6. **Async Processing**: Use Celery for background document ingestion

### Modularity

The architecture follows clear separation of concerns:

1. **Service Layer**: Independent services (embedding, FAISS, language, translation) that can be swapped or extended
2. **Router Layer**: Isolated API endpoints for easy extension
3. **Middleware**: Centralized authentication that can be extended
4. **Configuration**: Environment variables for easy configuration

Future improvements could include dependency injection, plugin system for embedding models, and strategy pattern for different vector stores.

### Future Improvements

1. **LLM Integration**: Replace mock response generation with actual LLM API
2. **Advanced Chunking**: Implement semantic chunking with overlap
3. **Reranking**: Add cross-encoder reranking for better relevance
4. **Query Expansion**: Implement query expansion for better retrieval
5. **Multi-format Support**: Extend beyond .txt to PDF, DOCX, Markdown
6. **Metadata Filtering**: Support filtering by document metadata
7. **User Management**: Add user authentication and document ownership
8. **Analytics**: Track query patterns and system performance
9. **Monitoring**: Add logging, metrics (Prometheus), and error tracking
10. **Batch Processing**: Support batch ingestion for large document sets

## Security Considerations

1. **API Key Management**: Use secure key management services in production
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Input Validation**: Enhanced validation for file uploads (size limits, content scanning)
4. **HTTPS**: Always use HTTPS in production
5. **CORS**: Configure CORS appropriately for your frontend
6. **Data Privacy**: Implement data encryption at rest and in transit
7. **Audit Logging**: Log all API access for security auditing

## License

This project is created for the Acme AI assignment.
