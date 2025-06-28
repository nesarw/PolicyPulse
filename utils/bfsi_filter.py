BFSI_KEYWORDS = [
    "insurance", "policy", "premium", "claim", "coverage", "beneficiary", "sum insured",
    "proposer", "insured", "nominee", "renewal", "endorsement", "rider", "deductible",
    "agent", "broker", "underwriting", "settlement", "grace period", "maturity", "surrender",
    "ULIP", "term plan", "health", "life", "auto", "motor", "fire", "marine", "travel",
    "customer code", "policy number", "plan", "hospitalization", "network hospital", "cashless",
    "invoice", "receipt", "payment", "sum assured", "sum insured", "proposer name", "insured name",
    "customer name", "policyholder", "member name"
]

def is_bfsi_query(query: str) -> bool:
    """
    Returns True if the query contains any BFSI-related keyword (case-insensitive, partial match).
    """
    query_lower = query.lower()
    return any(keyword.lower() in query_lower for keyword in BFSI_KEYWORDS) 