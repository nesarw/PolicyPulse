#!/usr/bin/env python3
"""
Test script to verify PolicyPulse's memory manager functionality
"""

import os
import sys
from dotenv import load_dotenv
from utils.llm_client import LLMClient
from utils.memory_manager import MemoryManager

# Load environment variables
load_dotenv()

def test_memory_manager():
    """Test the memory manager functionality"""
    print("🧪 Testing PolicyPulse Memory Manager")
    print("=" * 50)
    
    # Initialize LLM client and memory manager
    llm = LLMClient(api_key=os.getenv('HF_API_KEY'))
    memory_manager = MemoryManager(llm)
    
    # Test 1: Basic memory storage
    print("\n📝 Test 1: Basic Memory Storage")
    print("-" * 30)
    
    user_msg1 = "What is health insurance?"
    assistant_reply1 = "Health insurance is a type of insurance that covers medical expenses incurred due to illness, injury, or disease."
    
    print(f"User: {user_msg1}")
    print(f"Assistant: {assistant_reply1}")
    
    memory_manager.add_turn(user_msg1, assistant_reply1)
    
    print(f"Memory count: {memory_manager.get_memory_count()}")
    print(f"Memory context: {memory_manager.get_memory_context()}")
    
    # Test 2: Memory accumulation
    print("\n📝 Test 2: Memory Accumulation")
    print("-" * 30)
    
    user_msg2 = "What is life insurance?"
    assistant_reply2 = "Life insurance provides financial protection to beneficiaries upon the death of the insured person."
    
    print(f"User: {user_msg2}")
    print(f"Assistant: {assistant_reply2}")
    
    memory_manager.add_turn(user_msg2, assistant_reply2)
    
    print(f"Memory count: {memory_manager.get_memory_count()}")
    print(f"Memory context: {memory_manager.get_memory_context()}")
    
    # Test 3: Context injection simulation
    print("\n📝 Test 3: Context Injection Simulation")
    print("-" * 30)
    
    # Simulate what the prompt would look like with memory context
    base_prompt = "You are a helpful assistant. Answer the following question: What is the difference between health and life insurance?"
    memory_ctx = memory_manager.get_memory_context()
    
    if memory_ctx:
        full_prompt = f"### Conversation Memory:\n{memory_ctx}\n\n{base_prompt}"
        print("Full prompt with memory context:")
        print(full_prompt)
    else:
        print("No memory context available")
    
    # Test 4: Hallucination prevention test
    print("\n📝 Test 4: Hallucination Prevention Test")
    print("-" * 30)
    
    # Test with contradictory information
    user_msg3 = "What is the premium amount for my health insurance?"
    assistant_reply3 = "I don't have access to your specific policy details. You would need to check your policy document or contact customer service."
    
    memory_manager.add_turn(user_msg3, assistant_reply3)
    
    print(f"User: {user_msg3}")
    print(f"Assistant: {assistant_reply3}")
    print(f"Updated memory context: {memory_manager.get_memory_context()}")
    
    # Test 5: Memory overflow test
    print("\n📝 Test 5: Memory Overflow Test")
    print("-" * 30)
    
    # Add more entries to test the max_entries limit
    for i in range(8):  # Add 8 more entries to test overflow
        user_msg = f"Test question {i+4}"
        assistant_reply = f"Test answer {i+4}"
        memory_manager.add_turn(user_msg, assistant_reply)
    
    print(f"Final memory count: {memory_manager.get_memory_count()}")
    print(f"All summaries: {memory_manager.get_all_summaries()}")
    
    # Test 6: Memory clearing
    print("\n📝 Test 6: Memory Clearing")
    print("-" * 30)
    
    memory_manager.clear_memory()
    print(f"Memory count after clearing: {memory_manager.get_memory_count()}")
    print(f"Memory context after clearing: {memory_manager.get_memory_context()}")

def test_hallucination_prevention():
    """Test specific hallucination prevention scenarios"""
    print("\n🛡️ Testing Hallucination Prevention")
    print("=" * 50)
    
    llm = LLMClient(api_key=os.getenv('HF_API_KEY'))
    memory_manager = MemoryManager(llm)
    
    # Scenario 1: Contradictory information
    print("\n📝 Scenario 1: Contradictory Information")
    print("-" * 30)
    
    # First, establish a fact
    memory_manager.add_turn(
        "What is my policy number?",
        "Based on your policy document, your policy number is 123456789."
    )
    
    # Then ask a follow-up that might cause hallucination
    follow_up_prompt = f"""
### Conversation Memory:
{memory_manager.get_memory_context()}

You are a helpful assistant. The user asks: "What is my policy number again?"
"""
    
    print("Follow-up prompt with memory context:")
    print(follow_up_prompt)
    
    # Scenario 2: Context consistency
    print("\n📝 Scenario 2: Context Consistency")
    print("-" * 30)
    
    memory_manager.add_turn(
        "What is the coverage amount?",
        "Your policy provides coverage up to $500,000 for health insurance."
    )
    
    consistency_prompt = f"""
### Conversation Memory:
{memory_manager.get_memory_context()}

You are a helpful assistant. The user asks: "Can you remind me of my policy details?"
"""
    
    print("Consistency prompt with memory context:")
    print(consistency_prompt)

if __name__ == "__main__":
    test_memory_manager()
    test_hallucination_prevention()
    print("\n✅ Memory manager testing completed!") 