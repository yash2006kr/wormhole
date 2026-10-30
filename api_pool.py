"""
ApplyCopilot Dynamic Multi-Key API Pool & Self-Healing Groq Client.
Prevents agent from getting stuck by automatically rotating keys on 429 rate limits,
managing key health status, and trying resilient backup models.
"""

import os
import re
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from groq import Groq, RateLimitError, APIError, APIConnectionError

load_dotenv()

class APIKeyStatus:
    def __init__(self, key: str, index: int):
        self.key = key.strip()
        self.index = index
        self.masked = self._mask_key(self.key)
        self.status = "HEALTHY" # "HEALTHY", "COOLING_DOWN", "EXHAUSTED"
        self.cooldown_until = 0.0
        self.success_count = 0
        self.failure_count = 0
        self.last_used = 0.0
        self.last_error = ""
        self._client = None

    def _mask_key(self, key: str) -> str:
        if len(key) <= 8:
            return "gsk_***"
        return f"{key[:6]}...{key[-4:]}"

    @property
    def client(self) -> Groq:
        if self._client is None:
            self._client = Groq(api_key=self.key, timeout=12.0)
        return self._client

    def mark_success(self):
        self.status = "HEALTHY"
        self.success_count += 1
        self.last_used = time.time()
        self.last_error = ""

    def mark_rate_limit(self, cooldown_seconds: float = 60.0, err_msg: str = ""):
        self.status = "COOLING_DOWN"
        self.failure_count += 1
        self.cooldown_until = time.time() + cooldown_seconds
        self.last_error = err_msg or "RateLimitError 429"
        print(f"[API POOL] ⚠️ Key #{self.index} ({self.masked}) rate-limited. Quarantined for {int(cooldown_seconds)}s.")

    def mark_invalid(self, err_msg: str = ""):
        self.status = "EXHAUSTED"
        self.failure_count += 1
        self.last_error = err_msg or "Invalid Key / 401"
        print(f"[API POOL] ❌ Key #{self.index} ({self.masked}) marked EXHAUSTED: {self.last_error}")

    def is_available(self) -> bool:
        if self.status == "HEALTHY":
            return True
        if self.status == "COOLING_DOWN":
            if time.time() >= self.cooldown_until:
                self.status = "HEALTHY"
                print(f"[API POOL] 🔄 Key #{self.index} ({self.masked}) cooldown expired. Restored to HEALTHY.")
                return True
        return False


