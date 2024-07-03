import os
import re
import json
import boto3
import configparser

from botocore.exceptions import NoCredentialsError, PartialCredentialsError

LOG_DIR = os.path.expanduser("~/.mug")

def ensure_log_directory():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"Created log directory: {LOG_DIR}")

def get_aws_credentials():
    credentials_path = os.path.expanduser("~/.aws/credentials")
    if os.path.exists(credentials_path):
        config = configparser.ConfigParser()
        config.read(credentials_path)

        if 'default' in config:
            access_key = config['default'].get('aws_access_key_id')
            secret_key = config['default'].get('aws_secret_access_key')
            if access_key and secret_key:
                print("Using AWS credentials from ~/.aws/credentials")
                os.environ["AWS_ACCESS_KEY_ID"] = access_key
                os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
                return True

    print("AWS credentials file not found or incomplete.")
    return set_aws_credentials()

def set_aws_credentials():
    access_key = input("Please enter your AWS Access Key (or 'q' to quit): ")
    if access_key.lower() == 'q':
        print("Exiting without setting the AWS Access Key.")
        os.environ["NO_AWS"] = "true"
        os.environ["AWS_ACCESS_KEY_ID"] = ""
        os.environ["AWS_SECRET_ACCESS_KEY"] = ""
        return False

    secret_key = input("Please enter your AWS Secret Key (or 'q' to quit): ")
    if secret_key.lower() == 'q':
        print("Exiting without setting the AWS Secret Key.")
        os.environ["NO_AWS"] = "true"
        os.environ["AWS_ACCESS_KEY_ID"] = ""
        os.environ["AWS_SECRET_ACCESS_KEY"] = ""
        return False

    os.environ["AWS_ACCESS_KEY_ID"] = access_key
    os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
    os.environ["NO_AWS"] = "false"
    print("The AWS credentials have been set as environment variables.")
    return True

