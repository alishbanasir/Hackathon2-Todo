#!/usr/bin/env python3
"""
In-Memory Todo CLI Application
A simple interactive command-line todo manager with in-memory storage.
Data is lost when the program exits.
"""

from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Todo:
    """Represents a single todo item."""
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        status = "✓" if self.completed else "✗"
        desc = f" - {self.description}" if self.description else ""
        return f"[{status}] #{self.id}: {self.title}{desc}"


class TodoManager:
    """Manages in-memory todo list operations."""

    def __init__(self):
        self.todos: List[Todo] = []
        self.next_id: int = 1

    def add_todo(self, title: str, description: str = "") -> Todo:
        """Add a new todo item."""
        if not title.strip():
            raise ValueError("Title cannot be empty")

        todo = Todo(
            id=self.next_id,
            title=title.strip(),
            description=description.strip()
        )
        self.todos.append(todo)
        self.next_id += 1
        return todo

    def view_todos(self) -> List[Todo]:
        """Return all todos."""
        return self.todos.copy()

    def get_todo_by_id(self, todo_id: int) -> Optional[Todo]:
        """Find a todo by ID."""
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None

    def update_todo(self, todo_id: int, title: Optional[str] = None,
                   description: Optional[str] = None) -> Todo:
        """Update an existing todo."""
        todo = self.get_todo_by_id(todo_id)
        if not todo:
            raise ValueError(f"Todo with ID {todo_id} not found")

        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty")
            todo.title = title.strip()

        if description is not None:
            todo.description = description.strip()

        return todo

    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo by ID."""
        todo = self.get_todo_by_id(todo_id)
        if not todo:
            raise ValueError(f"Todo with ID {todo_id} not found")

        self.todos.remove(todo)
        return True

    def mark_complete(self, todo_id: int, completed: bool = True) -> Todo:
        """Mark a todo as complete or incomplete."""
        todo = self.get_todo_by_id(todo_id)
        if not todo:
            raise ValueError(f"Todo with ID {todo_id} not found")

        todo.completed = completed
        return todo


def display_menu():
    """Display the main menu."""
    print("\n" + "="*50)
    print("           IN-MEMORY TODO CLI")
    print("="*50)
    print("1. Add Todo")
    print("2. View All Todos")
    print("3. Update Todo")
    print("4. Delete Todo")
    print("5. Mark Todo Complete/Incomplete")
    print("6. Exit")
    print("="*50)


def get_input(prompt: str, required: bool = True) -> str:
    """Get user input with optional validation."""
    while True:
        value = input(prompt).strip()
        if not required or value:
            return value
        print("This field is required. Please try again.")


def get_int_input(prompt: str) -> int:
    """Get integer input from user."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Please enter a valid number.")


def handle_add_todo(manager: TodoManager):
    """Handle adding a new todo."""
    print("\n--- Add New Todo ---")
    title = get_input("Enter title: ", required=True)
    description = get_input("Enter description (optional): ", required=False)

    try:
        todo = manager.add_todo(title, description)
        print(f"\n✓ Todo added successfully!")
        print(f"  {todo}")
    except ValueError as e:
        print(f"\n✗ Error: {e}")


def handle_view_todos(manager: TodoManager):
    """Handle viewing all todos."""
    print("\n--- All Todos ---")
    todos = manager.view_todos()

    if not todos:
        print("No todos yet. Add one to get started!")
        return

    # Group by completion status
    incomplete = [t for t in todos if not t.completed]
    complete = [t for t in todos if t.completed]

    if incomplete:
        print("\n📋 Incomplete:")
        for todo in incomplete:
            print(f"  {todo}")

    if complete:
        print("\n✅ Complete:")
        for todo in complete:
            print(f"  {todo}")

    print(f"\nTotal: {len(todos)} | Complete: {len(complete)} | Incomplete: {len(incomplete)}")


