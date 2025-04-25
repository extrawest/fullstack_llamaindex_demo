#!/bin/bash

# Determine the script directory and project root
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PROJECT_ROOT="$SCRIPT_DIR" # Assuming the script is in the project root

# Activate Python virtual environment
VENV_PATH="$PROJECT_ROOT/.venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    echo "Activating Python virtual environment..."
    source "$VENV_PATH"
else
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Function to clean up background processes
cleanup() {
    echo "Cleaning up background processes..."
    # Check if PIDs exist before killing
    if [ -n "$INDEX_PID" ]; then
        kill "$INDEX_PID" 2>/dev/null
        echo "Killed index_server (PID: $INDEX_PID)"
    fi
    if [ -n "$FLASK_PID" ]; then
        kill "$FLASK_PID" 2>/dev/null
        echo "Killed Flask server (PID: $FLASK_PID)"
    fi
    # Add kill command for serve if it were run in background
    # if [ -n "$SERVE_PID" ]; then kill "$SERVE_PID"; fi 
    # Optionally wait for processes to ensure they are killed
    # wait $INDEX_PID 2>/dev/null
    # wait $FLASK_PID 2>/dev/null
    echo "Cleanup finished."
    exit 0 # Exit script after cleanup
}

# Trap signals to call the cleanup function
trap cleanup SIGINT SIGTERM

# Start backend index server
echo "Starting index_server..."
python "$PROJECT_ROOT/index_server.py" &
INDEX_PID=$!
echo "index_server running with PID $INDEX_PID"

# Wait for the server to start - adjust sleep time if needed
echo "Waiting for index_server to initialize..."
sleep 60 # Increase if index creation takes longer

# Start the flask server
echo "Starting Flask server..."
python "$PROJECT_ROOT/flask_demo.py" &
FLASK_PID=$!
echo "Flask server running with PID $FLASK_PID"

# Build and serve the frontend
FRONTEND_DIR="$PROJECT_ROOT/react_frontend"
if [ -d "$FRONTEND_DIR" ]; then
    echo "Building and serving frontend..."
    cd "$FRONTEND_DIR" || exit 1 # Exit if cd fails
    # assumes you've ran npm install already
    npm run build && npx serve -s build -l 3000 # Use npx and specify a port (e.g., 3000)
    # This command runs in the foreground. Script will wait here.
    # When serve is stopped (e.g., Ctrl+C), the trap will trigger cleanup.
else
    echo "Error: Frontend directory not found at $FRONTEND_DIR"
    # Optionally kill the background servers if frontend fails
    cleanup # Call cleanup if frontend setup fails
    exit 1
fi

# Wait for all background jobs to finish (optional, as serve runs in foreground)
# If serve were backgrounded (&), this wait would be necessary to keep script alive
# wait

# The script normally exits when 'npx serve' exits.
# The trap handles cleanup if interrupted.
echo "Application stopped normally."
