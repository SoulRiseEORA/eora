
import os
from dotenv import load_dotenv

load_dotenv()

def get_openai_client():
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing in environment.")
    return OpenAI(api_key=api_key)
