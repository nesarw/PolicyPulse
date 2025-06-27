def get_few_shot_prompt(context, user_msg):
    """
    Returns a prompt string composed of:
    - a clear system message (using the provided context),
    - five improved, realistic BFSI Q&A examples,
    - the dynamic user_msg at the end.
    """
    system_message = (
        f"You are a helpful assistant for insurance and policy questions. "
        f"Use the following context to answer accurately and concisely.\nContext: {context}\n"
    )

    examples = [
        ("How do I update my address on my policy?", "To update your address, log in to your account, go to 'Profile', and select 'Edit Address'."),
        ("What documents are needed to file a claim?", "You typically need your policy number, a government-issued ID, and any supporting documents related to your claim."),
        ("Can I pay my premium online?", "Yes, you can pay your premium online through our website or mobile app using various payment methods."),
        ("How do I check my claim status?", "Log in to your account, go to 'Claims', and select the claim you want to track."),
        ("What is the grace period for premium payment?", "The grace period is usually 30 days from the due date, but please check your policy for specific details."),
    ]

    examples_str = ""
    for q, a in examples:
        examples_str += f"User: {q}\nAssistant: {a}\n"

    prompt = f"{system_message}\n{examples_str}User: {user_msg}\nAssistant:"
    return prompt
