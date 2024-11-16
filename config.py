import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")

# Define the model
llm_model = "gpt-3.5-turbo"

# Initialize the model
chat = ChatOpenAI(temperature=0.0, model=llm_model, api_key=openai_api_key)
