import os
import requests
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
load_dotenv()

# Lazy import to avoid hard dependency if Gemini isn't used
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None

class LLMClient:
    def __init__(self, api_key=None, model="HuggingFaceH4/zephyr-7b-beta"):
        # HF token for fallback
        self.api_key = api_key or self._resolve_hf_token()
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

        # Gemini primary config
        self.gemini_api_key = self._resolve_gemini_token()
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    def _resolve_hf_token(self):
        """Resolve Hugging Face token from multiple possible sources."""
        candidate_env_vars = [
            "HF_API_KEY",
            "HUGGINGFACEHUB_API_TOKEN",
            "HUGGING_FACE_HUB_TOKEN",
            "HF_TOKEN",
        ]
        for name in candidate_env_vars:
            token = os.getenv(name)
            if token:
                return token
        try:
            import streamlit as st  # local import to avoid hard dependency at import time
            for name in [
                "HF_API_KEY",
                "HUGGINGFACEHUB_API_TOKEN",
                "HUGGING_FACE_HUB_TOKEN",
                "HF_TOKEN",
            ]:
                if name in st.secrets and st.secrets[name]:
                    return st.secrets[name]
        except Exception:
            pass
        return None

    def _resolve_gemini_token(self):
        """Resolve Gemini token from environment or Streamlit secrets."""
        token = os.getenv("GEMINI_API_KEY")
        if token:
            return token
        try:
            import streamlit as st  # local import
            if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
                return st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
        return None

    def _gemini_generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2):
        """Generate content with Gemini. Returns text or raises Exception."""
        if genai is None:
            raise RuntimeError("google-generativeai is not installed. Add 'google-generativeai' to requirements.")
        if not self.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY not set.")
        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel(self.gemini_model)
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        # Some SDK versions return .text; ensure we get a string
        text = getattr(response, "text", None)
        if not text:
            # attempt to extract from candidates
            try:
                candidates = getattr(response, "candidates", [])
                if candidates and getattr(candidates[0], "content", None):
                    parts = getattr(candidates[0].content, "parts", [])
                    if parts:
                        text = "".join(getattr(p, "text", "") for p in parts)
            except Exception:
                pass
        if not text:
            text = str(response)
        return text.strip()

    def chat(self, prompt, kb_passages=None):
        """
        Try Gemini first. If it fails, fallback to HuggingFace Zephyr.
        Returns a tuple (reply, rationale).
        """
        # 1) Try Gemini primary
        try:
            if self.gemini_api_key:
                reply = self._gemini_generate(prompt, max_tokens=512, temperature=0.2)
                # Rationale with Gemini if we have KB snippets
                limited_references = (kb_passages or [])[:2]
                references = "\n".join(limited_references).strip() if limited_references else ""
                if not references or references == "N/A":
                    rationale = "No relevant facts or KB snippets were found for this answer."
                else:
                    rationale_prompt = f"""
You are PolicyPulse. Given the following answer and ONLY the reference facts or KB snippets below, explain in one sentence which snippet(s) were most important in producing this answer. Do not mention anything not in the references.

Answer: {reply}
References:
{references}
"""
                    try:
                        rationale = self._gemini_generate(rationale_prompt, max_tokens=96, temperature=0.1)
                    except Exception:
                        # Non-fatal; provide no rationale if secondary call fails
                        rationale = None
                return reply, rationale
        except Exception as e:
            print(f"[Gemini] Error: {e}. Falling back to HuggingFace Zephyr.")

        # 2) Fallback to HuggingFace Zephyr
        if not self.api_key:
            friendly = (
                "Hugging Face API token is missing. Set one of: HF_API_KEY, HUGGINGFACEHUB_API_TOKEN, "
                "HUGGING_FACE_HUB_TOKEN or HF_TOKEN (in your environment, .env, or Streamlit secrets)."
            )
            return friendly, None

        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 256, "return_full_text": False}
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code == 404:
            return (
                "Model not found or is not available for Inference API. Please check your model name or use a supported public model.",
                None,
            )
        if response.status_code in (401, 403):
            return (
                "Unauthorized to call Hugging Face Inference API. Please verify your token has access and is set correctly (HF_API_KEY or HUGGINGFACEHUB_API_TOKEN).",
                None,
            )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[-1]:
            reply = result[-1]["generated_text"].strip()
        elif isinstance(result, dict) and "generated_text" in result:
            reply = result["generated_text"].strip()
        else:
            reply = str(result)

        # Rationale via Zephyr fallback as before
        limited_references = (kb_passages or [])[:2]
        references = "\n".join(limited_references).strip() if limited_references else ""
        if not references or references == "N/A":
            rationale = "No relevant facts or KB snippets were found for this answer."
            return reply, rationale

        rationale_prompt = f"""
You are PolicyPulse. Given the following answer and ONLY the reference facts or KB snippets below, explain in one sentence which snippet(s) were most important in producing this answer. Do not mention anything not in the references.

Answer: {reply}
References:
{references}
"""
        payload_rationale = {
            "inputs": rationale_prompt,
            "parameters": {"max_new_tokens": 64, "return_full_text": False}
        }
        response_rationale = requests.post(self.api_url, headers=self.headers, json=payload_rationale)
        if response_rationale.status_code == 404:
            return reply, None
        if response_rationale.status_code in (401, 403):
            return reply, None
        response_rationale.raise_for_status()
        result_rationale = response_rationale.json()
        if isinstance(result_rationale, list) and "generated_text" in result_rationale[-1]:
            rationale = result_rationale[-1]["generated_text"].strip()
        elif isinstance(result_rationale, dict) and "generated_text" in result_rationale:
            rationale = result_rationale["generated_text"].strip()
        else:
            rationale = str(result_rationale)
        return reply, rationale

    def stream_chat_response(self, prompt: str):
        """
        Stream tokens from HuggingFace InferenceClient as a generator.
        Falls back to regular chat if streaming fails.
        """
        try:
            # Use a more compatible model for streaming
            streaming_model = "gpt2"  # More compatible than zephyr-7b-beta
            client = InferenceClient(
                model=streaming_model,
                token=self.api_key
            )
            stream = client.text_generation(
                prompt,
                max_new_tokens=256,
                stream=True,
                return_full_text=False
            )
            for response in stream:
                if isinstance(response, dict) and 'token' in response:
                    yield response['token']
                else:
                    yield str(response)
        except Exception as e:
            print(f"Streaming failed: {e}. Falling back to regular chat.")
            reply, _ = self.chat(prompt)
            yield reply