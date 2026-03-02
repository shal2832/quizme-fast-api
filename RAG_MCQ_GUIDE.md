# RAG MCQ Generation Pipeline - User Guide

## Overview

This is a complete **Retrieval-Augmented Generation (RAG)** pipeline built with LangChain that:
- Retrieves content from a Qdrant vector database
- Uses Llama 3.3 LLM to generate multiple choice questions (MCQs)
- Provides REST API endpoints for easy integration

## Architecture

### Components

1. **Qdrant Vector Store** (`src/service/rag.py`)
   - Stores document embeddings using HuggingFace embeddings (all-MiniLM-L6-v2)
   - Enables semantic search and document retrieval
   - Collection name: `pdf_chunks`

2. **MCQ Generator** (`src/service/prepareMCQ.py`)
   - RAG pipeline for intelligent MCQ generation
   - Retrieves relevant documents from Qdrant
   - Uses Llama 3.3-70B language model
   - Generates structured JSON MCQs with explanations

3. **FastAPI Controllers** (`src/controller/uploadFile.py`)
   - REST endpoints for file upload and MCQ generation
   - Status monitoring endpoints
   - Query-based and batch MCQ generation

## Usage

### 1. Upload and Process Documents

**Endpoint:** `POST /api/upload`

Upload a PDF or text file to process and store in Qdrant:

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "message": "File processed successfully",
  "file": "/tmp/file.pdf",
  "chunks": [...]
}
```

### 2. Generate MCQs from a Query

**Endpoint:** `POST /api/questions/query`

Generate MCQs based on a specific topic or query:

```bash
curl -X POST "http://localhost:8000/api/questions/query" \
  -H "Content-Type: application/json" \
  -d {
    "query": "What are the key concepts of machine learning?",
    "num_questions": 5,
    "top_k": 5
  }
```

**Parameters:**
- `query` (string): Search query for retrieving relevant documents
- `num_questions` (integer, default=5): Number of MCQs to generate
- `top_k` (integer, default=5): Number of similar documents to retrieve

**Response:**
```json
{
  "query": "What are the key concepts of machine learning?",
  "num_documents_retrieved": 3,
  "documents": [...],
  "questions": [
    {
      "question": "What is machine learning?",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "A",
      "explanation": "..."
    }
  ],
  "total_questions_generated": 5,
  "status": "success"
}
```

### 3. Generate MCQs from All Documents

**Endpoint:** `POST /api/questions/all`

Generate MCQs from all documents currently in the Qdrant collection:

```bash
curl -X POST "http://localhost:8000/api/questions/all" \
  -H "Content-Type: application/json" \
  -d {
    "num_questions": 10,
    "batch_size": 5
  }
```

**Parameters:**
- `num_questions` (integer, default=10): Total MCQs to generate
- `batch_size` (integer, default=5): Documents to process per batch

**Response:**
```json
{
  "message": "MCQs generated successfully from all documents",
  "total_questions": 10,
  "questions": [...],
  "status": "success"
}
```

### 4. Check Collection Status

**Endpoint:** `GET /api/questions/status`

Check the status of your Qdrant collection and available documents:

```bash
curl -X GET "http://localhost:8000/api/questions/status"
```

**Response:**
```json
{
  "collections": [
    {
      "name": "pdf_chunks",
      "points_count": 42
    }
  ],
  "total_documents_in_pdf_chunks": 42,
  "status": "healthy"
}
```

### 5. Direct LLM Query

**Endpoint:** `POST /api/query`

Query the LLM directly without RAG:

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d "prompt=What is artificial intelligence?"
```

## Python API Usage

### Generate MCQs from Query

```python
from src.service.prepareMCQ import MCQGenerator

# Initialize the generator
generator = MCQGenerator()

# Generate MCQs based on a query
result = generator.generate_mcq_from_query(
    query="What are neural networks?",
    num_questions=5,
    top_k=5
)

print(result['questions'])
```

### Generate MCQs from All Content

```python
# Generate MCQs from all documents in the collection
questions = generator.generate_mcq_from_all_content(
    num_questions=10,
    batch_size=5
)

for q in questions:
    print(f"Q: {q['question']}")
    print(f"Options: {q['options']}")
    print(f"Answer: {q['correct_answer']}")
```

### Retrieve Documents

```python
# Retrieve relevant documents
documents = generator.retrieve_content(
    query="machine learning algorithms",
    top_k=5
)

# Or retrieve all documents
all_documents = generator.retrieve_all_content()
```

### Custom RAG Chain

```python
# Create a RetrievalQA chain for custom MCQ generation
rag_chain = generator.create_rag_chain()

result = generator.generate_with_rag_chain(
    query="Generate MCQs about data science"
)
```

## Configuration

### Environment Variables

Required in `.env` file:

```env
# Qdrant Configuration
qdrant_cluster_url=https://your-qdrant-cluster-url
qdrant_api_key=your-api-key

# HuggingFace API Token (for Llama 3.3)
HF_TOKEN=your-huggingface-token
```

### Embeddings Model

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding Dimension**: 384
- **Distance Metric**: COSINE

### LLM Configuration

- **Model**: `meta-llama/Llama-3.3-70B-Instruct`
- **Temperature**: 0.7
- **Max Tokens**: 2048
- **Provider**: HuggingFace Endpoints

## MCQ Output Format

Each generated MCQ has the following structure:

```json
{
  "question": "What is the primary advantage of using neural networks?",
  "options": [
    "Lower computational cost",
    "Ability to learn complex non-linear patterns",
    "Guaranteed convergence",
    "No need for training data"
  ],
  "correct_answer": "B",
  "explanation": "Neural networks excel at learning complex non-linear relationships in data through their multi-layer architecture and backpropagation algorithm."
}
```

## Performance Tips

1. **Batch Processing**: Use the batch MCQ generation endpoint for large datasets
2. **Vector Store**: Keep your collection size manageable (consider archiving old data)
3. **Top-K Parameter**: Adjust `top_k` based on your collection size:
   - Small collections (< 100 docs): `top_k=3-5`
   - Medium collections (100-1000 docs): `top_k=5-10`
   - Large collections (> 1000 docs): `top_k=10-15`

4. **Token Limits**: The LLM has a 2048 token limit for output. For very long documents, increase chunk size in Qdrant retrieval

## Troubleshooting

### No Documents Found
- Check if files have been uploaded and processed
- Use `/api/questions/status` to verify collection status
- Ensure queries are semantically related to document content

### MCQ Generation Fails
- Check HuggingFace API token is valid and has sufficient credits
- Verify Qdrant connection URL and API key
- Check system memory for LLM inference

### Empty Response
- Verify documents exist in collection
- Try with different query terms
- Check LLM response logs

## File Structure

```
src/
├── controller/
│   └── uploadFile.py      # FastAPI endpoints
├── models/
│   └── llama3.py          # LLM initialization
└── service/
    ├── prepareMCQ.py      # MCQ generation logic
    ├── rag.py             # RAG pipeline and Qdrant integration
    └── processFile.py     # File processing
```

## Future Enhancements

- [ ] Support for multiple languages
- [ ] Difficulty level selection for MCQs
- [ ] Topic categorization and filtering
- [ ] Batch export to various formats (XLSX, CSV, JSON)
- [ ] MCQ validation and quality scoring
- [ ] Analytics dashboard for question difficulty analysis

## Support

For issues or questions, check:
- Qdrant logs: `qdrant_cluster_url/collections`
- HuggingFace API status
- LLM response in server logs
