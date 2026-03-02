# Collection Cleanup - Quick Reference

## 🗑️ New Endpoints Added

### 1. Delete Collection
```
DELETE /api/collection/delete?collection_name=pdf_chunks
```
Permanently removes the collection from Qdrant.

### 2. Recreate Collection  
```
POST /api/collection/recreate?collection_name=pdf_chunks
```
Creates a fresh empty collection after deletion.

### 3. Generate & Auto-Cleanup
```
POST /api/questions/query/cleanup
Body: {"query": "...", "num_questions": 5, "top_k": 5}
```
Generates MCQs and deletes collection in one step (ideal for one-shot operations).

---

## 🐍 New Python Methods

### MCQGenerator
```python
# Delete collection
generator.cleanup_collection() → bool

# Generate and auto-cleanup
generator.generate_and_cleanup(query, num_questions, top_k) → dict
```

### Rag
```python
# Delete collection
rag.delete_collection(collection_name=None) → bool

# Recreate collection
rag.recreate_collection() → bool
```

---

## 💡 Usage Examples

### One-Shot: Upload → Generate → Delete
```bash
# Upload
curl -X POST "http://localhost:8000/api/upload" -F "file=@doc.pdf"

# Generate & cleanup in one call
curl -X POST "http://localhost:8000/api/questions/query/cleanup" \
  -d '{"query": "topic", "num_questions": 10}'
# Done! Collection is cleaned up
```

### Multi-Step: Keep Collection, Delete Later
```bash
# Upload & keep
curl -X POST "http://localhost:8000/api/upload" -F "file=@doc.pdf"

# Generate multiple times
curl -X POST "http://localhost:8000/api/questions/query" \
  -d '{"query": "topic1", "num_questions": 5}'
curl -X POST "http://localhost:8000/api/questions/query" \
  -d '{"query": "topic2", "num_questions": 5}'

# Delete when done
curl -X DELETE "http://localhost:8000/api/collection/delete"
```

### Python: Manual Control
```python
from src.service.prepareMCQ import MCQGenerator

generator = MCQGenerator()

# Do work
result = generator.generate_mcq_from_query("ml", num_questions=5)

# Safe the results
save_to_database(result['questions'])

# Clean up
generator.cleanup_collection()
```

---

## 📊 Endpoint Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload` | POST | Upload documents |
| `/api/questions/query` | POST | Generate MCQs from query |
| `/api/questions/all` | POST | Generate MCQs from all docs |
| `/api/questions/query/cleanup` | POST | **Generate MCQs & delete collection** |
| `/api/questions/status` | GET | Check collection status |
| `/api/collection/delete` | DELETE | **Delete collection** |
| `/api/collection/recreate` | POST | **Recreate collection** |

---

## ⚠️ Important Notes

✅ **MCQ data is returned before deletion** - You get the results in the response  
✅ **Deletion is immediate** - No backup created  
✅ **Collection can be recreated** - Just upload documents again  
❌ **Deletion is permanent** - Cannot undo!  
❌ **Cannot delete during active operations** - Wait for completion first

---

## 🔍 Check Before Delete

```bash
# See what's in collection before deleting
curl "http://localhost:8000/api/questions/status"
```

---

## 📝 File Changes

- **src/service/rag.py** - Added `delete_collection()`, `recreate_collection()`
- **src/service/prepareMCQ.py** - Added `cleanup_collection()`, `generate_and_cleanup()`
- **src/controller/uploadFile.py** - Added 3 new endpoints
- **CLEANUP_GUIDE.md** - Full cleanup documentation (NEW)

---

## See Also

- [CLEANUP_GUIDE.md](CLEANUP_GUIDE.md) - Comprehensive cleanup guide
- [QUICKSTART.md](QUICKSTART.md) - Setup & basic usage
- [RAG_MCQ_GUIDE.md](RAG_MCQ_GUIDE.md) - Full API reference
