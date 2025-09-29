from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM as Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from langserve import add_routes
from dotenv import load_dotenv
import os
from fastapi import FastAPI




load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

# Fastapi Setup
app = FastAPI(
    title="LLM API",
    description="An API for interacting with multiple LLMs using LangServe",
    version="1.0.0",
)


# Set up LLMs
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.8)
llm1 = Ollama(model='llama3.2:1b', temperature= 0.8)
llm2 = Ollama(model='gemma2:2b', temperature= 0.8)

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
    prompt | llm2 | StrOutputParser(),
    path="/chat",
    input_type=QuestionInput
)

