from openai import OpenAI
from env import OAI_API_KEY, GEMINI_API_KEY

def get_openai_client():
    return OpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )