from os import listdir, path
import time
import paho.mqtt.client as mqtt

serviceIP = "192.168.1.66"
servicePort = 1883
target_MAC = 'de:cc:1e:23:fe:98'
topic = "TESTING"

mqttc = mqtt.Client("python_pub")
mqttc.connect(serviceIP, servicePort)

current_data_len = 0
current_time = 0.0
current_tx = 0
current_other_tx = {}

while True:
	try:
		# busy waiting until reaching 1 second
		time_now = time.time()
		if time_now - current_time < 1 :
			continue

		# read target device
		target_file = f'/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/{target_MAC}/stats'
		input_file = open(target_file,'r')
		input = input_file.readlines()
		input_file.close()

		# read other device
		dirs = listdir('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations')
		other_station_msg = ""
		for d in dirs:
			# check if the current station is device 1 or not
			if d == target_file:
				continue

			# read device stats
			path = f'/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/{d}/stats'
			input_file2 = open(path,'r')
			input2 = input_file2.readlines()
			input_file2.close()

			# check if the device is connected for the first time
			if d not in current_other_tx:
				current_other_tx[d] = 0
			
			# record the MAC address, the airtime and store it in dict
			other_station_msg = other_station_msg + " " + d + " " + str(int(input2[9].split()[1]) - current_other_tx[d])
			current_other_tx[d] = int(input2[9].split()[1])

		# process stats of target device
		nss = input[0].split()[5]
		mcs_index = input[0].split()[6]
		if len(input[0].split()) == 8:
			GI = "SGI"
		else:
			GI = "GI"
		data_len = int(input[8].split()[1])
		tx = int(input[9].split()[1])
		new_data = data_len - current_data_len

		output = f'{nss} {mcs_index} {GI} {str(new_data)} {str(time_now - current_time)} {str(tx - current_tx)}'
		#output = nss + " " + mcs_index + " " + GI
		#output = output + " " + str(new_data) + " " + str(time_now - current_time) + " " + str(tx - current_tx)
		output = output + other_station_msg
		
		# publish the message to MQTT broker
		mqttc.publish(topic, output)
		
		# store the current information
		current_data_len = data_len
		current_time = time_now
		current_tx = tx
		print(output)
	except:
		continue