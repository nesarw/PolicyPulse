BFSI_KEYWORDS = [
    'insurance', 'policy', 'premium', 'claim', 'coverage', 'beneficiary', 'deductible',
    'health insurance', 'life insurance', 'auto insurance', 'home insurance',
    'bank', 'banking', 'loan', 'credit', 'debit', 'account', 'mortgage', 'investment',
    'mutual fund', 'fixed deposit', 'savings', 'interest rate', 'financial', 'finance',
    'payment', 'renewal', 'grace period', 'customer service', 'policyholder', 'risk',
    'underwriting', 'actuary', 'BFSI', 'insurance company', 'policy number', 'claim status',
    'premium payment', 'policy renewal', 'insurance plan', 'coverage amount', 'sum assured',
    'network hospital', 'cashless', 'enrollment', 'dependent', 'benefit', 'rider', 'endorsement',
    'third party', 'TPA', 'agent', 'broker', 'commission', 'regulation', 'IRDA', 'settlement',
    'disbursement', 'nominee', 'surrender', 'maturity', 'annuity', 'pension', 'grievance',
    'dispute', 'ombudsman', 'claim form', 'policy document', 'premium receipt', 'statement',
    'transaction', 'EMI', 'credit card', 'debit card', 'KYC', 'compliance', 'fraud', 'scam',
    'cyber insurance', 'travel insurance', 'marine insurance', 'fire insurance', 'property insurance',
    'vehicle insurance', 'two wheeler', 'four wheeler', 'personal accident', 'group insurance',
    'term plan', 'ULIP', 'endowment', 'money back', 'child plan', 'retirement plan', 'tax', 'GST',
    'income tax', 'tax benefit', 'section 80C', 'section 10(10D)', 'policy lapse', 'revival',
    'bonus', 'participating', 'non-participating', 'guaranteed', 'non-guaranteed', 'sum insured',
    'policy schedule', 'proposal form', 'medical test', 'pre-existing', 'waiting period', 'exclusion',
    'inclusion', 'hospitalization', 'network', 'cashless', 'reimbursement', 'claim intimation',
    'settlement ratio', 'persistency', 'solvency', 'asset', 'liability', 'portfolio', 'fund value',
    'NAV', 'switch', 'top-up', 'partial withdrawal', 'surrender value', 'free look', 'cooling off',
    'policy servicing', 'customer care', 'helpline', 'support', 'complaint', 'feedback', 'suggestion'
]

def is_bfsi_query(user_input: str) -> bool:
    """
    Returns True if the user_input contains BFSI-related keywords, False otherwise.
    """
    user_input_lower = user_input.lower()
    return any(keyword in user_input_lower for keyword in BFSI_KEYWORDS) 