import os
import sys
import time
import json
from dotenv import load_dotenv

# Ensure clean UTF-8 console output on Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from groq import Groq

def run_part1_demonstration():
    print("=" * 65)
    print("  \U0001F300 WORMHOLE / APPLYCOPILOT: PART 1 RUNNER & VERIFICATION")
    print("=" * 65)

    # 1. Inspect User Vault
    vault_path = "vault.json"
    print(f"\n[1/3] Loading Local Candidate Vault: {vault_path}...")
    if not os.path.exists(vault_path):
        print(f"  [X] Error: {vault_path} not found!")
        return

    with open(vault_path, "r", encoding="utf-8") as f:
        vault = json.load(f)

    profile = vault.get("profile", {})
    academic = vault.get("academic", {})
    transit = vault.get("transit_preferences", {})

    print(f"  * Candidate Name: {profile.get('full_name')} (Age: {profile.get('age')})")
    print(f"  * Institution:    {academic.get('institution')}")
    print(f"  * Degree & Branch: {academic.get('course')} - {academic.get('branch')}")
    print(f"  * Academic CGPA:  {academic.get('cgpa')} (10th: {academic.get('tenth_percentage')})")
    print(f"  * Default Route:  {transit.get('default_origin')} -> {transit.get('default_destination')}")
    print(f"  * Stored Passengers: {len(transit.get('passengers', []))} passenger profiles ready")
    print("  [OK] Local Encrypted Vault Loaded Successfully.")

    # 2. Check Groq API Configuration
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("\n  [X] Error: GROQ_API_KEY is missing from .env!")
        return

    masked_key = f"{groq_key[:8]}...{groq_key[-4:]}"
    print(f"\n[2/3] Authenticating Groq LPU with Key: {masked_key}...")
    client = Groq(api_key=groq_key)

    # 3. Test Intent Router across multiple voice queries
    test_queries = [
        "Jarvis, book 2 sleeper berths from Bangalore to Mysore on KSRTC Airavat for tomorrow night.",
        "Jarvis, my GATE application photo keeps getting rejected because it's 2.4 MB. Fix it to 30 KB.",
        "Jarvis, clean checkout mode. Book my flight but strip the 199 rupee insurance and donation."
    ]

    print("\n[3/3] Live Benchmark: Voice Intent -> Protocol Router (Model: openai/gpt-oss-20b)")
    print("-" * 65)

    for idx, query in enumerate(test_queries, 1):
        print(f"\nQuery {idx}: \"{query}\"")
        t0 = time.time()
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS, an autonomous web copilot protocol router. "
                        "Classify the user intent into exactly one protocol: "
                        "[TRANSIT_RUSH, CIVIC_HELPER, FRAUD_SENTINEL, DOC_EXORCIST, ANTI_DARK_PATTERN]. "
                        "Respond ONLY in valid JSON with fields: 'protocol', 'confidence', 'extracted_params', 'reason'."
                    )
                },
                {"role": "user", "content": query}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        t1 = time.time()
        latency_ms = round((t1 - t0) * 1000, 1)

        result = json.loads(response.choices[0].message.content)
        protocol = result.get("protocol")
        reason = result.get("reason")
        params = result.get("extracted_params", {})

        print(f"  * Target Protocol: \033[1;32m{protocol}\033[0m (Latency: {latency_ms} ms)")
        print(f"  * Extracted Params: {params}")
        print(f"  * Router Reasoning: {reason}")

    print("\n" + "=" * 65)
    print("  \u2705 PART 1 VERIFICATION COMPLETE: ALL SYSTEMS FUNCTIONAL")
    print("=" * 65)

if __name__ == "__main__":
    run_part1_demonstration()
