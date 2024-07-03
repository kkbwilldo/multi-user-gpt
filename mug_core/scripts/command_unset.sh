# Unset the session log file environment variable
unset SESSION_FILE

# Remove preexec function
unset -f preexec

echo "Session ended and hooks removed."
