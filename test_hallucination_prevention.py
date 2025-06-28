#!/usr/bin/env python3
"""
Advanced test script to verify hallucination prevention with actual LLM calls
"""

import os
import sys
from dotenv import load_dotenv
from utils.llm_client import LLMClient
from utils.memory_manager import MemoryManager

# Load environment variables
load_dotenv()

def test_without_memory():
    """Test LLM responses without memory context"""
    print("🧪 Testing WITHOUT Memory Context")
    print("=" * 50)
    
    llm = LLMClient(api_key=os.getenv('HF_API_KEY'))
    
    # Test 1: Ask for specific policy details without context
    prompt1 = """
You are a helpful assistant for BFSI questions. Answer the following question:

User: What is my policy number?
Assistant:"""
    
    print("\n📝 Test 1: Policy Number Query (No Memory)")
    print("-" * 40)
    print("Prompt:", prompt1.strip())
    
    try:
        response1, _ = llm.chat(prompt1)
        print("Response:", response1)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Ask for coverage details without context
    prompt2 = """
You are a helpful assistant for BFSI questions. Answer the following question:

User: What is my coverage amount?
Assistant:"""
    
    print("\n📝 Test 2: Coverage Amount Query (No Memory)")
    print("-" * 40)
    print("Prompt:", prompt2.strip())
    
    try:
        response2, _ = llm.chat(prompt2)
        print("Response:", response2)
    except Exception as e:
        print(f"Error: {e}")

def test_with_memory():
    """Test LLM responses with memory context"""
    print("\n🧪 Testing WITH Memory Context")
    print("=" * 50)
    
    llm = LLMClient(api_key=os.getenv('HF_API_KEY'))
    memory_manager = MemoryManager(llm)
    
    # Establish some facts in memory
    print("\n📝 Establishing Facts in Memory")
    print("-" * 40)
    
    # Add specific policy information
    memory_manager.add_turn(
        "What is my policy number?",
        "Based on your policy document, your policy number is 123456789."
    )
    
    memory_manager.add_turn(
        "What is my coverage amount?",
        "Your health insurance policy provides coverage up to $500,000."
    )
    
    memory_manager.add_turn(
        "What is my premium amount?",
        "Your monthly premium is $150 for the health insurance policy."
    )
    
    print(f"Memory count: {memory_manager.get_memory_count()}")
    print(f"Memory context: {memory_manager.get_memory_context()}")
    
    # Test 1: Ask for policy number with memory context
    memory_ctx = memory_manager.get_memory_context()
    prompt1 = f"""
### Conversation Memory:
{memory_ctx}

You are a helpful assistant for BFSI questions. Answer the following question:

User: What is my policy number?
Assistant:"""
    
    print("\n📝 Test 1: Policy Number Query (With Memory)")
    print("-" * 40)
    print("Prompt:", prompt1.strip())
    
    try:
        response1, _ = llm.chat(prompt1)
        print("Response:", response1)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Ask for coverage amount with memory context
    prompt2 = f"""
### Conversation Memory:
{memory_ctx}

You are a helpful assistant for BFSI questions. Answer the following question:

User: What is my coverage amount?
Assistant:"""
    
    print("\n📝 Test 2: Coverage Amount Query (With Memory)")
    print("-" * 40)
    print("Prompt:", prompt2.strip())
    
    try:
        response2, _ = llm.chat(prompt2)
        print("Response:", response2)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Ask for premium amount with memory context
    prompt3 = f"""
### Conversation Memory:
{memory_ctx}

You are a helpful assistant for BFSI questions. Answer the following question:

User: What is my premium amount?
Assistant:"""
    
    print("\n📝 Test 3: Premium Amount Query (With Memory)")
    print("-" * 40)
    print("Prompt:", prompt3.strip())
    
    try:
        response3, _ = llm.chat(prompt3)
        print("Response:", response3)
    except Exception as e:
        print(f"Error: {e}")

def test_contradiction_detection():
    """Test if the system can detect and handle contradictions"""
    print("\n🧪 Testing Contradiction Detection")
    print("=" * 50)
    
    llm = LLMClient(api_key=os.getenv('HF_API_KEY'))
    memory_manager = MemoryManager(llm)
    
    # Establish initial fact
    memory_manager.add_turn(
        "What is my policy number?",
        "Your policy number is 123456789."
    )
    
    # Try to contradict the established fact
    memory_ctx = memory_manager.get_memory_context()
    contradiction_prompt = f"""
### Conversation Memory:
{memory_ctx}

You are a helpful assistant for BFSI questions. The user says: "My policy number is 987654321."

User: Is my policy number 987654321?
Assistant:"""
    
    print("\n📝 Contradiction Detection Test")
    print("-" * 40)
    print("Prompt:", contradiction_prompt.strip())
    
    try:
        response, _ = llm.chat(contradiction_prompt)
        print("Response:", response)
    except Exception as e:
        print(f"Error: {e}")

def test_memory_persistence():
    """Test memory persistence across multiple calls"""
    print("\n🧪 Testing Memory Persistence")
    print("=" * 50)
    
    llm = LLMClient(api_key=os.getenv('HF_API_KEY'))
    memory_manager = MemoryManager(llm)
    
    # Add multiple facts
    facts = [
        ("What is my name?", "Your name is John Doe."),
        ("What is my policy type?", "You have a health insurance policy."),
        ("What is my deductible?", "Your deductible is $1,000."),
        ("What is my copay?", "Your copay is $25 for doctor visits."),
        ("What is my network?", "You are in the Blue Cross Blue Shield network.")
    ]
    
    for question, answer in facts:
        memory_manager.add_turn(question, answer)
    
    print(f"Total facts stored: {memory_manager.get_memory_count()}")
    print(f"Memory context: {memory_manager.get_memory_context()}")
    
    # Test retrieval of specific information
    memory_ctx = memory_manager.get_memory_context()
    retrieval_prompt = f"""
### Conversation Memory:
{memory_ctx}

You are a helpful assistant for BFSI questions. Answer the following question:

User: What are my policy details?
Assistant:"""
    
    print("\n📝 Memory Retrieval Test")
    print("-" * 40)
    print("Prompt:", retrieval_prompt.strip())
    
    try:
        response, _ = llm.chat(retrieval_prompt)
        print("Response:", response)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🧪 PolicyPulse Memory Manager & Hallucination Prevention Tests")
    print("=" * 70)
    
    # Run all tests
    test_without_memory()
    test_with_memory()
    test_contradiction_detection()
    test_memory_persistence()
    
    print("\n✅ All tests completed!")
    print("\n📊 Analysis:")
    print("- Compare responses with and without memory context")
    print("- Check if memory context improves accuracy and consistency")
    print("- Verify that the system doesn't hallucinate specific details")
    print("- Ensure memory persistence across multiple interactions") 