import sqlite3
import json
from config.config import default_system_prompt


class Dialog:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.default_system_prompt = default_system_prompt

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS dialogs
                                (dialog_id INTEGER PRIMARY KEY,
                                messages TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS system_prompts
                                (prompt_id INTEGER PRIMARY KEY,
                                text TEXT)''')
        self.conn.commit()

    def add_message(self, dialog_id, sender, text):
        self.cursor.execute("SELECT messages FROM dialogs WHERE dialog_id=?", (dialog_id,))
        result = self.cursor.fetchone()
        if result is None:
            messages = [(sender, text)]
        else:
            messages = json.loads(result[0])
            messages.append((sender, text))
        self.cursor.execute("INSERT OR REPLACE INTO dialogs VALUES (?,?)", (dialog_id, json.dumps(messages)))
        self.conn.commit()

    def add_dialog(self, dialog_id, messages):
        self.cursor.execute("INSERT OR REPLACE INTO dialogs VALUES (?,?)", (dialog_id, json.dumps(messages)))
        self.conn.commit()

    def get_dialog(self, dialog_id):
        self.cursor.execute("SELECT messages FROM dialogs WHERE dialog_id=?", (dialog_id,))
        result = self.cursor.fetchone()
        if result is None:
            return []
        else:
            messages = json.loads(result[0])
            return messages

    def clear_dialog(self, dialog_id):
        self.cursor.execute("DELETE FROM dialogs WHERE dialog_id=?", (dialog_id,))
        self.conn.commit()

    def set_system_prompt(self, prompt_id, text):
        self.cursor.execute("INSERT OR REPLACE INTO system_prompts VALUES (?,?)", (prompt_id, text))
        self.conn.commit()

    def get_system_prompt(self, prompt_id):
        self.cursor.execute("SELECT text FROM system_prompts WHERE prompt_id=?", (prompt_id,))
        result = self.cursor.fetchone()
        if result is None:
            return self.default_system_prompt
        else:
            return result[0]
