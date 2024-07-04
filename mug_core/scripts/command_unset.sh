# Unset the session log file environment variable
unset SESSION_FILE
unset BUCKET_NAME
unset NO_AWS
unset S3_KEY
unset SESSION_LOG_NAME
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY

unset -f execute_with_redirection
unset -f sync_to_s3
unset -f sync_from_s3

echo "Session ended and hooks removed."
