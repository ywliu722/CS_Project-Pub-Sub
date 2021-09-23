from threading import current_thread
from time import sleep
import paho.mqtt.client as mqtt

serviceIP = "192.168.1.148"
servicePort = 1883
topic = "TESTING"

mqttc = mqtt.Client("python_pub")
mqttc.connect(serviceIP, servicePort)

current_msec = "0"
current_data_len = "0"

while True:
	try:
		input_file = open('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/08:c5:e1:f1:fc:11/stats','r')
		#input_file = open('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/48:45:20:98:d4:1a/stats','r')
		input = input_file.readlines()
		input_file.close()
		nss = input[0].split()[5]
		mcs_index = input[0].split()[6]
		if len(input[0].split()) == 8:
			GI = True
		else:
			GI = False
		msec = input[7].split()[1]
		data_len = input[8].split()[1]

		if msec != current_msec:
			new_data = int(data_len) - int(current_data_len)
			if GI:
				output = nss + " " + mcs_index + " SGI " + str(new_data)
			else:
				output = nss + " " + mcs_index + " GI " + str(new_data)
			mqttc.publish(topic, output)
			current_msec = msec
			current_data_len = data_len
			print(output)
			sleep(1)
	except:
		continue
