import os
import requests

class LLMClient:
    def __init__(self, api_key=None, model="HuggingFaceH4/zephyr-7b-beta"):
        self.api_key = api_key or os.getenv('HF_API_KEY')
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def chat(self, prompt):
        """
        Sends the prompt to the LLM and returns a tuple (reply, rationale),
        where rationale is a one-sentence summary of why the answer was given.
        """
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 256, "return_full_text": False}
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code == 404:
            return "Model not found or is not available for Inference API. Please check your model name or use a supported public model.", None
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[-1]:
            reply = result[-1]["generated_text"].strip()
        elif isinstance(result, dict) and "generated_text" in result:
            reply = result["generated_text"].strip()
        else:
            reply = str(result)

        rationale_prompt = f'''
You are PolicyPulse. Given the context and the answer:
"""{reply}"""
Summarize in one sentence why you gave that answer, referencing the facts or KB snippets you used.
'''
        payload_rationale = {
            "inputs": rationale_prompt,
            "parameters": {"max_new_tokens": 64, "return_full_text": False}
        }
        response_rationale = requests.post(self.api_url, headers=self.headers, json=payload_rationale)
        if response_rationale.status_code == 404:
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