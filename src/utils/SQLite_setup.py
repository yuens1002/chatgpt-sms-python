import sqlite3
import os
from utils.path_finder import get_parent_child_path
import uuid
from datetime import datetime, timedelta
import threading

DATABASE_NAME = "chatbot.db"
db_path = os.path.join(get_parent_child_path("db"), DATABASE_NAME)


class UserDb:
    _instance = None
    lock = threading.Lock()  # Add a lock object

    def __new__(cls, *args, **kwargs):
        """
        Overriding __new__ to ensure a single instance of the class.
        """
        if not cls._instance:
            cls._instance = super(UserDb, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize_db()  # Initialize DB connection and cursor
        return cls._instance

    def _initialize_db(self):
        """
        Initializes the database schema (if not exists) and creates a connection/cursor.
        """
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        schema_sql = """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY,
            phone_number TEXT, 
            session_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP
        );
        """
        self.cursor.executescript(schema_sql)

    def __del__(self):
        """Destructor to close the database connection when the object is destroyed."""
        if self.conn:
            self.conn.close()

    def create_session(self, phone):
        """Creates a new session record in the chat_sessions table."""
        now_str = datetime.now().isoformat()  # Convert datetime to ISO format string
        session_id = f"{str(uuid.uuid4())}-{now_str}"  # Use the string
        sql = """
            INSERT INTO chat_sessions (phone_number, session_id, created_at, last_accessed)
            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        with self.lock:
            self.cursor.execute(sql, (phone, session_id))
            self.conn.commit()

    def get_session_id(self, phone):
        with self.lock:
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
        with self.lock:
            """Looks up a property (column) in the chat_sessions table by session_id."""
            if not property_name:
                raise ValueError("Property name cannot be empty")

            sql = "SELECT {} FROM chat_sessions WHERE session_id = ?".format(
                property_name
            )
            self.cursor.execute(sql, (session_id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                return None

    def write_last_session_accessed(self, session_id):
        with self.lock:
            """Updates the last_accessed time for a given session ID."""
            sql = "UPDATE chat_sessions SET last_accessed = CURRENT_TIMESTAMP WHERE session_id = ?"
            self.cursor.execute(sql, (session_id,))
            self.conn.commit()  # commit the change
