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
print("Loaded GOOGLE_API_KEY =", os.getenv("GOOGLE_API_KEY"))
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""  # Prevent ADC fallback
# os.environ["GOOGLE_AUTH_DISABLE_SSL_CERTIFICATE_CHECKS"] = "1" 


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

# Set up LLMs
model_gemini = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.8)
llm_llama = Ollama(model='llama3.2:1b', temperature= 0.8)
llm_gemma = Ollama(model='gemma2:2b', temperature= 0.8)

# Define the prompt templates
prompt = ChatPromptTemplate.from_messages([ 

    ("system", '''You are a helpul assistant. Your nature and tone is cool intelligent agent. you will communicate like a chill person. 
                You have to understand the user's intent behind the question he/she asks.
                Provide the best available results to the users related to their content of need only. Always behave in a very friendly manner with the user.'''),
    ("user", "Query:{questions}")
])

#add routes for the LLMs
# issue : have to add routes as per the model selected from frontend

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


