# Collection Cleanup & Deletion Guide

## Overview

After generating MCQs from your Qdrant collection, you may want to delete the collection to:
- Free up storage resources
- Clean up after a single-use session  
- Reset for a new set of documents
- Manage API quotas

## Available Methods

### 1. Manual Collection Deletion (REST API)

**Endpoint:** `DELETE /api/collection/delete`

Delete a collection from Qdrant:

```bash
curl -X DELETE "http://localhost:8000/api/collection/delete?collection_name=pdf_chunks"
```

**Query Parameters:**
- `collection_name` (string, default="pdf_chunks"): Name of the collection to delete

**Response:**
```json
{
  "message": "Collection 'pdf_chunks' deleted successfully",
  "collection_name": "pdf_chunks",
  "status": "deleted"
}
```

### 2. Python Method - Manual Cleanup

```python
from src.service.prepareMCQ import MCQGenerator

generator = MCQGenerator()

# Generate MCQs first
result = generator.generate_mcq_from_query(
    query="machine learning",
    num_questions=5
)

# Then cleanup when done
success = generator.cleanup_collection()
print(f"Collection deleted: {success}")
```

### 3. Combined Generation & Cleanup (REST API)

**Endpoint:** `POST /api/questions/query/cleanup`

Generate MCQs and automatically delete the collection in one request:

```bash
curl -X POST "http://localhost:8000/api/questions/query/cleanup" \
  -H "Content-Type: application/json" \
  -d {
    "query": "machine learning algorithms",
    "num_questions": 5,
    "top_k": 5
  }
```

**Response:**
```json
{
  "query": "machine learning algorithms",
  "num_documents_retrieved": 3,
  "documents": [...],
  "questions": [...],
  "total_questions_generated": 5,
  "cleanup_status": "success",
  "status": "success"
}
```

### 4. Python Method - Auto-Cleanup

```python
from src.service.prepareMCQ import MCQGenerator

generator = MCQGenerator()

# Generate MCQs and automatically delete collection
result = generator.generate_and_cleanup(
    query="neural networks",
    num_questions=5,
    top_k=5
)

print(f"Questions: {len(result['questions'])}")
print(f"Cleanup: {result['cleanup_status']}")
```

### 5. Recreate Collection (REST API)

**Endpoint:** `POST /api/collection/recreate`

Recreate a collection after deletion (useful if you want to upload more documents):

```bash
curl -X POST "http://localhost:8000/api/collection/recreate?collection_name=pdf_chunks"
```

**Response:**
```json
{
  "message": "Collection 'pdf_chunks' recreated successfully",
  "collection_name": "pdf_chunks",
  "status": "created"
}
```

### 6. Check Collection Status Before Deletion

**Endpoint:** `GET /api/questions/status`

```bash
curl "http://localhost:8000/api/questions/status"
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

## Common Workflows

### Workflow 1: Upload → Generate → Delete (One-Shot)

```bash
# 1. Upload document
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@document.pdf"

# 2. Generate MCQs and auto-cleanup
curl -X POST "http://localhost:8000/api/questions/query/cleanup" \
  -H "Content-Type: application/json" \
  -d '{"query": "topic", "num_questions": 10}'

# Done! Collection is cleaned up automatically
```

### Workflow 2: Upload → Generate → Keep → Delete Later

```bash
# 1. Upload document
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@document.pdf"

# 2. Generate MCQs (keep collection)
curl -X POST "http://localhost:8000/api/questions/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "topic", "num_questions": 10}'

# 3. Do more operations...

# 4. Delete when done
curl -X DELETE "http://localhost:8000/api/collection/delete"
```

### Workflow 3: Upload → Generate Multiple Batches → Delete

```bash
# 1. Upload document
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@document.pdf"

# 2. Generate batch 1
curl -X POST "http://localhost:8000/api/questions/query" \
  -d '{"query": "topic1", "num_questions": 5}'

# 3. Generate batch 2
curl -X POST "http://localhost:8000/api/questions/query" \
  -d '{"query": "topic2", "num_questions": 5}'

# 4. Generate from all documents
curl -X POST "http://localhost:8000/api/questions/all" \
  -d '{"num_questions": 10}'

# 5. Cleanup
curl -X DELETE "http://localhost:8000/api/collection/delete"
```

## Python API Methods Summary

### MCQGenerator Class Methods

```python
# Core methods
generator.generate_mcq_from_query(query, num_questions, top_k)
generator.generate_mcq_from_all_content(num_questions, batch_size)

# Cleanup methods
generator.cleanup_collection()  # Returns: bool
generator.generate_and_cleanup(query, num_questions, top_k)  # Returns: dict with questions + cleanup_status
```

### Rag Class Methods

```python
# Collection management
rag.delete_collection(collection_name=None)  # Returns: bool
rag.recreate_collection()  # Returns: bool

# Document retrieval
rag.retrieve_documents(query, top_k=5)  # Returns: List[Document]
rag.retrieve_all_documents()  # Returns: List[Document]
```

## Best Practices

### ✅ DO:
- Use auto-cleanup endpoint (`/api/questions/query/cleanup`) for one-shot operations
- Check collection status before deletion
- Delete collections you're not actively using
- Recreate collections after cleanup when uploading new documents

### ❌ DON'T:
- Delete a collection while MCQ generation is in progress
- Forget to save MCQ results before deleting (response will still contain them)
- Assume collection exists without checking status first
- Delete shared collections without coordinating with other users

## Error Handling

### Collection Not Found
```json
{
  "error": "Collection 'pdf_chunks' not found",
  "status": "failed"
}
```

### Qdrant Connection Error
```json
{
  "error": "Failed to connect to Qdrant",
  "message": "Failed to delete collection"
}
```

### Solutions:
1. Verify Qdrant URL and API key in `.env`
2. Check Qdrant service is running
3. Confirm collection name is correct
4. Check network connectivity

## FAQ

**Q: Will my generated MCQs be lost if I delete the collection?**  
A: No! The MCQs are returned in the API response before deletion. Deletion only removes the vector store data.

**Q: Can I recreate a collection after deleting it?**  
A: Yes, use the `/api/collection/recreate` endpoint or simply upload new documents.

**Q: Is deletion permanent?**  
A: Yes, deletion is permanent. No backup is created. Save your MCQ results before deletion.

**Q: Can I delete a collection while it's being queried?**  
A: Avoid this. Wait for active queries/uploads to complete first.

**Q: What happens if deletion fails?**  
A: Check the error message. Usually it's a connection issue. Retry after fixing the connection.

## Environment Variables

No additional environment variables needed. Uses existing Qdrant configuration:

```env
qdrant_cluster_url=your-url
qdrant_api_key=your-key
```

## See Also

- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [RAG_MCQ_GUIDE.md](RAG_MCQ_GUIDE.md) - Comprehensive guide
- [rag_demo.py](../rag_demo.py) - Python examples
