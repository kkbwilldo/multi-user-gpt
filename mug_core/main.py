import sys
from .api import set_api_keys, load_session_log
from .chatgpt import ask_chatgpt

def main():
    """
    Main function to handle different commands: start, end, and questions.

    Returns:
        None
    """
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            set_api_keys()
        elif sys.argv[1] == "end":
            print("Ending session.")
        else:
            question = " ".join(sys.argv[1:])
            context = load_session_log()
            response = ask_chatgpt(question, context)
            print(f"ChatGPT response: {response}")

if __name__ == "__main__":
    main()
