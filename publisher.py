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
		ppdu_rate = input[1].split()[2].split('%')[0]
		current_success = input[8].split()[1]
		msec = input[10].split()[2]
		#data_len = input[10].split()[1]
		#ppdu_cnt = input[9].split()[2]
		rate = input[12].split()[4]

		if msec != current_msec:
			interval = int(msec) - int(current_msec)
			#new_data = int(data_len) - int(current_data_len)
			if GI:
				#output = nss + " " + mcs_index + " " + ppdu_rate + " SGI " + str(interval) + " " + current_success + " " + str(new_data) + " " + ppdu_cnt
				output = nss + " " + mcs_index + " " + ppdu_rate + " SGI " + current_success + " " + rate
			else:
				#output = nss + " " + mcs_index + " " + ppdu_rate + " GI " + str(interval) + " " + current_success + " " + str(new_data) + " " + ppdu_cnt
				output = nss + " " + mcs_index + " " + ppdu_rate + " GI " + current_success + " " + rate
			mqttc.publish(topic, output)
			current_msec = msec
			#current_data_len = data_len
			print(output)
	except:
		continue
