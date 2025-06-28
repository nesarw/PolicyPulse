#!/usr/bin/env python3
"""
Quick test to verify hallucination prevention
"""

import os
from dotenv import load_dotenv
from utils.llm_client import LLMClient
from utils.memory_manager import MemoryManager

load_dotenv()

def quick_hallucination_test():
    """Quick test to verify the system doesn't hallucinate specific details"""
    
    print("🧪 Quick Hallucination Prevention Test")
    print("=" * 50)
    
    llm = LLMClient(api_key=os.getenv('HF_API_KEY'))
    memory_manager = MemoryManager(llm)
    
    # Test 1: Without memory - should not hallucinate specific details
    print("\n📝 Test 1: Without Memory Context")
    print("-" * 40)
    
    prompt1 = """
You are a helpful assistant for BFSI questions. Answer the following question:

User: What is my policy number?
Assistant:"""
    
    try:
        response1, _ = llm.chat(prompt1)
        print("Response:", response1)
        print("✅ Expected: Should say it doesn't have access to specific policy details")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: With memory context - should maintain consistency
    print("\n📝 Test 2: With Memory Context")
    print("-" * 40)
    
    # Add a specific fact to memory
    memory_manager.add_turn(
        "What is my policy number?",
        "Based on your policy document, your policy number is 123456789."
    )
    
    memory_ctx = memory_manager.get_memory_context()
    prompt2 = f"""
### Conversation Memory:
{memory_ctx}

You are a helpful assistant for BFSI questions. Answer the following question:

User: What is my policy number?
Assistant:"""
    
    try:
        response2, _ = llm.chat(prompt2)
        print("Response:", response2)
        print("✅ Expected: Should reference the stored policy number 123456789")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Contradiction test
    print("\n📝 Test 3: Contradiction Detection")
    print("-" * 40)
    
    contradiction_prompt = f"""
### Conversation Memory:
{memory_ctx}

You are a helpful assistant for BFSI questions. The user says: "My policy number is 987654321."

User: Is my policy number 987654321?
Assistant:"""
    
    try:
        response3, _ = llm.chat(contradiction_prompt)
        print("Response:", response3)
        print("✅ Expected: Should detect the contradiction with stored memory")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n🎯 Analysis:")
    print("- Test 1: Without memory, system should not make up specific details")
    print("- Test 2: With memory, system should reference stored facts")
    print("- Test 3: System should detect contradictions with established facts")

if __name__ == "__main__":
    quick_hallucination_test() 