from threading import current_thread
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
current_second_tx = 0
second_device = True

while True:
	try:
		# read device 1
		input_file = open('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/08:c5:e1:f1:fc:11/stats','r')
		input = input_file.readlines()
		input_file.close()
		
		# read device 2
		if(second_device):
			input_file2 = open('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/48:45:20:98:d4:1a/stats','r')
			input2 = input_file2.readlines()
			input_file2.close()

		# busy waiting until reaching 1 second
		time_now = time.time()
		if time_now - current_time < 1 :
			continue

		nss = input[0].split()[5]
		mcs_index = input[0].split()[6]
		if len(input[0].split()) == 8:
			GI = True
		else:
			GI = False
		msec = input[7].split()[1]
		data_len = int(input[8].split()[1])
		tx = int(input[9].split()[1])
		if(second_device):
			second_tx = int(input2[9].split()[1])
		
		if msec != current_msec:
			new_data = data_len - current_data_len
			if GI:
				output = nss + " " + mcs_index + " SGI " + str(new_data)
			else:
				output = nss + " " + mcs_index + " GI " + str(new_data)

			output = output + " " + str(time_now - current_time) + str(tx - current_tx)
			if(second_device):
				output = output + " " + str(second_tx - current_second_tx)
				current_second_tx = second_tx
			
			mqttc.publish(topic, output)
			current_time = time_now
			current_msec = msec
			current_data_len = data_len
			current_tx = tx
			print(output)
	except:
		continue
