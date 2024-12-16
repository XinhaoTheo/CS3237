from flask import Flask, Flask, render_template, redirect, url_for, request, jsonify, send_file
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO, emit
import sys
import io

from MQTT import Subscriber
from telegram_bot import send_telegram_alert
from database import get_latest_image, get_db_connection


app = Flask(__name__)
socketio = SocketIO(app)
scheduler = APScheduler()
scheduler.init_app(app)
if not scheduler.running: 
    scheduler.start() # start the app

mqtt_tilt = Subscriber(topic="sensor/tilt", broker_address="localhost")
mqtt_tilt.run()

mqtt_img = Subscriber(topic="camera/image", broker_address="localhost")
mqtt_img.run()

mqtt_label = Subscriber(topic="camera/label", broker_address="localhost")
mqtt_label.run()


# Function to store the image in the SQLite database
def store_image_in_db():
    print("start store img")
    conn = get_db_connection()
    image_data = mqtt_img.get_img()
    if not image_data:
        print("No image to store")
        return
    conn.execute("INSERT INTO image_data (image) VALUES (?)", (image_data,))
    conn.commit()
    conn.close()

scheduler.add_job(id="image_data_process", func=store_image_in_db, trigger='interval', seconds=60)

# New route to display the latest image
@app.route('/latest_image')
def latest_image():
    image_data = get_latest_image()
    if image_data:
        return send_file(io.BytesIO(image_data), mimetype='image/jpeg')
    return "No image found", 404


numerical_data = None
image_data = None

def process_numerical_data():
    # global numerical_data
    with app.app_context():  # Ensure application context is available
        numerical_data = mqtt_tilt.get_message()
        # print("numerical_data",numerical_data)
        if numerical_data is not None:
            try:
                if numerical_data == "Tilt detected":
                    # Emit event via SocketIO to trigger redirection
                    print("Tilt Detected!")
                    socketio.emit('redirect', {'url': '/alert_1'})
                    send_telegram_alert("Alert! Fall detected.")
                    return True
            except Exception as e:
                print(f"Error in numerical prediction: {e}")
    return False

# Scheduler to Receive Data Every Second
scheduler.add_job(id="numerical_data_process", func=process_numerical_data, trigger='interval', seconds=1)

# Main Route
@app.route('/')
def main():
    return render_template('home_new.html')

# Alert Page if the Condition is Met
@app.route('/alert_1')
def alert_page():
    return render_template('alert_1.html')

# Endpoint to Receive Numerical Data via JSON
@app.route('/numerical', methods=['POST'])
def receive_numerical_data():
    global numerical_data
    numerical_data = request.get_json().get("value")  # Expecting JSON format {"value": <number>}
    result_redirect = process_numerical_data()  # Check if it triggers redirect
    if result_redirect:
        return redirect(url_for('alert_page'))  # Redirect to alert page if condition is met
    return jsonify({"message": "Numerical data received"})


if __name__ == "__main__": # run the application
    try:
        # app.run(debug=True)
        socketio.run(app, debug=True)
    except KeyboardInterrupt:
        scheduler.shutdown(wait=True)
        sys.exit()