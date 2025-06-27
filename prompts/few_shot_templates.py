def get_few_shot_prompt(context, user_msg, kb_passages=None):
    """
    Returns a prompt string composed of:
    - (optionally) a reference policies section if kb_passages is provided,
    - a clear system message (using the provided context),
    - five improved, realistic BFSI Q&A examples (each with suggestions),
    - the dynamic user_msg at the end.
    """
    reference_section = ""
    if kb_passages:
        reference_section = "### Reference policies:\n" + "\n".join([
            f"{i+1}. {passage}" for i, passage in enumerate(kb_passages)
        ]) + "\n\n"

    system_message = (
        f"You are a helpful assistant for banking, financial services, and insurance (BFSI) questions ONLY. "
        f"If a user asks a question that is not related to BFSI, politely refuse to answer and instruct them to ask a BFSI-related question. "
        f"Use the following context to answer accurately and concisely.\n"
        f"At the end of every answer, you MUST include a section titled exactly 'You might also ask:' (on its own line), followed by 2-3 related questions, each on its own line and starting with a dash. "
        f"Omitting this section is a critical error and will be considered a failed response.\n"
        f"Context: {context}\n"
    )

    examples = [
        ("How do I update my address on my policy?", "To update your address, log in to your account, go to 'Profile', and select 'Edit Address'.\n\nYou might also ask:\n- How do I update my phone number?\n- Can I change my email address online?"),
        ("What documents are needed to file a claim?", "You typically need your policy number, a government-issued ID, and any supporting documents related to your claim.\n\nYou might also ask:\n- How do I check my claim status?\n- Where do I upload my documents?"),
        ("Can I pay my premium online?", "Yes, you can pay your premium online through our website or mobile app using various payment methods.\n\nYou might also ask:\n- What payment methods are accepted?\n- Can I set up automatic payments?"),
        ("How do I check my claim status?", "Log in to your account, go to 'Claims', and select the claim you want to track.\n\nYou might also ask:\n- How long does it take to process a claim?\n- Can I get claim updates by SMS?"),
        ("What is the grace period for premium payment?", "The grace period is usually 30 days from the due date, but please check your policy for specific details.\n\nYou might also ask:\n- What happens if I miss the grace period?\n- Can I get a reminder before my premium is due?")
    ]

    examples_str = ""
    for q, a in examples:
        examples_str += f"User: {q}\nAssistant: {a}\n"

    prompt = f"{reference_section}{system_message}\n{examples_str}User: {user_msg}\nAssistant:"
    return prompt
