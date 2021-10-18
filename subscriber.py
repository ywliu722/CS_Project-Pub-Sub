import json
import paho.mqtt.client as mqtt

'''
bitrate= {"GI": {}, "SGI": {}}
bitrate["GI"] = {"MCS0": 29.3, "MCS1": 58.5, "MCS2": 87.8, "MCS3": 117.0, "MCS4": 175.5,
                         "MCS5": 234.0,"MCS6": 263.3, "MCS7": 292.5, "MCS8": 351.0, "MCS9": 390.0}
bitrate["SGI"] = {"MCS0": 32.5, "MCS1": 65.0, "MCS2": 97.5, "MCS3": 130.0, "MCS4": 195.0,
                         "MCS5": 260.0,"MCS6": 292.5, "MCS7": 325.0, "MCS8": 390.0, "MCS9": 433.3}
'''

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("TESTING")

def on_message(client, userdata, msg):
    input = msg.payload.decode().split()
    nss = float(input[0][3])
    mcs_index = input[1]
    GI = input[2]
    data_len = float(input[3])
    airtime = int(input[4]) + int(input[5]) + int(input[6]) + int(input[7])
    #airtime2 = int(input[8]) + int(input[9]) + int(input[10]) + int(input[11])
    #interval = float(input[12])
    interval = float(input[8])
    send_tx = float(input[9])
    ack_tx = float(input[10])

    output = {
        "NSS" : nss,
        "MCS" : mcs_index,
        "GI" : GI,
        "Data Length": data_len
    }
    #print(output)
    print("Current Rate: " + str((data_len * 8 / 1000000)/interval) + " Mbits/s")
    #print("Airtime: " + str(airtime) + " " + str(airtime2))
    print("Airtime: " + str(airtime))
    print("Airtime percentage: " + str(( airtime/ (interval * 1000000))*100) + "%")
    #print("Airtime percentage: " + str(( airtime2/ (interval * 1000000))*100) + "%\n")
    #print("Total airtime: " + str(airtime + airtime2))
    #print("Total Airtime percentage: " + str(( (airtime + airtime2)/ (interval * 1000000))*100) + "%")
    print("Send Tx time: " + str(send_tx))
    print("Ack Tx time: " + str(ack_tx))
    print("-----------------------------------------------")
    '''
    try:
        output_file = open("output.json","w")
        json.dump(output, output_file)
        output_file.close()
        print(output)
    except:
        pass
    '''

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.148", 1883, 60)
client.loop_forever()