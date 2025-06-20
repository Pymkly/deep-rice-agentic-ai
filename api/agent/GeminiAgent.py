import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from api.agent.main_agent import MainAgent

load_dotenv()
print(os.getenv("GOOGLE_API_KEY"))
class GeminiAgent (MainAgent):
    def __init__(self, tag, file_path):
        super().__init__(
            tag=tag,
            file_path = file_path,
            llm= ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
        )


