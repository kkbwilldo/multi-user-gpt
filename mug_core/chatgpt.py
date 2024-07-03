import os
import openai

def set_openai_api_key():
    """
    Prompts the user to input their OpenAI API key and sets it as an environment variable.
    If the user inputs 'q', the function exits without setting the API key.
    The API key is verified before being set.

    Returns:
        None
    """
    # Check if OPENAI_API_KEY is already set in environment variables
    existing_api_key = os.getenv("OPENAI_API_KEY")
    if existing_api_key:
        if verify_api_key(existing_api_key):
            use_existing = input("An OpenAI API key is already set in the environment variables. Would you like to use it? [y/n]: ").lower()
            if use_existing == 'y':
                print("Using existing OpenAI API Key from environment variable.")
                return
            else:
                print("Existing API Key will not be used. Please provide a new API Key.")
        else:
            print("The existing OpenAI API Key in the environment variables is invalid. Please provide a new API Key.")
    
    while True:
        api_key = input("Please enter your OpenAI API Key (or 'q' to quit): ")
        if api_key.lower() == 'q':
            print("Exiting without setting the API key.")
            return

        # Verify the API key
        if verify_api_key(api_key):
            os.environ["OPENAI_API_KEY"] = api_key
            print("The OpenAI API Key has been set as an environment variable.")
            break
        else:
            print("Invalid API Key. Please try again.")

def verify_api_key(api_key):
    """
    Verifies the provided OpenAI API key by attempting to list available models.

    Args:
        api_key (str): The OpenAI API key to verify.

    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    client = openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
        return True
    except openai.AuthenticationError:
        return False

def ask_chatgpt(question, context):
    """
    Sends a question to OpenAI's GPT model with provided context and returns the response.

    Args:
        question (str): The question to ask.
        context (str): The context to provide.

    Returns:
        str: The response from the GPT model.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        return "OpenAI API Key not found. Please configure it using 'mug start'."

    prompt = f"Context:\n{context}\n\nQuestion:\n{question}"
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

if __name__ == "__main__":
    set_openai_api_key()
