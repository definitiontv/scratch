#!/bin/bash

# Function to display help message
show_help() {
  cat << EOF
Usage: ./packagetracker.sh [options] [filename]

Description:
  A bash wrapper for the packagetracker.py script.
  This script collects information about installed packages and system metadata.

Options:
  --help        Show this help message and exit.
  --json        Save output in JSON format.
  --gzip        Compress the output file using gzip.
  --detailed    Include detailed package information (description, dependencies).
  --test        Run in test mode (prints what would happen without writing files).
  [filename]    Optional. Specify the output filename.
                If not provided, a timestamped filename will be generated.
EOF
}

# Initialize variables
PYTHON_ARGS=""
FILENAME_ARG=""

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --help)
      show_help
      exit 0
      ;;
    --json)
      PYTHON_ARGS+=" --json"
      shift
      ;;
    --gzip)
      PYTHON_ARGS+=" --gzip"
      shift
      ;;
    --detailed)
      PYTHON_ARGS+=" --detailed"
      shift
      ;;
    --test)
      PYTHON_ARGS+=" --test"
      shift
      ;;
    -*)
      echo "Error: Unknown option $1"
      exit 1
      ;;
    *)
      if [[ -n "$FILENAME_ARG" ]]; then
        echo "Error: Only one filename can be specified."
        exit 1
      fi
      FILENAME_ARG="$1"
      shift
      ;;
  esac
done

# Trim leading/trailing whitespace from PYTHON_ARGS
PYTHON_ARGS=$(echo "$PYTHON_ARGS" | awk '{$1=$1};1')

# Construct and execute the command
CMD="python3 packagetracker.py $PYTHON_ARGS $FILENAME_ARG"
echo "Executing: $CMD" # Added for debugging, can be removed later
eval "$CMD"
