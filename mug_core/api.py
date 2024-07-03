import os
import json
from .chatgpt import set_openai_api_key, ask_chatgpt
from .aws_s3 import get_aws_credentials, aws_menu, LOG_DIR

CONFIG_PATH = os.path.join(LOG_DIR, "config.json")

def load_existing_config():
    """
    Loads the existing config file from ~/.mug/config.json if it exists.

    Returns:
        dict: The configuration dictionary if the file exists, otherwise None.
    """
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as config_file:
            config = json.load(config_file)
            return config
    return None

def use_existing_config(config):
    """
    Sets environment variables based on the provided configuration dictionary.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        None
    """
    for key, value in config.items():
        if value is not None:
            os.environ[key] = value

def save_config():
    """
    Saves the current environment variables for OpenAI and AWS to a JSON config file.
    The config file is saved in the ~/.mug directory.

    Returns:
        None
    """
    config = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "SESSION_LOG_NAME": os.getenv("SESSION_LOG_NAME"),
        "BUCKET_NAME": os.getenv("BUCKET_NAME"),
        "NO_AWS": os.getenv("NO_AWS", "true")
    }

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    with open(CONFIG_PATH, 'w') as config_file:
        json.dump(config, config_file, indent=4)

    print(f"Config file saved to: {CONFIG_PATH}")

def load_openai_api_key():
    """
    Loads the OpenAI API key from the configuration file.

    Returns:
        str: The OpenAI API key if it exists, otherwise None.
    """
    try:
        config = load_existing_config()
        if config:
            return config.get("OPENAI_API_KEY")
    except Exception as e:
        print(f"Error loading OpenAI API Key: {e}")
    return None

def load_session_log_file():
    """
    Loads the session log file name from the configuration file.

    Returns:
        str: The session log file name with full path if it exists, otherwise None.
    """
    try:
        config = load_existing_config()
        if config:
            session_log_name = config.get("SESSION_LOG_NAME")
            if session_log_name:
                return os.path.join(LOG_DIR, session_log_name)
    except Exception as e:
        print(f"Error loading session log file from config: {e}")
    return None

def load_session_log():
    """
    Loads the content of the session log file.

    Returns:
        str: The content of the session log file if it exists, otherwise an empty string.
    """
    session_file = load_session_log_file()
    if session_file and os.path.exists(session_file):
        try:
            with open(session_file, 'r') as log_file:
                return log_file.read()
        except Exception as e:
            print(f"Error reading session log: {e}")
    return ""

def is_valid_config(config):
    """
    Checks if the config contains valid values for required keys.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        bool: True if all required keys have non-empty values, False otherwise.
    """
    required_keys = [
        "OPENAI_API_KEY",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "SESSION_LOG_NAME",
        "BUCKET_NAME"
    ]
    for key in required_keys:
        if not config.get(key):
            return False
    return True

def set_api_keys():
    """
    Main function that orchestrates the setup of OpenAI and AWS configurations.
    Checks for existing config, and allows user to decide whether to use it or create a new one.

    Returns:
        None
    """

    existing_config = load_existing_config()

    if existing_config:
        print("Existing configuration found:")
        print(json.dumps(existing_config, indent=4))
        if is_valid_config(existing_config):
            use_existing = input("Would you like to use the existing configuration? (y/n): ").lower()
            if use_existing == 'y':
                use_existing_config(existing_config)
                print("Using existing configuration.")
                return
        else:
            print("Existing configuration in `~/.mug/` is not valid. Some keys have empty values.")

    # Step 1: Set OpenAI API Key
    set_openai_api_key()

    # Step 2: AWS setup and log creation
    if get_aws_credentials():
        aws_menu()

    # Step 3: Save new configuration to JSON
    save_config()
    print("New configuration has been saved, overwriting the existing config if it existed.")

