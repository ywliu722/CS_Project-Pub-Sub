from threading import current_thread
from time import sleep
import paho.mqtt.client as mqtt

serviceIP = "192.168.1.148"
servicePort = 1883
topic = "TESTING"

mqttc = mqtt.Client("python_pub")
mqttc.connect(serviceIP, servicePort)
current_nss = ""
current_mcs = ""
current_ppdu = ""
current_GI = True

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
		ppdu_rate = input[1].split()[2].split('%')[0]
		if nss != current_nss or mcs_index != current_mcs or ppdu_rate != current_ppdu or GI != current_GI:
			if GI:
				output = nss + " " + mcs_index + " " + ppdu_rate + " SGI"
			else:
				output = nss + " " + mcs_index + " " + ppdu_rate + " GI"
			mqttc.publish(topic, output)
			current_nss = nss
			current_mcs = mcs_index
			current_ppdu = ppdu_rate
			current_GI = GI
			print(output)
	except:
		continue
