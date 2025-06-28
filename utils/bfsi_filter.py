BFSI_KEYWORDS = [
    "insurance", "policy", "premium", "claim", "coverage", "beneficiary", "sum insured",
    "proposer", "insured", "nominee", "renewal", "endorsement", "rider", "deductible",
    "agent", "broker", "underwriting", "settlement", "grace period", "maturity", "surrender",
    "ULIP", "term plan", "health", "life", "auto", "motor", "fire", "marine", "travel",
    "customer code", "policy number", "plan", "hospitalization", "network hospital", "cashless",
    "invoice", "receipt", "payment", "sum assured", "sum insured", "proposer name", "insured name",
    "customer name", "policyholder", "member name"
]

# Blocklist of unsafe words/phrases
UNSAFE_WORDS = [
    "kill", "suicide", "hack", "bomb", "terrorist", "attack", "murder", "assassinate",
    "explosive", "weapon", "gun", "shoot", "bombing", "terrorism", "violence", "harm",
    "hurt", "injury", "death", "die", "dead", "poison", "drug", "illegal", "crime",
    "criminal", "fraud", "scam", "phishing", "malware", "virus", "spam", "hate",
    "discrimination", "racist", "sexist", "abuse", "harassment", "threat", "blackmail",
    "extortion", "bribe", "corruption", "money laundering", "terrorist financing"
]

def is_bfsi_query(query: str) -> bool:
    """
    Returns True if the query contains any BFSI-related keyword (case-insensitive, partial match).
    """
    query_lower = query.lower()
    return any(keyword.lower() in query_lower for keyword in BFSI_KEYWORDS)

def safety_check(user_input: str, response_text: str) -> dict:
    """
    Performs safety checks on both user input and LLM response.
    
    Args:
        user_input: The user's input message
        response_text: The LLM's response text
        
    Returns:
        dict with keys:
        - unsafe: bool - True if unsafe content detected
        - reason: str - Reason for flagging (if unsafe)
        - bfsi_relevance: bool - True if content is BFSI-relevant
        - bfsi_score: int - Number of BFSI keywords found
    """
    result = {
        "unsafe": False,
        "reason": "",
        "bfsi_relevance": False,
        "bfsi_score": 0
    }
    
    # Convert to lowercase for checking
    input_lower = user_input.lower()
    response_lower = response_text.lower()
    combined_text = f"{input_lower} {response_lower}"
    
    # Check for unsafe words in both input and response
    for unsafe_word in UNSAFE_WORDS:
        if unsafe_word in input_lower or unsafe_word in response_lower:
            result["unsafe"] = True
            result["reason"] = f"Unsafe content detected: '{unsafe_word}'"
            break
    
    # Count BFSI keywords in combined text
    bfsi_count = 0
    for keyword in BFSI_KEYWORDS:
        if keyword.lower() in combined_text:
            bfsi_count += 1
    
    result["bfsi_score"] = bfsi_count
    result["bfsi_relevance"] = bfsi_count >= 2  # Require at least 2 BFSI keywords for relevance
    
    # Additional safety checks
    if not result["unsafe"]:
        # Check for potential harmful patterns
        harmful_patterns = [
            "how to hack", "how to kill", "how to commit suicide",
            "how to make bomb", "how to attack", "how to harm",
            "instructions for", "tutorial on", "guide to"
        ]
        
        for pattern in harmful_patterns:
            if pattern in combined_text:
                result["unsafe"] = True
                result["reason"] = f"Potentially harmful instruction pattern detected: '{pattern}'"
                break
    
    return result 