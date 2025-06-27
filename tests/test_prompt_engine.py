import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from prompts.few_shot_templates import get_few_shot_prompt

def test_get_few_shot_prompt_contains_examples_and_user_msg():
    context = "Banking context."
    user_msg = "What is a fixed deposit?"
    prompt = get_few_shot_prompt(context, user_msg)

    example_questions = [
        "What is KYC in banking?",
        "How does a credit score affect loan eligibility?",
        "What is the difference between NEFT and RTGS?",
        "What is an insurance premium?",
        "What does 'mutual fund SIP' mean?"
    ]

    for question in example_questions:
        assert question in prompt

    # The prompt should end with the user message
    assert prompt.strip().endswith(f"User: {user_msg}\nAssistant:")
