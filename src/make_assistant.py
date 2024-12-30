from openai import OpenAI
from prompts import assistant_prompt
from utils import get_openai_client

client = get_openai_client()

prompts = assistant_prompt()
assistant = client.beta.assistants.create(
  name="MirrorBot assistant",
  instructions=prompts["system"],
  model="gpt-4o",
)