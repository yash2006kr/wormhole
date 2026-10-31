"""
ApplyCopilot Universal Multi-Provider API Pool & Self-Healing Client.
Seamlessly cascades between:
  1. Groq Cloud (Multi-Key Pool with automatic 429 rotation)
  2. Google Gemini 2.5 Flash (Google AI Studio REST API: 1M TPM / 1500 RPD Free)
  4. Cerebras Cloud (1M free tokens/day at 2000 tok/sec)
  5. Local Zero-Token Autonomous Engine (Zero external dependencies)

Guarantees the agent never hangs, crashes, or halts due to API rate limits or downtime.
"""

import os
import sys
import re
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

load_dotenv()

# ==============================================================================
# 1. GROQ KEY STATUS & CLIENT WRAPPER
# ==============================================================================
try:
    from groq import Groq, RateLimitError, APIError, APIConnectionError
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GroqKeyStatus:
    def __init__(self, key: str, index: int):
        self.key = key.strip()
        self.index = index
        self.masked = self._mask_key(self.key)
        self.status = "HEALTHY"  # "HEALTHY", "COOLING_DOWN", "EXHAUSTED"
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
    def client(self):
        if not GROQ_AVAILABLE:
            return None
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
        print(f"[API POOL] [!WARN] Groq Key #{self.index} ({self.masked}) rate-limited. Quarantined for {int(cooldown_seconds)}s.")

    def mark_invalid(self, err_msg: str = ""):
        self.status = "EXHAUSTED"
        self.failure_count += 1
        self.last_error = err_msg or "Invalid Key / 401"
        print(f"[API POOL] [ERROR] Groq Key #{self.index} ({self.masked}) marked EXHAUSTED: {self.last_error}")

    def is_available(self) -> bool:
        if self.status == "HEALTHY":
            return True
        if self.status == "COOLING_DOWN":
            if time.time() >= self.cooldown_until:
                self.status = "HEALTHY"
                print(f"[API POOL] [FAILOVER] Groq Key #{self.index} ({self.masked}) cooldown expired. Restored to HEALTHY.")
                return True
        return False


# ==============================================================================
# 2. GOOGLE GEMINI 2.5 FLASH PROVIDER (Google AI Studio REST)
# ==============================================================================
class GeminiProvider:
    def __init__(self):
        self.keys: List[str] = []
        self.current_idx = 0
        self.cooldown_until = 0.0
        self.success_count = 0
        self.models = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]
        self._load_keys()

    def _load_keys(self):
        discovered = []
        for var in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_KEY"]:
            val = os.getenv(var, "").strip().strip("'\"")
            if val and val not in discovered:
                discovered.append(val)
        for i in range(1, 10):
            val = os.getenv(f"GEMINI_API_KEY_{i}", "").strip().strip("'\"")
            if val and val not in discovered:
                discovered.append(val)
        self.keys = discovered
        if self.keys:
            print(f"[API POOL] Initialized Google Gemini Provider with {len(self.keys)} key(s).")

    def execute(self, messages: List[Dict[str, str]], max_tokens: int = 300) -> Optional[Dict[str, Any]]:
        if not self.keys:
            return None
        if time.time() < self.cooldown_until:
            return None

        # Build prompt from messages
        prompt_parts = []
        for m in messages:
            role = m.get("role", "user").upper()
            content = m.get("content", "")
            prompt_parts.append(f"[{role}]:\n{content}")
        full_prompt = "\n\n".join(prompt_parts)
        full_prompt += "\n\nCRITICAL: Respond with a single valid JSON object only. Do NOT include markdown blocks."

        key = self.keys[self.current_idx % len(self.keys)]
        for model in self.models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.1
                }
            }
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    parsed = self._clean_and_parse_json(text)
                    if parsed and isinstance(parsed, dict) and parsed.get("action"):
                        self.success_count += 1
                        print(f"[API POOL] [OK] Gemini Provider ({model}) returned action: '{parsed.get('action')}'")
                        return parsed
            except urllib.error.HTTPError as e:
                err_body = ""
                try:
                    err_body = e.read().decode("utf-8")
                except Exception:
                    pass
                print(f"[API POOL] [!WARN] Gemini HTTP {e.code} on {model}: {err_body[:100]}")
                if e.code == 429:
                    self.cooldown_until = time.time() + 45.0
                    break
                elif e.code == 404:
                    continue
            except Exception as e:
                print(f"[API POOL] [!WARN] Gemini request error on {model}: {e}")
                continue

        return None

    def _clean_and_parse_json(self, raw: str) -> Optional[Dict[str, Any]]:
        text = raw.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        try:
            return json.loads(text)
        except Exception:
            match = re.search(r'"action"\s*:\s*"([^"]+)"', text)
            if match:
                return {"action": match.group(1), "message": text, "reason": "Parsed from response."}
            return None


