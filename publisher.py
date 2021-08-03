from threading import current_thread
from time import sleep
import paho.mqtt.client as mqtt

serviceIP = "192.168.1.15"
servicePort = 1883
topic = "TESTING"

mqttc = mqtt.Client("python_pub")
mqttc.connect(serviceIP, servicePort)
current_mcs = ""
current_ppdu = ""

while True:
	try:
		input_file = open('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/08:c5:e1:f1:fc:11/stats','r')
		input = input_file.readlines()
		input_file.close()
		mcs_index = input[0].split()[6]
		ppdu_rate = input[1].split()[2].split('%')[0]
		if mcs_index != current_mcs or ppdu_rate != current_ppdu:
			output = mcs_index + " " + ppdu_rate
			mqttc.publish(topic, output)
			current_mcs = mcs_index
			current_ppdu = ppdu_rate
			print(output)
	except:
		continue
