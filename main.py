import sqlite3
import sys
import os
import time

DB_FILE = "tasks.db"

# ANSI color codes
GRAY = '\x1b[1;90m'
RESET = '\033[0m'
BLUE = '\x1b[1;94m'
GREEN = '\x1b[1;92m'
RED = '\x1b[1;91m'

def cprint(text, color=GRAY):
    print(color + text + RESET)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class TaskManager:
    def __init__(self, db_file="tasks.db"):
        self.db_file = db_file
        self.commands = {
            "a": self.add,
            "add": self.add,
            "r": self.remove,
            "remove": self.remove,
            "l": self.list,
            "list": self.list,
            "t": self.toggle,
            "toggle": self.toggle,
            "q": self.exit,
            "quit": self.exit,
            "h": self.show_help,
            "help": self.show_help
        }
        # Initialize database
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("CREATE TABLE IF NOT EXISTS tasks(task_index INTEGER PRIMARY KEY, task_name TEXT, task_completed INTEGER)")
                conn.commit()
                cprint("Database initialized successfully. ✅", GREEN)
            except sqlite3.OperationalError as e:
                cprint(f"Error initializing database: {e} ⛔", RED)

    def _get_connection(self):
        return sqlite3.connect(self.db_file)

    def add(self):
        clear_screen()
        cprint("Add a New Task", BLUE)
        task_name = input("Task name: ").strip().capitalize()
        if not task_name:
            cprint("Task name cannot be empty. ❌", RED)
            return
        if len(task_name) > 255:
            cprint("Task name too long (max 255 characters). ❌", RED)
            return
        while True:
            task_completed_input = input("Is task completed? (y/n): ").lower()
            if task_completed_input in ("y", "n"):
                task_state = 1 if task_completed_input == "y" else 0
                break
            cprint("Please enter 'y' or 'n'. ❌", RED)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO tasks (task_name, task_completed) VALUES (?, ?)", (task_name, task_state))
                conn.commit()
                cprint(f"Task '{task_name}' added successfully! ✨", GREEN)
            except sqlite3.Error as e:
                cprint(f"Error adding task: {e} ⛔", RED)
        time.sleep(0.1)

    def list(self):
        clear_screen()
        query = "SELECT task_index, task_name, task_completed FROM tasks ORDER BY task_completed DESC, task_name ASC"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            tasks = cursor.execute(query).fetchall()
            if not tasks:
                cprint("No tasks found. Add some tasks! 📝", GRAY)
                return {}
            cprint("--- Task List ---", BLUE)
            display_number = 1
            display_to_id_map = {}
            for task_item in tasks:
                status = "✅ Completed" if task_item[2] == 1 else "⏳ Pending"
                cprint(f"{display_number}. {task_item[1]} [{status}]", GRAY)
                display_to_id_map[display_number] = task_item[0]
                display_number += 1
            cprint("----------------", BLUE)
            return display_to_id_map
        time.sleep(0.1)

    def remove(self):
        clear_screen()
        display_to_id_map = self.list()
        if not display_to_id_map:
            cprint("No tasks to remove. 🤷", GRAY)
            time.sleep(0.1)
            return
        try:
            display_num = int(input("Enter task number to remove: "))
            task_id = display_to_id_map.get(display_num)
            if task_id is None:
                cprint(f"No task with number {display_num}. 🤔", RED)
                time.sleep(0.1)
                return
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT task_name FROM tasks WHERE task_index = ?", (task_id,))
                task_name = cursor.fetchone()[0]
                confirm = input(f"Delete '{task_name}'? (y/n): ").lower()
                if confirm != "y":
                    cprint("Deletion cancelled. 😊", GRAY)
                    time.sleep(0.1)
                    return
                cursor.execute("DELETE FROM tasks WHERE task_index = ?", (task_id,))
                if cursor.rowcount > 0:
                    conn.commit()
                    cprint(f"Task '{task_name}' deleted successfully! 🗑️", GREEN)
                else:
                    cprint(f"Failed to delete task. 🤔", RED)
        except ValueError:
            cprint("Please enter a valid number. 🔢", RED)
        time.sleep(0.1)

    def toggle(self):
        clear_screen()
        display_to_id_map = self.list()
        if not display_to_id_map:
            cprint("No tasks to toggle. 🤷", GRAY)
            time.sleep(0.1)
            return
        try:
            display_num = int(input("Enter task number to toggle: "))
            task_id = display_to_id_map.get(display_num)
            if task_id is None:
                cprint(f"No task with number {display_num}. 🤔", RED)
                time.sleep(0.1)
                return
            with self._get_connection() as conn:
                cursor = conn.cursor()
                while True:
                    task_completed_input = input("Set as completed? (y/n): ").lower()
                    if task_completed_input in ("y", "n"):
                        new_state = 1 if task_completed_input == "y" else 0
                        break
                    cprint("Please enter 'y' or 'n'. ❌", RED)
                cursor.execute("UPDATE tasks SET task_completed = ? WHERE task_index = ?", (new_state, task_id))
                if cursor.rowcount > 0:
                    conn.commit()
                    status = "completed" if new_state == 1 else "pending"
                    cprint(f"Task set to {status}! ✅🔄", GREEN)
                else:
                    cprint("Task status unchanged (already in that state). 🤷", GRAY)
        except ValueError:
            cprint("Please enter a valid number. 🔢", RED)
        time.sleep(0.1)

    def exit(self):
        clear_screen()
        cprint("Thanks for using To-Do List! 👋", BLUE)
        time.sleep(0.1)
        sys.exit(0)

    def show_help(self):
        clear_screen()
        cprint("Available Commands", BLUE)
        print("""
        add (a)     - Add a new task
        remove (r)  - Remove a task by number
        list (l)    - List all tasks
        toggle (t)  - Change task completion status
        quit (q)    - Exit the application
        help (h)    - Show this help
        """)
        time.sleep(0.1)

    def run(self):
        clear_screen()
        cprint("Welcome to your To-Do List! Type 'help' for commands", BLUE)
        while True:
            user_input = input("\n>>> ").lower()
            command = self.commands.get(user_input)
            if command:
                command()
            else:
                clear_screen()
                cprint("Invalid command. Type 'help' for commands. ❓", RED)
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        task_app = TaskManager()
        task_app.run()
    except KeyboardInterrupt:
        task_app.exit()