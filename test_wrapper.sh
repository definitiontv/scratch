#!/bin/bash

# Ensure packagetracker.sh is executable
chmod +x ./packagetracker.sh

# Initialize test counters
total_tests=0
passed_tests=0

# Helper function to assert command equality
assert_command_equals() {
  expected_command="packagetracker.py $1"
  shift
  actual_args="$@"

  total_tests=$((total_tests + 1))

  # Mock python3
  export python3_CMD_ARGS=""
  python3() {
    python3_CMD_ARGS="$*"
  }
  export -f python3

  # Execute packagetracker.sh
  # The echo "Executing: $CMD" line in packagetracker.sh will be captured by stdout
  # We need to suppress it or account for it. For now, let's capture it.
  # Also, the actual script execution might print errors to stderr.
  # Let's capture both stdout and stderr.
  script_output=$(./packagetracker.sh $actual_args 2>&1)

  # The packagetracker.sh script has an "Executing: ..." line.
  # We need to extract the command that was actually prepared for python3.
  # This is now stored in python3_CMD_ARGS by our mock.
  actual_executed_command="$python3_CMD_ARGS"

  # Unset mock
  unset -f python3
  unset python3_CMD_ARGS

  echo "Test Case: ./packagetracker.sh $actual_args"
  echo "Expected for packagetracker.py: '$expected_command'"
  echo "Actual for packagetracker.py: '$actual_executed_command'"

  # Remove the "Executing: python3 ..." line from the script_output if we were to check script_output directly
  # For now, we rely on the mocked python3_CMD_ARGS

  if [[ "$actual_executed_command" == "$expected_command" ]]; then
    echo "PASS"
    passed_tests=$((passed_tests + 1))
  else
    echo "FAIL"
    echo "  Script output was: $script_output"
  fi
  echo "--------------------------------------------------"
}

# Test cases
assert_command_equals "--json --test mypackages.json" --json --test mypackages.json
assert_command_equals "--gzip" --gzip
assert_command_equals "--detailed output.txt" --detailed output.txt
assert_command_equals "" # No args for python script

# Test --help
total_tests=$((total_tests + 1))
echo "Test Case: ./packagetracker.sh --help"
help_output=$(./packagetracker.sh --help)
if echo "$help_output" | grep -q "Usage:"; then
  echo "PASS"
  passed_tests=$((passed_tests + 1))
else
  echo "FAIL"
  echo "  Help output was: $help_output"
fi
echo "--------------------------------------------------"

# Test unknown option
total_tests=$((total_tests + 1))
echo "Test Case: ./packagetracker.sh --unknown"
./packagetracker.sh --unknown > /dev/null 2>&1
exit_status=$?
if [[ $exit_status -eq 1 ]]; then
  echo "PASS"
  passed_tests=$((passed_tests + 1))
else
  echo "FAIL - Expected exit status 1, got $exit_status"
fi
echo "--------------------------------------------------"

# Test multiple filenames
total_tests=$((total_tests + 1))
echo "Test Case: ./packagetracker.sh file1 file2"
./packagetracker.sh file1 file2 > /dev/null 2>&1
exit_status=$?
if [[ $exit_status -eq 1 ]]; then
  echo "PASS"
  passed_tests=$((passed_tests + 1))
else
  echo "FAIL - Expected exit status 1, got $exit_status"
fi
echo "--------------------------------------------------"

# Summary
echo ""
echo "Test Summary: $passed_tests / $total_tests tests passed."

# Make test_wrapper.sh executable
chmod +x ./test_wrapper.sh

# Exit with 0 if all tests passed, 1 otherwise
if [[ $passed_tests -eq $total_tests ]]; then
  exit 0
else
  exit 1
fi