def handle_update_todo(manager: TodoManager):
    """Handle updating a todo."""
    print("\n--- Update Todo ---")

    # Show current todos
    todos = manager.view_todos()
    if not todos:
        print("No todos to update.")
        return

    print("Current todos:")
    for todo in todos:
        print(f"  {todo}")

    todo_id = get_int_input("\nEnter todo ID to update: ")

    # Check if todo exists
    existing = manager.get_todo_by_id(todo_id)
    if not existing:
        print(f"\n✗ Todo with ID {todo_id} not found.")
        return

    print(f"\nCurrent: {existing}")
    print("(Leave blank to keep current value)")

    title = get_input(f"New title [{existing.title}]: ", required=False)
    description = get_input(f"New description [{existing.description}]: ", required=False)

    try:
        # Only pass non-empty values
        kwargs = {}
        if title:
            kwargs['title'] = title
        if description or description == "":  # Allow clearing description
            kwargs['description'] = description

        if not kwargs:
            print("\n✗ No changes made.")
            return

        updated = manager.update_todo(todo_id, **kwargs)
        print(f"\n✓ Todo updated successfully!")
        print(f"  {updated}")
    except ValueError as e:
        print(f"\n✗ Error: {e}")


def handle_delete_todo(manager: TodoManager):
    """Handle deleting a todo."""
    print("\n--- Delete Todo ---")

    # Show current todos
    todos = manager.view_todos()
    if not todos:
        print("No todos to delete.")
        return

    print("Current todos:")
    for todo in todos:
        print(f"  {todo}")

    todo_id = get_int_input("\nEnter todo ID to delete: ")

    try:
        # Show what will be deleted
        todo = manager.get_todo_by_id(todo_id)
        if todo:
            print(f"\nAbout to delete: {todo}")
            confirm = get_input("Are you sure? (y/n): ", required=True).lower()

            if confirm == 'y':
                manager.delete_todo(todo_id)
                print(f"\n✓ Todo #{todo_id} deleted successfully!")
            else:
                print("\n✗ Deletion cancelled.")
        else:
            print(f"\n✗ Todo with ID {todo_id} not found.")
    except ValueError as e:
        print(f"\n✗ Error: {e}")


def handle_mark_complete(manager: TodoManager):
    """Handle marking a todo as complete/incomplete."""
    print("\n--- Mark Todo Complete/Incomplete ---")

    # Show current todos
    todos = manager.view_todos()
    if not todos:
        print("No todos available.")
        return

    print("Current todos:")
    for todo in todos:
        print(f"  {todo}")

    todo_id = get_int_input("\nEnter todo ID: ")

    try:
        todo = manager.get_todo_by_id(todo_id)
        if not todo:
            print(f"\n✗ Todo with ID {todo_id} not found.")
            return

        # Toggle completion status
        new_status = not todo.completed
        action = "complete" if new_status else "incomplete"

        confirm = get_input(f"Mark as {action}? (y/n): ", required=True).lower()

        if confirm == 'y':
            manager.mark_complete(todo_id, new_status)
            print(f"\n✓ Todo marked as {action}!")
            print(f"  {todo}")
        else:
            print("\n✗ Action cancelled.")
    except ValueError as e:
        print(f"\n✗ Error: {e}")


def main():
    """Main application loop."""
    manager = TodoManager()

    print("\n🎯 Welcome to In-Memory Todo CLI!")
    print("⚠️  Note: All data is stored in memory and will be lost when you exit.")

    while True:
        display_menu()

        try:
            choice = get_input("\nEnter your choice (1-6): ", required=True)

            if choice == '1':
                handle_add_todo(manager)
            elif choice == '2':
                handle_view_todos(manager)
            elif choice == '3':
                handle_update_todo(manager)
            elif choice == '4':
                handle_delete_todo(manager)
            elif choice == '5':
                handle_mark_complete(manager)
            elif choice == '6':
                print("\n👋 Goodbye! All todos have been discarded.")
                break
            else:
                print("\n✗ Invalid choice. Please enter a number between 1 and 6.")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()
