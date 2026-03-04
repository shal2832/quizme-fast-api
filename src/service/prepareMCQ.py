import json
import re
class MCQGenerator:
    """
    RAG-based MCQ Generator that retrieves content from Qdrant
    and generates multiple choice questions using LLaMA
    """
    def generate_mcq_response(llm_result : str):
        try:
            # 1. Strip out markdown code blocks if they exist
            clean_json = re.sub(r'^```json\s*|```$', '', llm_result, flags=re.MULTILINE)
            parsed_response = json.loads(clean_json)
            print(f"Extracted questions from LLM response: {clean_json}")
            return parsed_response
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")


