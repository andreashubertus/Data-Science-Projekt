from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def summarize_article(article: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Du bist ein hilfreicher Assistent der Nachrichtenartikel präzise und neutral zusammenfasst."
            },
            {
                "role": "user",
                "content": ""
            }])
    return response.choices[0].message.content