# Use Python to read the SESSION_LOG_NAME from ~/.mug/config.json
SESSION_FILE=$(python3 -c '
import json
import os

config_path = os.path.expanduser("~/.mug/config.json")
if os.path.exists(config_path):
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        session_log_name = config.get("SESSION_LOG_NAME", None)
        if session_log_name:
            print(os.path.expanduser("~/.mug/") + session_log_name)
')

if [ -z "$SESSION_FILE" ]; then
    echo "Session log file not found in config.json."
    exit 1
fi

BUCKET_NAME=$(python3 -c '
import json
import os

config_path = os.path.expanduser("~/.mug/config.json")
if os.path.exists(config_path):
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        bucket_name = config.get("BUCKET_NAME", None)
        if bucket_name:
            print(bucket_name)
')

S3_KEY=$(python3 -c '
import json
import os

config_path = os.path.expanduser("~/.mug/config.json")
if os.path.exists(config_path):
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        session_log_name = config.get("SESSION_LOG_NAME", None)
        if session_log_name:
            print(session_log_name)
')

NO_AWS=$(python3 -c '
import json
import os

config_path = os.path.expanduser("~/.mug/config.json")
if os.path.exists(config_path):
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        no_aws = config.get("NO_AWS", False)
        print(no_aws)
')

if [ -f "$SESSION_FILE" ]; then
    function execute_with_redirection() {
        {
            if [ -z "$HOST" ]; then
                export HOST=$(hostname)
                echo "---------------------------- host: $(hostname) ----------------------------" >> "$SESSION_FILE"
            elif [ "$HOST" != "$(hostname)" ]; then
                export HOST=$(hostname)
                echo "------------- host: $(hostname) -------------" >> "$SESSION_FILE"
            fi

            if [ "$NO_AWS" = "false" ]; then
                sync_from_s3 "$BUCKET_NAME" "$S3_KEY" "$SESSION_FILE"
            fi

            echo "Input:" >> "$SESSION_FILE"
            echo "- $@" >> "$SESSION_FILE"
            echo "" >> "$SESSION_FILE"

            {
                echo "Output:" >> "$SESSION_FILE"
                { "$@" |& tee -a "$SESSION_FILE"; } >> "$SESSION_FILE"
                echo "" >> "$SESSION_FILE"
            }

            if [ "$NO_AWS" = "false" ]; then
                sync_to_s3 "$BUCKET_NAME" "$SESSION_FILE" "$S3_KEY"
            fi

        } || {
            echo "An error occurred during the execution of: $@"
        }
    }

    function sync_to_s3() {
        python3 -c "import mug_core; mug_core.sync_local_to_s3('$1', '$2', '$3')"
    }

    function sync_from_s3() {
        python3 -c "import mug_core; mug_core.sync_s3_to_local('$1', '$2', '$3')"
    }
else
    echo "Session file not found."
    exit 1
fi

