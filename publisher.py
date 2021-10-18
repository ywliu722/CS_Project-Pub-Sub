from threading import current_thread
import time
import paho.mqtt.client as mqtt

serviceIP = "192.168.1.148"
servicePort = 1883
topic = "TESTING"

mqttc = mqtt.Client("python_pub")
mqttc.connect(serviceIP, servicePort)

current_msec = "0"
current_data_len = "0"
current_time = 0.0
airtime = [0,0,0,0]
current_airtime = [0,0,0,0]
airtime2 = [0,0,0,0]
current_airtime2 = [0,0,0,0]

while True:
	try:
		input_file = open('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/08:c5:e1:f1:fc:11/stats','r')
		#input_file = open('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/48:45:20:98:d4:1a/stats','r')
		input = input_file.readlines()
		input_file.close()
		'''
		input_file2 = open('/sys/kernel/debug/ieee80211/phy0/netdev:wlan0/stations/48:45:20:98:d4:1a/stats','r')
		input2 = input_file2.readlines()
		input_file2.close()
		'''
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
		data_len = input[8].split()[1]
		airtime[0] = int(input[9].split()[2])
		airtime[1] = int(input[10].split()[2])
		airtime[2] = int(input[11].split()[2])
		airtime[3] = int(input[12].split()[2])
		'''
		airtime2[0] = int(input2[9].split()[2])
		airtime2[1] = int(input2[10].split()[2])
		airtime2[2] = int(input2[11].split()[2])
		airtime2[3] = int(input2[12].split()[2])
		'''
		send_tx_time = input[21].split()[2]
		ack_tx_time = input[22].split()[2]
		
		if msec != current_msec:
			new_data = int(data_len) - int(current_data_len)
			if GI:
				output = nss + " " + mcs_index + " SGI " + str(new_data)
			else:
				output = nss + " " + mcs_index + " GI " + str(new_data)
			for i in range(4):
				output = output + " " + str(airtime[i] - current_airtime[i])
				current_airtime[i] = airtime[i]
			'''
			for i in range(4):
				output = output + " " + str(airtime2[i] - current_airtime2[i])
				current_airtime2[i] = airtime2[i]
			'''
			output = output + " " + str(time_now - current_time)
			output = output + " " + send_tx_time + " " + ack_tx_time
			mqttc.publish(topic, output)
			current_time = time_now
			current_msec = msec
			current_data_len = data_len
			print(output)
	except:
		continue
