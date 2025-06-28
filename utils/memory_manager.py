import streamlit as st

class MemoryManager:
    def __init__(self, llm_client, max_entries: int = 15):
        """
        Initialize the memory manager with an LLM client and maximum number of summaries to store.
        
        Args:
            llm_client: An LLM client instance with a chat() method
            max_entries: Maximum number of summaries to keep in memory (default: 15)
        """
        self.llm = llm_client
        self.max_entries = max_entries

    def add_turn(self, user_msg: str, assistant_reply: str):
        """
        Summarize the key fact(s) from this exchange in 1-2 sentences.
        Only store the summary if it is sufficiently informative (>5 words).
        Keep at most `max_entries` summaries, dropping the oldest.
        
        Args:
            user_msg: The user's message
            assistant_reply: The assistant's reply
        """
        mem_prompt = f'''
        Extract the most important factual information from this exchange. Write ONLY the key facts in 1-2 clear sentences. Do not mention the summarization process or use phrases like "Here is the most important information" or "The user's policy number is".

        Focus on:
        - Specific facts, numbers, or details mentioned
        - Key definitions or explanations provided
        - Important policy information or requirements
        - Any specific user details or preferences mentioned
        
        If the exchange contains no concrete facts or is just general conversation, write "No specific facts to remember."

        User: "{user_msg}"
        Assistant: "{assistant_reply}"

        Key facts:'''
        
        try:
            # Use the LLM client's chat method and extract just the reply
            summary_response = self.llm.chat(mem_prompt)
            
            # Handle the tuple response format (reply, rationale)
            if isinstance(summary_response, tuple):
                summary = summary_response[0].strip()
            else:
                summary = summary_response.strip()
            
            # Debug output
            print(f"Memory summarization - User: '{user_msg}' | Assistant: '{assistant_reply}' | Summary: '{summary}'")
            
            # Only store if summary is sufficiently informative (>3 words and not the default message)
            if len(summary.split()) > 3 and summary != "No specific facts to remember.":
                # Initialize memories in session state if not present
                if 'memories' not in st.session_state:
                    st.session_state.memories = []
                
                st.session_state.memories.append(summary)
                print(f"Memory stored. Total memories: {len(st.session_state.memories)}")
                
                # Keep only the most recent max_entries summaries
                if len(st.session_state.memories) > self.max_entries:
                    st.session_state.memories.pop(0)
            else:
                print(f"Memory not stored - too short or no facts: '{summary}'")
                    
        except Exception as e:
            # Silently fail if summarization fails - don't break the main conversation
            print(f"Memory summarization failed: {e}")

    def get_memory_context(self, n: int = 5) -> str:
        """
        Return the last `n` stored memory summaries joined by newlines.
        Args:
            n: Number of most recent summaries to return (default: 5)
        Returns:
            String containing the memory context with summaries separated by newlines
        """
        if 'memories' not in st.session_state:
            print("No memories in session state")
            return ""
        
        memories = st.session_state.memories
        print(f"Total memories available: {len(memories)}")
        
        # Get the last n summaries
        recent_memories = memories[-n:] if len(memories) >= n else memories
        
        if not recent_memories:
            print("No recent memories to return")
            return ""
        
        # Format each memory as a numbered summary
        context_lines = []
        for i, memory in enumerate(recent_memories, 1):
            context_lines.append(f"{i}. {memory}")
        
        context = "\n".join(context_lines)
        print(f"Memory context being returned: {context}")
        return context
    
    def clear_memory(self):
        """Clear all stored summaries."""
        if 'memories' in st.session_state:
            st.session_state.memories.clear()
    
    def get_memory_count(self) -> int:
        """Get the current number of stored summaries."""
        if 'memories' not in st.session_state:
            return 0
        return len(st.session_state.memories)
    
    def get_all_summaries(self) -> list[str]:
        """Get all stored summaries as a list."""
        if 'memories' not in st.session_state:
            return []
        return st.session_state.memories.copy() 