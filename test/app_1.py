from flask import Flask, render_template, redirect, url_for, request, jsonify, send_file
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO
import sqlite3
import sys
import os
import io
from MQTT import Subscriber

app = Flask(__name__)
socketio = SocketIO(app)
scheduler = APScheduler()
scheduler.init_app(app)

if not scheduler.running:
    scheduler.start()

# MQTT Subscriber Setup
mqtt = Subscriber(topic="weather/temp", broker_address="localhost")
mqtt.run()

numerical_data = None

# Function to create a SQLite database connection
def get_db_connection():
    conn = sqlite3.connect('messages.db')  # Database for storing images
    conn.execute('''CREATE TABLE IF NOT EXISTS image_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image BLOB NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
    return conn

# Function to store the image in the SQLite database
def store_image_in_db(image_path):
    conn = get_db_connection()
    with open(image_path, 'rb') as img_file:
        image_data = img_file.read()
    conn.execute("INSERT INTO image_data (image) VALUES (?)", (image_data,))
    conn.commit()
    conn.close()

# Function to retrieve and store the image via MQTT
def retrieve_and_store_image():
    image_path = mqtt.get_image()  # Get the image from MQTT
    if image_path:
        store_image_in_db(image_path)
        os.remove(image_path)  # Clean up the image file after storing it

# Scheduler job to check for images every second
scheduler.add_job(id="image_data_process", func=retrieve_and_store_image, trigger='interval', seconds=60)

# Function to retrieve the latest image from the SQLite database
def get_latest_image():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM image_data ORDER BY id DESC LIMIT 1")
    image_data = cursor.fetchone()
    conn.close()
    return image_data[0] if image_data else None

# New route to display the latest image
@app.route('/latest_image')
def latest_image():
    image_data = get_latest_image()
    if image_data:
        return send_file(io.BytesIO(image_data), mimetype='image/jpeg')
    return "No image found", 404

# Function to process numerical data from MQTT
def process_numerical_data():
    global numerical_data
    with app.app_context():
        numerical_data = mqtt.get_message()
        if numerical_data is not None:
            try:
                if numerical_data >= 31.0:
                    socketio.emit('redirect', {'url': '/alert_1'})
                    return True
            except Exception as e:
                print(f"Error in numerical prediction: {e}")
    return False

# Add scheduler jobs for numerical data
scheduler.add_job(id="numerical_data_process", func=process_numerical_data, trigger='interval', seconds=1)

# Main Route
@app.route('/')
def main():
    return render_template('home_1.html')

# Alert Page Route
@app.route('/alert_1')
def alert_page():
    return render_template('alert_1.html')

# Endpoint to Receive Numerical Data
@app.route('/numerical', methods=['POST'])
def receive_numerical_data():
    global numerical_data
    numerical_data = request.get_json().get("value")
    result_redirect = process_numerical_data()
    if result_redirect:
        return redirect(url_for('alert_page'))
    return jsonify({"message": "Numerical data received"})

# Start the application
if __name__ == "__main__":
    try:
        socketio.run(app, debug=True)
    except KeyboardInterrupt:
        scheduler.shutdown(wait=True)
        sys.exit()
