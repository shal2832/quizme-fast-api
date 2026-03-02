import json
from typing import List, Optional, Dict, Any
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from src.models.llama3 import get_llm, llm_invoke
from src.service.rag import Rag


class MCQGenerator:
    """
    RAG-based MCQ Generator that retrieves content from Qdrant
    and generates multiple choice questions using LLaMA
    """
    
    def __init__(self, collection_name: str = 'pdf_chunks'):
        """
        Initialize the MCQ Generator with RAG pipeline
        
        Args:
            collection_name: Name of the Qdrant collection to retrieve from
        """
        self.rag = Rag(collection_name=collection_name)
        self.llm = get_llm()
        
    def retrieve_content(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Retrieve relevant content from Qdrant based on query
        
        Args:
            query: Search query for similar documents
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        print(f"Retrieving top {top_k} relevant documents for query: {query}")
        documents = self.rag.retrieve_documents(query, top_k=top_k)
        return documents
    
    def retrieve_all_content(self) -> List[Document]:
        """
        Retrieve all documents from the Qdrant collection
        
        Returns:
            List of all documents in the collection
        """
        print("Retrieving all documents from Qdrant collection...")
        documents = self.rag.retrieve_all_documents()
        return documents
    
    def format_context(self, documents: List[Document]) -> str:
        """
        Format retrieved documents into context string
        
        Args:
            documents: List of Document objects
            
        Returns:
            Formatted context string
        """
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"Document {i}:\n{doc.page_content}\n")
        
        return "\n".join(context_parts)
    
    def generate_mcq_from_content(self, content: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """
        Generate MCQs from the provided content
        
        Args:
            content: The content to generate questions from
            num_questions: Number of MCQs to generate
            
        Returns:
            List of MCQ dictionaries containing question, options, and answer
        """
        prompt = f"""Based on the following content, generate exactly {num_questions} multiple choice questions with 4 options each. 
The questions should be clear, educational, and relevant to the content provided.

Content:
{content}

Generate the questions in the following JSON format:
{{
    "questions": [
        {{
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Correct option letter (A/B/C/D)",
            "explanation": "Brief explanation of why this is correct"
        }}
    ]
}}

Ensure the output is valid JSON and contains exactly {num_questions} questions."""

        system_prompt = """You are an expert MCQ generator. Create educational, clear, and engaging multiple choice questions based on the provided content. 
Always format your response as valid JSON with the structure specified. The questions should test understanding of key concepts."""
        
        try:
            response = llm_invoke(prompt, system_prompt=system_prompt)
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                mcqs = json.loads(json_str)
                return mcqs.get('questions', [])
            else:
                print("Warning: Could not find JSON in response")
                return []
                
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return []
        except Exception as e:
            print(f"Error generating MCQs: {e}")
            return []
    
    def generate_mcq_from_query(self, query: str, num_questions: int = 5, top_k: int = 5) -> Dict[str, Any]:
        """
        Complete RAG pipeline: Retrieve content based on query and generate MCQs
        
        Args:
            query: Search query for retrieving relevant documents
            num_questions: Number of MCQs to generate
            top_k: Number of documents to retrieve for context
            
        Returns:
            Dictionary containing query, retrieved documents, and generated MCQs
        """
        print(f"\n{'='*60}")
        print(f"MCQ Generation Pipeline for Query: {query}")
        print(f"{'='*60}")
        
        # Step 1: Retrieve relevant documents
        documents = self.retrieve_content(query, top_k=top_k)
        
        if not documents:
            print("No relevant documents found in the collection.")
            return {
                "query": query,
                "documents": [],
                "questions": [],
                "status": "No documents found"
            }
        
        print(f"Retrieved {len(documents)} relevant documents")
        
        # Step 2: Format context
        context = self.format_context(documents)
        
        # Step 3: Generate MCQs
        print(f"Generating {num_questions} MCQs from retrieved content...")
        questions = self.generate_mcq_from_content(context, num_questions=num_questions)
        
        return {
            "query": query,
            "num_documents_retrieved": len(documents),
            "documents": [{"content": doc.page_content, "metadata": doc.metadata} for doc in documents],
            "questions": questions,
            "total_questions_generated": len(questions),
            "status": "success"
        }
    
    def generate_mcq_from_all_content(self, num_questions: int = 10, batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        Generate MCQs from all documents in the Qdrant collection
        
        Args:
            num_questions: Total number of MCQs to generate
            batch_size: Number of documents to process in each batch
            
        Returns:
            List of generated MCQs
        """
        print(f"\n{'='*60}")
        print(f"Generating MCQs from All Documents in Collection")
        print(f"{'='*60}")
        
        # Retrieve all documents
        all_documents = self.retrieve_all_content()
        
        if not all_documents:
            print("No documents found in the collection.")
            return []
        
        print(f"Found {len(all_documents)} documents in collection")
        
        all_questions = []
        questions_per_batch = max(1, num_questions // ((len(all_documents) + batch_size - 1) // batch_size))
        
        # Process documents in batches
        for i in range(0, len(all_documents), batch_size):
            batch = all_documents[i:i + batch_size]
            context = self.format_context(batch)
            
            print(f"\nProcessing batch {i // batch_size + 1} ({len(batch)} documents)")
            questions = self.generate_mcq_from_content(context, num_questions=questions_per_batch)
            all_questions.extend(questions)
            
            if len(all_questions) >= num_questions:
                break
        
        # Trim to exact number requested
        all_questions = all_questions[:num_questions]
        
        print(f"\n{'='*60}")
        print(f"Total MCQs Generated: {len(all_questions)}")
        print(f"{'='*60}\n")
        
        return all_questions
    
    def create_rag_chain(self):
        """
        Create a LangChain RetrievalQA chain for MCQ generation
        
        Returns:
            RetrievalQA chain instance
        """
        retriever = self.rag.get_retriever(top_k=5)
        
        prompt_template = """You are an expert MCQ generator. Based on the following context, generate 5 multiple choice questions.

Context:
{context}

Question: Generate 5 multiple choice questions based on the above context in JSON format with structure: {{"questions": [{{"question": "...", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "..."}}]}}

Answer:"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context"]
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
        
        return qa_chain
    
    def generate_with_rag_chain(self, query: str) -> Dict[str, Any]:
        """
        Generate MCQs using the RetrievalQA chain
        
        Args:
            query: Query for MCQ generation
            
        Returns:
            Generated MCQs from the chain
        """
        rag_chain = self.create_rag_chain()
        result = rag_chain.invoke({"query": query})
        
        return {
            "query": query,
            "result": result.get("result", ""),
            "source_documents": [{"content": doc.page_content, "metadata": doc.metadata} for doc in result.get("source_documents", [])]
        }
    
    def cleanup_collection(self) -> bool:
        """
        Delete the collection from Qdrant after MCQ generation is complete.
        Useful for cleanup and resource management.
        
        Returns:
            True if deletion was successful, False otherwise
        """
        return self.rag.delete_collection()
    
    def generate_and_cleanup(self, query: str, num_questions: int = 5, top_k: int = 5) -> Dict[str, Any]:
        """
        Complete workflow: Generate MCQs from query and then delete the collection.
        
        Args:
            query: Search query for retrieving relevant documents
            num_questions: Number of MCQs to generate
            top_k: Number of documents to retrieve for context
            
        Returns:
            Dictionary containing generated questions and cleanup status
        """
        print(f"\n{'='*60}")
        print(f"MCQ Generation with Auto-Cleanup")
        print(f"{'='*60}")
        
        # Generate MCQs
        result = self.generate_mcq_from_query(
            query=query,
            num_questions=num_questions,
            top_k=top_k
        )
        
        # Delete collection
        print("\nCleaning up Qdrant collection...")
        cleanup_success = self.cleanup_collection()
        
        result['cleanup_status'] = 'success' if cleanup_success else 'failed'
        
        return result


# Example usage function
def example_usage():
    """Example of how to use the MCQGenerator"""
    
    # Initialize the generator
    generator = MCQGenerator()
    
    # Option 1: Generate MCQs from a specific query
    result = generator.generate_mcq_from_query(
        query="What are the key concepts of machine learning?",
        num_questions=5,
        top_k=5
    )
    print(json.dumps(result, indent=2))
    
    # Option 2: Generate MCQs from all documents
    all_questions = generator.generate_mcq_from_all_content(num_questions=10)
    print(json.dumps(all_questions, indent=2))
