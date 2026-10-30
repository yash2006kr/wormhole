import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

models = client.models.list()
print("All available Groq models:")
for m in sorted(models.data, key=lambda x: x.id):
    print("  -", m.id)
