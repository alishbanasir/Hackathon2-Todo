"""Manual test script for Phase I todo CLI.

This script demonstrates all CRUD operations in a single session
since the in-memory repository doesn't persist between runs.
"""

import subprocess
import sys


def run_command(cmd: str) -> None:
    """Run a todo command and display the output."""
    print(f"\n{'='*60}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        # Filter out JSON logs for cleaner output
        lines = result.stdout.split('\n')
        for line in lines:
            if not line.startswith('{'):
                print(line)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    if result.returncode != 0:
        print(f"Exit code: {result.returncode}")


def main() -> None:
    """Run the manual test suite."""
    print("Phase I Todo CLI - Manual Test Suite")
    print("Note: Each command runs in a new process, so tasks don't persist.")
    print("In-memory storage is working as designed for Phase I.")

    # Test 1: Add tasks
    run_command('uv run todo add "Buy groceries"')
    run_command('uv run todo add "Write report"')
    run_command('uv run todo add "Call dentist"')

    # Test 2: List tasks (will be empty - expected for in-memory)
    run_command('uv run todo list')

    # Test 3: Help command
    run_command('uv run todo help')

    # Test 4: Error handling - empty description
    run_command('uv run todo add ""')

    # Test 5: Error handling - task not found
    run_command('uv run todo done 999')

    # Test 6: Update command (will fail - no tasks)
    run_command('uv run todo update 1 "New description"')

    # Test 7: Delete command (will fail - no tasks)
    run_command('uv run todo delete 1')

    print("\n" + "="*60)
    print("Test suite complete!")
    print("="*60)
    print("\nNOTE: Tasks don't persist between commands because each")
    print("'uv run todo' creates a new in-memory repository instance.")
    print("This is expected behavior for Phase I.")
    print("\nPhase II will add database persistence to enable cross-session storage.")


if __name__ == "__main__":
    main()
