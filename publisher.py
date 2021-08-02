from time import sleep
import paho.mqtt.client as mqtt

serviceIP = "192.168.1.15"
servicePort = 1883
topic = "TESTING"

mqttc = mqtt.Client("python_pub")
mqttc.connect(serviceIP, servicePort)

while True:
	try:
		input_file = open('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/08:c5:e1:f1:fc:11/stats','r')
		input = input_file.readline()
		input_file.close()
		mqttc.publish(topic, input)
		print(input)
		sleep(1)
	except:
		continue
