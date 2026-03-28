from dotenv import load_dotenv
import os
from pathlib import Path
from groq import Groq

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "summarize.txt").read_text(encoding="utf-8")
load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def summarize_article(article: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": ""
            }])
    return response.choices[0].message.content