# ==============================================================================
# 4. CEREBRAS CLOUD PROVIDER (1M Tokens/Day Free)
# ==============================================================================
class CerebrasProvider:
    def __init__(self):
        self.api_key = os.getenv("CEREBRAS_API_KEY", "").strip().strip("'\"")
        self.cooldown_until = 0.0
        self.models = ["llama-3.3-70b", "llama3.1-8b"]
        if self.api_key:
            print("[API POOL] Initialized Cerebras Cloud Provider.")

    def execute(self, messages: List[Dict[str, str]], max_tokens: int = 300) -> Optional[Dict[str, Any]]:
        if not self.api_key or time.time() < self.cooldown_until:
            return None

        url = "https://api.cerebras.ai/v1/chat/completions"
        for model in self.models:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": max_tokens
            }
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    msg = data["choices"][0]["message"]
                    text = (msg.get("content") or msg.get("reasoning") or "").strip()
                    parsed = json.loads(text)
                    if parsed:
                        print(f"[API POOL] [OK] Cerebras ({model}) returned action: '{parsed.get('action')}'")
                        return parsed
            except Exception as e:
                print(f"[API POOL] [!WARN] Cerebras error on {model}: {e}")
                continue

        return None


# ==============================================================================
# 5. MASTER UNIVERSAL MULTI-PROVIDER POOL
# ==============================================================================
class MultiKeyAPIPool:
    def __init__(self):
        self.keys: List[GroqKeyStatus] = []
        self.current_idx = 0
        self._load_groq_keys()
        self.gemini = GeminiProvider()
        self.cerebras = CerebrasProvider()

    def _load_groq_keys(self):
        discovered_keys = []
        env_keys_list = os.getenv("GROQ_API_KEYS", "")
        if env_keys_list:
            for k in re.split(r"[,;\n]+", env_keys_list):
                k_clean = k.strip().strip("'\"")
                if k_clean and k_clean not in discovered_keys:
                    discovered_keys.append(k_clean)

        for i in range(1, 20):
            k = os.getenv(f"GROQ_API_KEY_{i}") or os.getenv(f"GROQ_KEY_{i}")
            if k:
                k_clean = k.strip().strip("'\"")
                if k_clean and k_clean not in discovered_keys:
                    discovered_keys.append(k_clean)

        single_key = os.getenv("GROQ_API_KEY", "")
        if single_key:
            k_clean = single_key.strip().strip("'\"")
            if k_clean and k_clean not in discovered_keys:
                discovered_keys.append(k_clean)

        self.keys = [GroqKeyStatus(k, idx + 1) for idx, k in enumerate(discovered_keys)]
        print(f"[API POOL] Initialized pool with {len(self.keys)} Groq key(s).")

    def add_key(self, raw_key: str) -> bool:
        cleaned = raw_key.strip().strip("'\"")
        if not cleaned:
            return False
        if cleaned.startswith("gsk_"):
            if not any(k.key == cleaned for k in self.keys):
                new_obj = GroqKeyStatus(cleaned, len(self.keys) + 1)
                self.keys.append(new_obj)
                print(f"[API POOL] Added Groq key #{new_obj.index}")
                return True
        elif cleaned.startswith("csk-"):
            self.cerebras.api_key = cleaned
            print("[API POOL] Set Cerebras key.")
            return True
        else:
            if cleaned not in self.gemini.keys:
                self.gemini.keys.append(cleaned)
                print("[API POOL] Added Google Gemini key.")
                return True
        return False

    def get_healthy_groq_key(self) -> Optional[GroqKeyStatus]:
        if not self.keys:
            return None
        total = len(self.keys)
        for step in range(total):
            idx = (self.current_idx + step) % total
            candidate = self.keys[idx]
            if candidate.is_available():
                self.current_idx = (idx + 1) % total
                return candidate
        return None

    def execute_chat_completion(
        self,
        messages: List[Dict[str, str]],
        models: Optional[List[str]] = None,
        temperature: float = 0.1,
        max_tokens: int = 350,
        response_format: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Universal fallback cascade:
          1. Groq Multi-Key Pool (Ultra-fast LPU)
          2. Google Gemini 2.5 Flash (1M TPM / 1500 RPD Free)
          4. Cerebras Cloud (1M Tokens/Day Free)
          5. Local Zero-Token Autonomous Engine (return None)
        """
        if models is None:
            models = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"]

        # Ensure the prompt contains the word 'json' for strict API requirements
        has_json_word = any("json" in m.get("content", "").lower() for m in messages)
        if not has_json_word:
            messages = [{"role": "system", "content": "Return valid json."}] + messages

        # --- LEVEL 1: GROQ MULTI-KEY POOL ---
        for key_idx in range(len(self.keys)):
            key_status = self.get_healthy_groq_key()
            if not key_status or not key_status.client:
                break

            client = key_status.client
            for model_name in models:
                try:
                    kwargs = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                    if response_format:
                        kwargs["response_format"] = response_format

                    res = client.chat.completions.create(**kwargs)
                    content = (res.choices[0].message.content or "{}").strip()
                    parsed = self._parse_json_result(content)
                    if parsed:
                        key_status.mark_success()
                        return parsed
                except RateLimitError as e:
                    err_text = str(e)
                    print(f"[API POOL] [!WARN] Groq Rate limit on Key #{key_status.index} ({model_name}): {err_text[:100]}")
                    # Try next available model for this key before quarantining the key
                    continue
                except APIError as e:
                    err_text = str(e)
                    if "401" in err_text or "invalid" in err_text.lower():
                        key_status.mark_invalid(err_text[:80])
                        break
                    if "400" in err_text or "json" in err_text.lower():
                        # Bad request or JSON mode format issue: retry without response_format constraint
                        try:
                            res = client.chat.completions.create(
                                model=model_name,
                                messages=messages,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                            content = (res.choices[0].message.content or "{}").strip()
                            parsed = self._parse_json_result(content)
                            if parsed:
                                key_status.mark_success()
                                return parsed
                        except Exception:
                            pass
                        continue
                    key_status.mark_rate_limit(cooldown_seconds=30.0, err_msg=err_text[:80])
                    break
                except Exception as e:
                    print(f"[API POOL] [!WARN] Groq unexpected error: {e}")
                    continue

        # --- LEVEL 2: GOOGLE GEMINI 2.5 FLASH ---
        print("[API POOL] [FAILOVER] Groq pool cooling down. Cascading to Google Gemini 2.5 Flash...")
        gemini_action = self.gemini.execute(messages, max_tokens=max_tokens)
        if gemini_action:
            return gemini_action

        # --- LEVEL 4: CEREBRAS CLOUD ---
        if self.cerebras.api_key:
            print("[API POOL] [FAILOVER] Cascading to Cerebras Cloud...")
            cerebras_action = self.cerebras.execute(messages, max_tokens=max_tokens)
            if cerebras_action:
                return cerebras_action

        # --- LEVEL 5: RETURN NONE FOR LOCAL AUTONOMOUS FALLBACK ---
        print("[API POOL] [!WARN] All external API tiers engaged. Yielding to Zero-Token Local Autonomous Engine.")
        return None

    def _parse_json_result(self, content: str) -> Optional[Dict[str, Any]]:
        clean_content = content
        if "```json" in clean_content:
            clean_content = clean_content.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_content:
            clean_content = clean_content.split("```")[1].split("```")[0].strip()
        try:
            parsed = json.loads(clean_content)
        except Exception:
            match = re.search(r'"action"\s*:\s*"([^"]+)"', clean_content)
            act = match.group(1) if match else "respond"
            parsed = {"action": act, "message": clean_content, "reason": "Model response."}
        if isinstance(parsed, list):
            parsed = parsed[0] if len(parsed) > 0 else None
        return parsed

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "groq_keys_total": len(self.keys),
            "groq_keys_healthy": sum(1 for k in self.keys if k.is_available()),
            "gemini_keys": len(self.gemini.keys),
            "gemini_active": len(self.gemini.keys) > 0 and time.time() >= self.gemini.cooldown_until,
            "cerebras_active": bool(self.cerebras.api_key)
        }


# Global singleton instance
api_pool = MultiKeyAPIPool()