def list_s3_buckets():
    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_buckets()
        print("S3 Buckets:")
        for i, bucket in enumerate(response['Buckets']):
            print(f"{i + 1}. {bucket['Name']}")
        return response['Buckets']
    except NoCredentialsError:
        print("Credentials not available.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return []

def list_bucket_contents(bucket_name):
    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            print(f"Contents of bucket '{bucket_name}':")
            for obj in response['Contents']:
                print(f"  {obj['Key']}")
        else:
            print(f"The bucket '{bucket_name}' is empty.")
    except Exception as e:
        print(f"An error occurred: {e}")

def aws_menu():
    buckets = list_s3_buckets()
    selected_bucket = None

    if len(buckets) == 0:
        print("No S3 buckets found.")
        choice = input("You can use 'n' option to create a new bucket or use the 'q' option to use local storage: ")
        if choice.lower() == 'n':
            bucket_name = input("Enter the new bucket name: ")
            create_bucket(bucket_name)
            buckets = list_s3_buckets()
        elif choice.lower() == 'q':
            print("Exiting without selecting a bucket.")
            os.environ["NO_AWS"] = "true"
            os.environ["AWS_ACCESS_KEY_ID"] = ""
            os.environ["AWS_SECRET_ACCESS_KEY"] = ""
            log_number = get_next_log_number_local()
            local_file = os.path.join(LOG_DIR, f"session_log_{log_number}.txt")
            with open(local_file, 'w') as file:
                pass
            os.environ["SESSION_LOG_NAME"] = f"session_log_{log_number}.txt"
            return

    while True:
        choice = input('"s" for show mode, "n" for new bucket, "q" for not selecting, 1~{} to select: '.format(len(buckets)))

        if choice.lower() == 's':
            while True:
                print("S3 Buckets:")
                for i, bucket in enumerate(buckets):
                    print(f"{i + 1}. {bucket['Name']}")
                bucket_choice = input("Which bucket's contents would you like to list? Please select a number between 1 and {}: ".format(len(buckets)))
                if bucket_choice.lower() == 'q':
                    print("Exiting without selecting a bucket.")
                    os.environ["NO_AWS"] = "true"
                    os.environ["AWS_ACCESS_KEY_ID"] = ""
                    os.environ["AWS_SECRET_ACCESS_KEY"] = ""
                    return
                if bucket_choice.isdigit():
                    bucket_index = int(bucket_choice) - 1
                    if 0 <= bucket_index < len(buckets):
                        list_bucket_contents(buckets[bucket_index]['Name'])
                        break
                    else:
                        print("Invalid bucket number.")
                else:
                    print("Invalid input. Please enter a number.")

        elif choice.lower() == 'n':
            bucket_name = input("Enter the new bucket name: ")
            create_bucket(bucket_name)
            buckets = list_s3_buckets()
            use_bucket(bucket_name)
            return

        elif choice.lower() == 'q':
            print("No bucket selected. Exiting.")
            os.environ["NO_AWS"] = "true"
            os.environ["AWS_ACCESS_KEY_ID"] = ""
            os.environ["AWS_SECRET_ACCESS_KEY"] = ""
            log_number = get_next_log_number_local()
            local_file = os.path.join(LOG_DIR, f"session_log_{log_number}.txt")
            with open(local_file, 'w') as file:
                pass
            os.environ["SESSION_LOG_NAME"] = f"session_log_{log_number}.txt"
            return

        elif choice.isdigit():
            bucket_index = int(choice) - 1
            if 0 <= bucket_index < len(buckets):
                selected_bucket = buckets[bucket_index]['Name']
                os.environ["NO_AWS"] = "false"
                os.environ["BUCKET_NAME"] = selected_bucket
                print(f"Selected bucket: {selected_bucket}")
                use_bucket(selected_bucket)
                return
            else:
                print("Invalid bucket number.")
        else:
            print("Invalid choice. Please try again.")

def create_bucket(bucket_name):
    try:
        s3_client = boto3.client('s3')
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    except Exception as e:
        print(f"An error occurred while creating the bucket: {e}")

def get_next_log_number(bucket_name):
    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            log_numbers = []
            for obj in response['Contents']:
                match = re.match(r'session_log_(\d+)\.txt', obj['Key'])
                if match:
                    log_numbers.append(int(match.group(1)))
            if log_numbers:
                return max(log_numbers) + 1
        return 1
    except Exception as e:
        print(f"An error occurred while determining the next log number: {e}")
        return 1

def list_session_logs(bucket_name):
    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        session_logs = []
        if 'Contents' in response:
            for obj in response['Contents']:
                if re.match(r'session_log_\d+\.txt', obj['Key']):
                    session_logs.append(obj['Key'])
        return session_logs
    except Exception as e:
        print(f"An error occurred while listing session logs: {e}")
        return []

def list_local_session_logs():
    ensure_log_directory()
    local_logs = []
    for file in os.listdir(LOG_DIR):
        if re.match(r'session_log_\d+\.txt', file):
            local_logs.append(file)
    return local_logs

def get_next_log_number_local():
    local_logs = list_local_session_logs()
    if local_logs:
        log_numbers = []
        for log in local_logs:
            match = re.match(r'session_log_(\d+)\.txt', log)
            if match:
                log_numbers.append(int(match.group(1)))
        if log_numbers:
            return max(log_numbers) + 1
    return 1

def use_bucket(bucket_name):
    ensure_log_directory()
    session_logs = list_session_logs(bucket_name)

    if session_logs:
        print(f"Session logs available: {', '.join(session_logs)}")
        choice = input("You can continue with an existing log or create a new one. Enter the log number (`session_log_{number}.txt`) to continue or 'n' for a new log: ")
        if choice.lower() == 'n':
            log_number = get_next_log_number(bucket_name)
        elif choice.isdigit():
            log_number = int(choice)
        else:
            print("Invalid choice. Creating a new session log.")
            log_number = get_next_log_number(bucket_name)
    else:
        log_number = get_next_log_number(bucket_name)
        choice = str(log_number)
        print(f"No session logs found. `session_log_{log_number}.txt` has been created.")

    local_file = os.path.join(LOG_DIR, f"session_log_{log_number}.txt")
    s3_key = f"session_log_{log_number}.txt"

    os.environ["SESSION_LOG_NAME"] = s3_key

    if choice.lower() != 'n' and choice.isdigit():
        sync_s3_to_local(bucket_name, s3_key, local_file)
    else:
        with open(local_file, 'w') as file:
            file.write("This is a session log.\n")
        sync_s3_to_local(bucket_name, s3_key, local_file)
        print(f"Created local log file: {local_file}")

    sync_local_to_s3(bucket_name, local_file, s3_key)

def sync_local_to_s3(bucket_name, local_file, s3_key):
    try:
        s3_client = boto3.client('s3')
        s3_client.upload_file(local_file, bucket_name, s3_key)
        print(f"Synced local file '{local_file}' to S3 bucket '{bucket_name}' as '{s3_key}'.")
    except Exception as e:
        print(f"An error occurred while syncing local file to S3: {e}")

def sync_s3_to_local(bucket_name, s3_key, local_file):
    try:
        s3_client = boto3.client('s3')
        s3_client.download_file(bucket_name, s3_key, local_file)
        print(f"Synced S3 file '{s3_key}' from bucket '{bucket_name}' to local file '{local_file}'.")
    except s3_client.exceptions.NoSuchKey:
        print(f"The file '{s3_key}' does not exist in the S3 bucket '{bucket_name}'.")
    except Exception as e:
        print(f"An error occurred while syncing S3 file to local: {e}")

if __name__ == "__main__":
    if get_aws_credentials():
        aws_menu()
