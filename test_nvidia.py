import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("/Users/shreyas/Desktop/Bruno_Assistant/.env")
client = OpenAI(
  base_url = "https://api.groq.com/openai/v1",
  api_key = os.environ.get("OPENAI_API_KEY")
)

try:
    completion = client.chat.completions.create(
      model="llama-3.3-70b-versatile",
      messages=[{"role":"user","content":"what is 2 plus 2"}],
      max_tokens=1024,
      tools=[{
          "type": "function",
          "function": {
              "name": "get_time",
              "description": "Gets time",
              "parameters": {"type": "object", "properties": {}}
          }
      }]
    )
    print("Tools completion:", completion.choices[0].message.content)
except Exception as e:
    print("Tools completion failed:", e)
