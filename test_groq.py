import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
print(f"Testing Groq API with key: {groq_key[:8]}...{groq_key[-4:]}")

client = Groq(api_key=groq_key)

model_choice = "openai/gpt-oss-20b"
print(f"Testing with model: {model_choice}...")

t0 = time.time()
response = client.chat.completions.create(
    model=model_choice,
    messages=[
        {"role": "system", "content": "You are JARVIS intent classifier. Respond ONLY in valid JSON with fields: 'protocol' (one of TRANSIT_RUSH, CIVIC_HELPER, FRAUD_SENTINEL, DOC_EXORCIST, ANTI_DARK_PATTERN), and 'reason'."},
        {"role": "user", "content": "Jarvis, book 2 sleeper berths from Bangalore to Mysore on KSRTC Airavat for tomorrow night."}
    ],
    temperature=0.1,
    response_format={"type": "json_object"}
)
t1 = time.time()

print(f"Latency: {round((t1 - t0)*1000, 1)} ms")
print("Response content:")
print(response.choices[0].message.content)
