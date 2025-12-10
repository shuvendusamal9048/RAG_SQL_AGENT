
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY (or GOOGLE_API_KEY) not found in environment")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=API_KEY)