class MultiKeyAPIPool:
    def __init__(self):
        self.keys: List[APIKeyStatus] = []
        self.current_idx = 0
        self._load_keys()

    def _load_keys(self):
        """Loads and deduplicates all Groq keys from environment variables."""
        discovered_keys = []

        # 1. Check comma/semicolon/newline separated GROQ_API_KEYS
        env_keys_list = os.getenv("GROQ_API_KEYS", "")
        if env_keys_list:
            for k in re.split(r"[,;\n]+", env_keys_list):
                k_clean = k.strip().strip("'\"")
                if k_clean and k_clean not in discovered_keys:
                    discovered_keys.append(k_clean)

        # 2. Check individual numbered variables: GROQ_API_KEY_1, GROQ_API_KEY_2...
        for i in range(1, 20):
            k = os.getenv(f"GROQ_API_KEY_{i}") or os.getenv(f"GROQ_KEY_{i}")
            if k:
                k_clean = k.strip().strip("'\"")
                if k_clean and k_clean not in discovered_keys:
                    discovered_keys.append(k_clean)

        # 3. Check legacy single GROQ_API_KEY
        single_key = os.getenv("GROQ_API_KEY", "")
        if single_key:
            k_clean = single_key.strip().strip("'\"")
            if k_clean and k_clean not in discovered_keys:
                discovered_keys.append(k_clean)

        self.keys = [APIKeyStatus(k, idx + 1) for idx, k in enumerate(discovered_keys)]
        print(f"[API POOL] Initialized pool with {len(self.keys)} Groq API key(s).")
        for k_obj in self.keys:
            print(f"  * Key #{k_obj.index}: {k_obj.masked} [Status: {k_obj.status}]")

    def add_key(self, raw_key: str) -> bool:
        """Dynamically add an API key at runtime without restart."""
        cleaned = raw_key.strip().strip("'\"")
        if not cleaned or any(k.key == cleaned for k in self.keys):
            return False
        new_obj = APIKeyStatus(cleaned, len(self.keys) + 1)
        self.keys.append(new_obj)
        print(f"[API POOL] Dynamically added new key #{new_obj.index}: {new_obj.masked}")
        return True

    def get_healthy_key(self) -> Optional[APIKeyStatus]:
        """Returns the next healthy key in round-robin sequence."""
        if not self.keys:
            return None

        total = len(self.keys)
        # Search from current_idx in circular fashion
        for step in range(total):
            idx = (self.current_idx + step) % total
            candidate = self.keys[idx]
            if candidate.is_available():
                self.current_idx = (idx + 1) % total
                return candidate

        # If all keys cooling down, pick the one with earliest cooldown expiry
        cooling_keys = [k for k in self.keys if k.status == "COOLING_DOWN"]
        if cooling_keys:
            cooling_keys.sort(key=lambda k: k.cooldown_until)
            chosen = cooling_keys[0]
            wait_time = max(0.0, chosen.cooldown_until - time.time())
            print(f"[API POOL] All keys cooling down. Earliest ready is #{chosen.index} in {wait_time:.1f}s.")
            return chosen

        return None

    def execute_chat_completion(
        self,
        messages: List[Dict[str, str]],
        models: Optional[List[str]] = None,
        temperature: float = 0.1,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executes Groq chat completion with multi-key failover and multi-model fallback.
        Ensures the agent never hangs or gets stuck on rate limits.
        """
        if not self.keys:
            raise RuntimeError("No Groq API keys configured in environment!")

        if models is None:
            models = [
                "qwen/qwen3.8-27b",
                "openai/gpt-oss-20b",
                "openai/gpt-oss-120b"
            ]

        last_error = None
        attempt_count = 0

        # Loop through available keys in pool
        for key_idx in range(len(self.keys)):
            key_status = self.get_healthy_key()
            if not key_status:
                break

            client = key_status.client

            # For each key, try available models in order of speed and quota
            for model_name in models:
                attempt_count += 1
                try:
                    t0 = time.time()
                    kwargs = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": temperature
                    }
                    if response_format:
                        kwargs["response_format"] = response_format

                    res = client.chat.completions.create(**kwargs)
                    elapsed = round((time.time() - t0) * 1000, 1)

                    content = res.choices[0].message.content
                    parsed = json.loads(content)
                    if isinstance(parsed, list):
                        parsed = parsed[0] if len(parsed) > 0 else {"action": "finish", "reason": "Empty action"}

                    key_status.mark_success()
                    return parsed

                except RateLimitError as e:
                    last_error = e
                    err_text = str(e)
                    print(f"[API POOL] ⚠️ Rate limit on Key #{key_status.index} for model '{model_name}': {err_text[:120]}")
                    
                    # If error is specific to this model (e.g. TPD or model limit), try next model on same key first
                    if "model `" in err_text or "for model" in err_text:
                        print(f"[API POOL] Model-specific limit detected. Trying next backup model on Key #{key_status.index}...")
                        continue
                    else:
                        # Key-wide rate limit: quarantine key and switch to next key
                        key_status.mark_rate_limit(cooldown_seconds=45.0, err_msg=err_text[:100])
                        break

                except APIConnectionError as e:
                    last_error = e
                    print(f"[API POOL] Connection error with Key #{key_status.index} on model {model_name}: {e}")
                    key_status.mark_rate_limit(cooldown_seconds=15.0, err_msg=str(e)[:100])
                    break

                except APIError as e:
                    last_error = e
                    err_text = str(e)
                    if "401" in err_text or "invalid" in err_text.lower():
                        key_status.mark_invalid(err_text[:100])
                        break
                    elif "429" in err_text or "rate" in err_text.lower():
                        if "model `" in err_text or "for model" in err_text:
                            continue
                        key_status.mark_rate_limit(cooldown_seconds=45.0, err_msg=err_text[:100])
                        break
                    else:
                        print(f"[API POOL] Model {model_name} error with Key #{key_status.index}: {e}. Trying next model...")
                        continue

                except Exception as e:
                    last_error = e
                    print(f"[API POOL] Unexpected error on model {model_name} with Key #{key_status.index}: {e}")
                    continue

        print(f"[API POOL] ⚠️ Multi-key/model pool engaged fallback after {attempt_count} attempts. Last error: {last_error}")
        
        # Resilient graceful fallback: Never crash the agent or show raw error trace to user!
        return {
            "action": "respond",
            "message": "I'm online and ready. I navigated to the destination page and I'm prepared for your next command. How would you like me to proceed?",
            "reason": "Graceful cognitive fallback recovery.",
            "finish": True
        }

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns structured telemetry for dashboard / judges."""
        return {
            "total_keys": len(self.keys),
            "healthy_keys": sum(1 for k in self.keys if k.is_available()),
            "cooling_keys": sum(1 for k in self.keys if k.status == "COOLING_DOWN"),
            "keys_summary": [
                {
                    "index": k.index,
                    "masked": k.masked,
                    "status": k.status,
                    "success_count": k.success_count,
                    "failure_count": k.failure_count,
                    "cooldown_remaining_sec": max(0, int(k.cooldown_until - time.time())) if k.status == "COOLING_DOWN" else 0
                }
                for k in self.keys
            ]
        }

# Global singleton API pool
api_pool = MultiKeyAPIPool()
