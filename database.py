import sqlite3
from MQTT import Subscriber

# Function to create a SQLite database connection
def get_db_connection():
    conn = sqlite3.connect('messages.db')  # Database for storing images
    conn.execute('''CREATE TABLE IF NOT EXISTS image_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image BLOB NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
    return conn


def get_latest_image():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM image_data ORDER BY id DESC LIMIT 1")
    image_data = cursor.fetchone()
    conn.close()
    return image_data[0] if image_data else None