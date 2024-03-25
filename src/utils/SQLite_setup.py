import sqlite3
import os
from utils.path_finder import get_parent_child_path
import uuid
from datetime import datetime, timedelta

DATABASE_NAME = "chatbot.db"
db_path = os.path.join(get_parent_child_path("db"), DATABASE_NAME)


class UserDb:
    def __init__(self):
        """Initializes the database and creates a connection instance."""
        self._initialize_db()
        self.cursor = self.conn.cursor()  # Reuse the connection

    def _initialize_db(self):
        """Creates the database schema if it doesn't exist and establishes a connection."""
        schema_sql = """
        CREATE TABLE chat_sessions (
            id INTEGER PRIMARY KEY,
            phone_number TEXT, 
            session_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP
        );
        """
        self.conn = sqlite3.connect(db_path)  # Create the connection
        self.cursor.executescript(schema_sql)

    def create_session(self, phone):
        """Creates a new session record in the chat_sessions table."""
        sql = """
            INSERT INTO chat_sessions (phone_number, session_id, created_at, last_accessed)
            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        self.cursor.execute(sql, (phone, f"{str(uuid.uuid4())}-{str(datetime.now)}"))
        self.conn.commit()

    def get_session_id(self, phone):
        """Retrieves the session ID associated with a given phone number."""
        self.cursor.execute(
            "SELECT session_id FROM chat_sessions WHERE phone_number = ?", (phone,)
        )
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def get_property(self, session_id, property_name):
        """Looks up a property (column) in the chat_sessions table by session_id."""
        if not property_name:
            raise ValueError("Property name cannot be empty")

        sql = "SELECT {} FROM chat_sessions WHERE session_id = ?".format(property_name)
        self.cursor.execute(sql, (session_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def write_last_session_accessed(self, session_id):
        """Updates the last_accessed time for a given session ID."""
        sql = "UPDATE chat_sessions SET last_accessed = CURRENT_TIMESTAMP WHERE session_id = ?"
        self.cursor.execute(sql, (session_id,))
        self.conn.commit()  # commit the change
