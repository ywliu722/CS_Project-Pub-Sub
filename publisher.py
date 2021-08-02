from time import sleep
import paho.mqtt.client as mqtt

serviceIP = "192.168.1.15"
servicePort = 1883
topic = "TESTING"

mqttc = mqtt.Client("python_pub")
mqttc.connect(serviceIP, servicePort)

while True:
	mqttc.publish(topic, "testing")
	print("testing")
	sleep(1)
