import paho.mqtt.client as mqtt
from time import sleep
import base64
from PIL import Image
import io

numerical_data = None  # Global variable


class Publisher:
    def __init__(self, topic, broker_address, port=1883, keep_alive_interval=30):
        self.client = mqtt.Client()
        self.topic = topic
        self.broker_address = broker_address
        self.port = port
        self.keep_alive_interval = keep_alive_interval
    
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code: " + str(rc))
    
    def publish(self, message):
        result = self.client.publish(self.topic, message)
        # Optionally check the result of the publish
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("Message published successfully.")
        else:
            print("Failed to publish message.")
    
    def run(self):
        self.client.on_connect = self.on_connect
        print(f"Topic:{self.topic} Start Connecting...")
        self.client.connect(self.broker_address, self.port, self.keep_alive_interval)
        self.client.loop_start()
        print(f"Topic:{self.topic} Connect Successfully!")

class Subscriber:
    def __init__(self, topic, broker_address, port=1883, keep_alive_interval=30):
        self.dataReceived = None
        self.imgData = None
        self.client = mqtt.Client()
        self.topic = topic
        self.broker_address = broker_address
        self.port = port
        self.keep_alive_interval = keep_alive_interval
    
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code: " + str(rc))
        self.client.subscribe(self.topic)
    
    def on_message(self, client, userdata, message):
        # global numerical_data 
        if self.topic == 'sensor/tilt':
            decoded_message = str(message.payload.decode('utf-8'))
            self.dataReceived = decoded_message
        elif self.topic == 'camera/image':
            print("Hi, image")
            encoded_image = message.payload
            # image_data = message.payload.decode('utf-8')
            image_data = base64.b64decode(encoded_image)
            self.imgData = image_data
            
            # Convert the byte data to an image
            image = Image.open(io.BytesIO(image_data))
            
            # Display the image
            image.show()
        elif self.topic == 'camera/label':
            ecoded_message = str(message.payload.decode('utf-8'))
            print(f"Speaker: {ecoded_message}" )
        # numerical_data = self.dataReceived
        # print("MQTT Received message " + decoded_message)
        # self.client.publish(self.topic, decoded_message)
    
    def get_message(self):
        return self.dataReceived 
    
    def get_img(self):
        return self.imgData
    
    def run(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print(f"Topic:{self.topic} Start Connecting...")
        self.client.connect(self.broker_address, self.port, self.keep_alive_interval)
        print(f"Topic:{self.topic} Connect Successfully!")
        self.client.loop_start()


        
