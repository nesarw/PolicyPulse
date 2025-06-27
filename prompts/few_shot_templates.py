def get_few_shot_prompt(context, user_msg):
    """
    Returns a prompt string composed of:
    - a system message (using the provided context),
    - five hard-coded BFSI Q&A examples,
    - the dynamic user_msg at the end.
    """
    system_message = f"""You are a helpful assistant specialized in the Banking, Financial Services, and Insurance (BFSI) sector. Use the following context to answer questions accurately and concisely.\nContext: {context}\n"""

    examples = [
        ("What is KYC in banking?", "KYC stands for 'Know Your Customer.' It is a process used by banks to verify the identity of their clients and assess potential risks of illegal intentions for the business relationship."),
        ("How does a credit score affect loan eligibility?", "A credit score is a numerical representation of a person's creditworthiness. Higher scores increase the chances of loan approval and may result in better interest rates."),
        ("What is the difference between NEFT and RTGS?", "NEFT (National Electronic Funds Transfer) and RTGS (Real Time Gross Settlement) are electronic payment systems. NEFT settles transactions in batches, while RTGS settles them in real time and is typically used for larger amounts."),
        ("What is an insurance premium?", "An insurance premium is the amount paid by the policyholder to the insurance company for coverage. It is usually paid monthly, quarterly, or annually."),
        ("What does 'mutual fund SIP' mean?", "A Systematic Investment Plan (SIP) allows investors to invest a fixed amount regularly in a mutual fund scheme, helping to build wealth over time through disciplined investing.")
    ]

    examples_str = ""
    for q, a in examples:
        examples_str += f"User: {q}\nAssistant: {a}\n"

    prompt = f"{system_message}\n{examples_str}User: {user_msg}\nAssistant:"
    return prompt
