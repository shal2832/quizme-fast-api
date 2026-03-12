import json
import re
from src.models.llama3 import llm_invoke
from src.service.qdrantApiService import qdrantApiServiceInstance
class MCQGenerator:
    """
    RAG-based MCQ Generator that retrieves content from Qdrant
    and generates multiple choice questions using LLaMA
    """

    def format_mcq_response(self, llm_result : str):
        """
         Formats the MCQ response that is generate by LLM

         Args:
            llm_result : string

         Response:
            JSON with MCQ questions
        """
        try:
            # 1. Strip out markdown code blocks if they exist
            clean_json = re.sub(r'^```json\s*|```$', '', llm_result, flags=re.MULTILINE)
            
            # 2. Try to extract JSON object from the response using regex
            json_match = re.search(r'\{[\s\S]*\}', clean_json)
            if json_match:
                clean_json = json_match.group(0)
            
            # 3. Remove trailing commas before closing brackets/braces (common JSON error)
            clean_json = re.sub(r',(\s*[}\]])', r'\1', clean_json)
            
            # 4. Try to parse the JSON
            parsed_response = json.loads(clean_json)
            print(f"Extracted questions from LLM response: {len(parsed_response.get('questions', []))} questions")
            return parsed_response
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw LLM response was: {llm_result}")
            return {"questions": []}


    def generate_mcq_with_context(self,  num_of_questions: int, query: str = ""):
        """
        Generate multiple choice questions (MCQs) based on the provided content.
        It uses the LLM to create educational and relevant MCQs.
        """
        print(f"[MCQ Generation] Starting MCQ generation for {num_of_questions} questions")
        
        context = ""
        if(query):
            context_response = qdrantApiServiceInstance.query_api(query)
            print(f"[MCQ Generation] Query API response received with status code: {context_response.status_code}")
            context = context_response.json().get("context", "")
            print(f"[MCQ Generation] Context retrieved based on user query with length: {len(context)} characters")
        else:
            context_response = qdrantApiServiceInstance.entire_context_api()
            print(f"[MCQ Generation] Entire context API response received with status code: {context_response.status_code}")
            context = context_response.json().get("context", "")
            print(f"[MCQ Generation] Context retrieved based on user query with length: {len(context)} characters")

        
        print(f"[MCQ Generation] Context retrieved with length: {len(context)} characters")
        
        system_prompt = self.get_system_prompt(context)
        print(f"[MCQ Generation] System prompt created")
        
        user_prompt = self.get_user_prompt(num_of_questions)
        print(f"[MCQ Generation] User prompt created for {num_of_questions} questions")

        print(f"[MCQ Generation] Invoking LLM...")
        res = llm_invoke(user_prompt, system_prompt, True)
        print(f"[MCQ Generation] LLM response received with length: {len(res)} characters")
        
        collections_response_json = qdrantApiServiceInstance.list_collections_api()
        collections_response = collections_response_json.json().get("collections", [])
        print(f"[MCQ Generation] Deleting collection:{collections_response}")
        qdrantApiServiceInstance.delete_api(collections_response_json.json().get("collections", [])[0] if collections_response_json.json().get("collections", []) else "")
        
        print(f"[MCQ Generation] Formatting MCQ response...")
        formatted_response = self.format_mcq_response(res)
        print(f"[MCQ Generation] MCQ generation complete with {len(formatted_response.get('questions', []))} questions")
        return formatted_response

    def get_system_prompt(self, context):
        return f"""
                You are an expert MCQ generator. Create educational, clear, and engaging multiple choice questions based on the provided content. 
                Always format your response as valid JSON with the structure specified. The questions should test understanding of key concepts.
                Content: {context}
            """  
    def get_user_prompt(self, num_of_questions):
        return f"""Based on the following content, generate exactly {num_of_questions} multiple choice questions with 4 options each. 
                The questions should be clear, educational, and relevant to the content provided.

                Generate the questions in the following JSON format:
                {{
                    "questions": [
                        {{
                            "question": "Question text here?",
                            "options": [
                                {{"A" : "Option A"}}, 
                                {{"B" : "Option B"}},
                                {{"C" : "Option C"}},
                                {{"D" : "Option D"}},
                             ],
                            "correct_answer": "Correct option letter (A/B/C/D)",
                            "explanation": "Brief explanation of why this is correct"
                        }}
                    ]
                }}

                Ensure the output is valid only markdown JSON and contains exactly {num_of_questions} questions."""        


mcq_generator = MCQGenerator()