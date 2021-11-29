from threading import current_thread
from os import listdir, path
import time
import paho.mqtt.client as mqtt

serviceIP = "192.168.1.148"
servicePort = 1883
topic = "TESTING"

mqttc = mqtt.Client("python_pub")
mqttc.connect(serviceIP, servicePort)

current_msec = "0"
current_data_len = 0
current_time = 0.0
current_tx = 0
current_multi_tx = 0
current_other_tx = {}
multi_device = True

while True:
	try:
		# busy waiting until reaching 1 second
		time_now = time.time()
		if time_now - current_time < 1 :
			continue
		
		# read device 1
		input_file = open('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/08:c5:e1:f1:fc:11/stats','r')
		input = input_file.readlines()
		input_file.close()

		dirs = listdir('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations')
		multi_airtime = 0
		other_station_msg = ""
		for d in dirs:
			if d == '08:c5:e1:f1:fc:11':
				continue
			path = '/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/'+d+'/stats'
			input_file2 = open(path,'r')
			input2 = input_file2.readlines()
			input_file2.close()
			multi_airtime += int(input2[9].split()[1])
			if d not in current_other_tx:
				current_other_tx[d] = 0
			other_station_msg = other_station_msg + " " + d + " " + str(int(input2[9].split()[1]) - current_other_tx[d])
			current_other_tx[d] = int(input2[9].split()[1])

		nss = input[0].split()[5]
		mcs_index = input[0].split()[6]
		if len(input[0].split()) == 8:
			GI = True
		else:
			GI = False
		msec = input[7].split()[1]
		data_len = int(input[8].split()[1])
		tx = int(input[9].split()[1])
		
		if msec != current_msec:
			new_data = data_len - current_data_len
			if GI:
				output = nss + " " + mcs_index + " SGI " + str(new_data)
			else:
				output = nss + " " + mcs_index + " GI " + str(new_data)

			output = output + " " + str(time_now - current_time) + " " + str(tx - current_tx)
			if(multi_device):
				output = output + " " + str(multi_airtime - current_multi_tx) + other_station_msg
				current_multi_tx = multi_airtime
			
			mqttc.publish(topic, output)
			current_time = time_now
			current_msec = msec
			current_data_len = data_len
			current_tx = tx
			print(output)
	except:
		continue
