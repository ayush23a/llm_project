from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM as Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi import FastAPI, UploadFile, Form, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, Dict, Any
from dotenv import load_dotenv
import os
import base64
import mimetypes

# --- Configuration & Initialization ---
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# FastAPI Setup
app = FastAPI(
    title="LLM API",
    description="An API for interacting with multiple LLMs with Multi-modal support",
    version="1.0.0",
)

# CORS Setup 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "Welcome to the LLM API. Visit /docs for API documentation."}


model_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.8,
    google_api_key=GOOGLE_API_KEY 
)
llm_llama = Ollama(model='llama3.2:1b', temperature= 0.8)
llm_gemma = Ollama(model='gemma2:2b', temperature= 0.8)


MODEL_RUNNABLES = {
    "gemini_chat": model_gemini,
    "llama_chat": llm_llama,
    "gemma_chat": llm_gemma
}

def process_image_input(query: str, mime_type: str, base64_image: str) -> Dict[str, Any]:
    """Creates the complex input structure required by ChatGoogleGenerativeAI for multi-modal input."""
    
    image_part = {
        "mime_type": mime_type,
        "data": base64_image
    }

    return {
        "questions": [
            {"type": "text", "text": query},
            {"type": "image_url", "image_url": image_part}
        ]
    }

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        '''You are a helpful assistant with a chill, friendly tone.
        Always format your responses clearly using the following rules:
        
        - Use short paragraphs.
        - Add line breaks between ideas.
        - Use bullet points, numbering, or headings when listing things.
        - Avoid long unformatted blocks of text.
        - Keep the tone friendly and natural, not overly formal.
        
        Analyze the user's input, including any attached files/content, and provide the best possible response.'''
    ),
    ("user", "Query:{questions}")
])

router = APIRouter(prefix="/api")

@router.post("/{model_name}/invoke")
async def invoke_model_with_file(
    model_name: str,
    questions: Annotated[str, Form()], 
    file: UploadFile = None, 
):
    # 1. Select the correct LLM
    if model_name not in MODEL_RUNNABLES:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
        
    llm = MODEL_RUNNABLES[model_name]
    runnable = prompt | llm | StrOutputParser()

    input_data = {"questions": questions} 
    
    if file and file.filename:
        content = await file.read()
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]

        # 2. HANDLE IMAGE INPUT (Multi-modal for Gemini only)
        if mime_type and mime_type.startswith('image/') and model_name == "gemini_chat":
            base64_image = base64.b64encode(content).decode('utf-8')
            input_data = process_image_input(questions, mime_type, base64_image)
        
        # 3. HANDLE TEXT/DOCUMENT INPUT (for all models)
        else:
            file_content = ""
            try:
                file_content = content.decode('utf-8')
            except UnicodeDecodeError:
                file_content = f"Attached binary file of type {mime_type} cannot be read as text."

            truncated_content = file_content[:2000]
            if len(file_content) > 2000:
                 truncated_content += "\n... [Content Truncated]"

            full_query = (
                f"{questions}\n\n"
                f"--- Attached File Content ({file.filename}) ---\n"
                f"{truncated_content}"
            )
            input_data = {"questions": full_query}

    # 4. Invoke the chain
    try:
        result = await runnable.ainvoke(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM invocation failed for {model_name}: {str(e)[:100]}...")

    return {"output": result}

app.include_router(router)
