from openai import OpenAI

api_key = "***REMOVED***"

def get_openai_client():
    return OpenAI(
        api_key=api_key
    )