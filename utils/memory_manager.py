import streamlit as st

class MemoryManager:
    def __init__(self, llm_client, max_entries: int = 10):
        """
        Initialize the memory manager with an LLM client and maximum number of summaries to store.
        
        Args:
            llm_client: An LLM client instance with a chat() method
            max_entries: Maximum number of summaries to keep in memory (default: 10)
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
        Extract the most important factual information from this exchange in one sentence. Focus on concrete facts, definitions, or key information that would be useful to remember for future conversations.

        User: "{user_msg}"
        Assistant: "{assistant_reply}"

        Important fact:'''
        
        try:
            # Use the LLM client's chat method and extract just the reply
            summary_response = self.llm.chat(mem_prompt)
            
            # Handle the tuple response format (reply, rationale)
            if isinstance(summary_response, tuple):
                summary = summary_response[0].strip()
            else:
                summary = summary_response.strip()
            
            # Only store if summary is sufficiently informative (>5 words)
            if len(summary.split()) > 5:
                # Initialize memories in session state if not present
                if 'memories' not in st.session_state:
                    st.session_state.memories = []
                
                st.session_state.memories.append(summary)
                
                # Keep only the most recent max_entries summaries
                if len(st.session_state.memories) > self.max_entries:
                    st.session_state.memories.pop(0)
                    
        except Exception as e:
            # Silently fail if summarization fails - don't break the main conversation
            print(f"Memory summarization failed: {e}")

    def get_memory_context(self, n: int = 2) -> str:
        """
        Return the last `n` full user/assistant turns joined by newlines.
        Args:
            n: Number of most recent turns to return (default: 2)
        Returns:
            String containing the memory context with turns separated by newlines
        """
        conversation = st.session_state.get('conversation', [])
        context = []
        # Get the last n user/assistant pairs (so 2n turns)
        for turn in conversation[-2*n:]:
            role = turn['role'].capitalize()
            content = turn['content']
            context.append(f"{role}: {content}")
        return "\n".join(context)
    
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