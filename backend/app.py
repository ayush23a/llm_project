from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM as Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from langserve import add_routes
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


# Fastapi Setup
app = FastAPI(
    title="LLM API",
    description="An API for interacting with multiple LLMs using LangServe",
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


class QuestionInput(BaseModel):
    questions: str



@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "Welcome to the LLM API. Visit /docs for API documentation."}


# Set up LLMs
model_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.8)
llm_llama = Ollama(model='llama3.2:1b', temperature= 0.8)
llm_gemma = Ollama(model='gemma2:2b', temperature= 0.8)

# Define the prompt templates
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
        
        Understand the user's intent and give the best possible response.'''
    ),
    ("user", "Query:{questions}")
])


#add routes for the LLMs

add_routes(
    app,
    prompt | model_gemini | StrOutputParser(),
    path="/gemini_chat",
    input_type=QuestionInput
)

add_routes(
    app,
    prompt | llm_llama | StrOutputParser(),
    path="/llama_chat",
    input_type=QuestionInput
)

add_routes(
    app,
    prompt | llm_gemma | StrOutputParser(),
    path="/gemma_chat",
    input_type=QuestionInput
)


