import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API KEY LOADED:", bool(api_key))

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not loaded")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents="Reply with exactly: Gemini is working."
)

print("\nGEMINI RESPONSE:")
print(response.text)