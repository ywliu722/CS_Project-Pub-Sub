import json
import paho.mqtt.client as mqtt

'''
bitrate= {"GI": {}, "SGI": {}}
bitrate["GI"] = {"MCS0": 29.3, "MCS1": 58.5, "MCS2": 87.8, "MCS3": 117.0, "MCS4": 175.5,
                         "MCS5": 234.0,"MCS6": 263.3, "MCS7": 292.5, "MCS8": 351.0, "MCS9": 390.0}
bitrate["SGI"] = {"MCS0": 32.5, "MCS1": 65.0, "MCS2": 97.5, "MCS3": 130.0, "MCS4": 195.0,
                         "MCS5": 260.0,"MCS6": 292.5, "MCS7": 325.0, "MCS8": 390.0, "MCS9": 433.3}
'''
second_device = True

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("TESTING")

def on_message(client, userdata, msg):
    input = msg.payload.decode().split()
    nss = float(input[0][3])
    mcs_index = input[1]
    GI = input[2]
    data_len = float(input[3])
    interval = float(input[4])
    tx = float(input[5])
    if(second_device):
        second_tx = float(input[6])

    output = {
        "NSS" : nss,
        "MCS" : mcs_index,
        "GI" : GI,
        "Data Length": data_len
    }
    #print(output)
    print("Current Rate: " + str((data_len * 8 / 1000000)/interval) + " Mbits/s")
    if(second_device):
        print("Tx: " + str(tx))
        print("Tx percentage: " + str(( tx/ (interval * 1000000))*100) + "%")
        print("Tx_2: " + str(second_tx))
        print("Tx_2 percentage: " + str(( second_tx/ (interval * 1000000))*100) + "%")
        print("Tx_total percentage: " + str(( (tx + second_tx)/ (interval * 1000000))*100) + "%")
    else:
        print("Tx: " + str(tx))
        print("Tx percentage: " + str(( tx/ (interval * 1000000))*100) + "%")
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