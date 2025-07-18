from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv("os.env")

app = FastAPI(
    title="Compliance Copilot API",
    description="Generates natural language explanations from structured compliance data."
)

#pydantic models for request & response
class RawJsonInput(BaseModel):
    json_data: dict

class ExplanationResponse(BaseModel):
    explanation: str

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.post("/generate_explanation", response_model=ExplanationResponse)
async def generate_explanation(request_body: RawJsonInput = Body(...)):
    """gets json and translates it into response for end users"""
    try:
        parsed_data = request_body.json_data
        formatted_json_for_prompt = json.dumps(parsed_data, indent=2)

        prompt = f"""
        You are a Compliance Copilot for Digio. Your task is to analyze structured ID verification results in JSON format and generate a clear, accurate, and actionable natural language explanation.

        **CRITICAL WRITING RULES**:
        The explanation should be tailored for end-users or support teams and must:
        - Start with a concise summary of the overall verification status.
        - Use bullet points to list specific issues.
        - Translate technical terms (e.g., "selfie_image_score", "template_match", "edge_noise") into easy-to-understand language.
        - Clearly state what the user can do to fix each issue.
        - Maintain a helpful and professional simple tone.
        - Be short and concise wwhile writing bullet points.
        - If all checks pass, state that the verification was successful.

        Here is the structured compliance data:
        ```json
        {formatted_json_for_prompt}
        ```

        Based on this data, generate the explanation:
        """
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                top_k=40,
                top_p=0.95,
                max_output_tokens=500
            )
        )

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            generated_text = response.candidates[0].content.parts[0].text
            return {"explanation": generated_text}
        else:
            raise HTTPException(status_code=500, detail="Gemini API did not return a valid explanation or was blocked.")

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON string provided in the 'json_data' field.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during generation: {e}")