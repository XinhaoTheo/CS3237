import base64
from PIL import Image
import io
from MQTT import Publisher
import time


mqtt = Publisher(topic="camera/image", broker_address="localhost")
mqtt_test = Publisher(topic="sensor/tilt", broker_address="localhost")
mqtt_speaker = Publisher(topic="camera/label", broker_address="localhost")
mqtt.run()
mqtt_test.run()
mqtt_speaker.run()

# Load and encode image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read())
    return encoded_image

# Publish the encoded image
def publish_image(image_path):
    # Encode the image
    encoded_image = encode_image(image_path)    
    # Publish the image data
    mqtt.publish(encoded_image)
    

# Example usage
image_path = "/Users/tanxinhao/Library/CloudStorage/OneDrive-NationalUniversityofSingapore/CS3237/project/MagicWand/data/images.png"
while 1:
    # publish_image(image_path)
    # time.sleep(5)
    # mqtt_test.publish("Tilt detected")
    # time.sleep(5)
    # mqtt_test.publish("No Tilt")
    # time.sleep(5)
    mqtt_speaker.publish("None")
    time.sleep(10)
    # mqtt_speaker.publish("None")
    # time.sleep(5)
    # mqtt_speaker.publish("None")
    # time.sleep(5)
    # mqtt_speaker.publish("None")
    # time.sleep(5)
    # mqtt_speaker.publish("None")
    # time.sleep(5)
    # mqtt_speaker.publish("None")
    # time.sleep(5)
    # mqtt_speaker.publish("None")
    # time.sleep(5)
    # mqtt_speaker.publish("None")
    # time.sleep(5)

# cd Desktop/OneDrive\ -\ National\ University\ of\ Singapore/CS3237/project/MagicWand 