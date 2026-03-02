# RAG MCQ Generator - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Prerequisites
```bash
# Ensure you have:
- Python 3.13+
- Qdrant running (cloud or local)
- HuggingFace API token
```

### 2. Environment Setup
Create a `.env` file in the project root:

```env
# Qdrant Configuration
qdrant_cluster_url=https://your-qdrant-instance.com
qdrant_api_key=your-api-key

# HuggingFace Token
HF_TOKEN=your-huggingface-token
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Start the Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`

---

## 📊 Common Operations

### Upload a Document
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@yourfile.pdf"
```

### Generate MCQs on a Topic
```bash
curl -X POST "http://localhost:8000/api/questions/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "num_questions": 5}'
```

### Generate from All Documents
```bash
curl -X POST "http://localhost:8000/api/questions/all" \
  -H "Content-Type: application/json" \
  -d '{"num_questions": 10}'
```

### Generate & Auto-Delete Collection
```bash
curl -X POST "http://localhost:8000/api/questions/query/cleanup" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "num_questions": 5}'
```

### Delete Collection
```bash
curl -X DELETE "http://localhost:8000/api/collection/delete"
```

### Recreate Collection
```bash
curl -X POST "http://localhost:8000/api/collection/recreate"
```

---

## 🐍 Python Usage

```python
from src.service.prepareMCQ import MCQGenerator

# Initialize
generator = MCQGenerator()

# Option 1: Generate from query
result = generator.generate_mcq_from_query(
    query="What is machine learning?",
    num_questions=5
)
print(result['questions'])

# Option 2: Generate from all documents
questions = generator.generate_mcq_from_all_content(num_questions=10)

# Option 3: Generate and auto-cleanup
result = generator.generate_and_cleanup(
    query="machine learning",
    num_questions=5
)

# Option 4: Just retrieve documents
docs = generator.retrieve_content("neural networks", top_k=5)

# Option 5: Manual cleanup
generator.cleanup_collection()
```

---

## 📁 Project Structure

```
src/
├── controller/uploadFile.py    ← REST API endpoints
├── service/
│   ├── prepareMCQ.py           ← MCQ generation logic
│   └── rag.py                  ← Qdrant integration
└── models/llama3.py            ← LLM configuration
```

---

## 🔑 Key Features

✅ **RAG Pipeline**: Retrieves relevant content from Qdrant  
✅ **Intelligent MCQs**: Uses Llama 3.3 to generate quality questions  
✅ **Batch Processing**: Generate MCQs from all documents at once  
✅ **Semantic Search**: Find documents by meaning, not just keywords  
✅ **REST API**: Easy integration with any frontend  
✅ **JSON Structured Output**: Ready for database storage or frontend rendering  

---

## 🛠️ Main Classes & Methods

### MCQGenerator
```python
# Retrieve content
retrieve_content(query, top_k=5)
retrieve_all_content()

# Generate MCQs
generate_mcq_from_query(query, num_questions=5, top_k=5)
generate_mcq_from_all_content(num_questions=10, batch_size=5)

# Advanced
create_rag_chain()
get_llm()
```

### Rag
```python
retrieve_documents(query, top_k=5)
retrieve_all_documents()
get_retriever(top_k=5)
```

---

## 📝 MCQ Output Format

```json
{
  "question": "What is machine learning?",
  "options": [
    "A field of AI studying human behavior",
    "A technique for computers to learn from data",
    "A programming language",
    "A type of database"
  ],
  "correct_answer": "B",
  "explanation": "Machine learning is a subset of AI that enables computers to improve performance through experience without being explicitly programmed."
}
```

---

## ⚡ Performance Tips

| Scenario | Recommendation |
|----------|-----------------|
| Small collection (<100 docs) | `top_k=3-5`, batch_size=5 |
| Medium collection (100-1k docs) | `top_k=5-10`, batch_size=10 |
| Large collection (>1k docs) | `top_k=10-15`, batch_size=20 |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| No documents found | Upload files first using `/api/upload` |
| API errors | Check Qdrant URL and API key in `.env` |
| Generation fails | Verify HuggingFace token is valid |
| Empty responses | Query might not match document content |

---

## 📚 Next Steps

1. Read [RAG_MCQ_GUIDE.md](RAG_MCQ_GUIDE.md) for detailed documentation
2. Run `python rag_demo.py` to see all examples
3. Integrate the API endpoints into your frontend
4. Customize MCQ prompts in `prepareMCQ.py` for your use case

---

## 🎯 Typical Workflow

```
1. Upload Document → /api/upload
2. Check Status → /api/questions/status
3. Generate MCQs → /api/questions/query OR /api/questions/all
4. Process & Display → Use returned JSON in your application
```

---

**Need help?** Check the detailed guide or examine the demo script: `python rag_demo.py`
