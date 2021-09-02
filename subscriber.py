import json
import paho.mqtt.client as mqtt

packet_size = 1470
bitrate= {"GI": {}, "SGI": {}}
bitrate["GI"] = {"MCS0": 29.3, "MCS1": 58.5, "MCS2": 87.8, "MCS3": 117.0, "MCS4": 175.5,
                         "MCS5": 234.0,"MCS6": 263.3, "MCS7": 292.5, "MCS8": 351.0, "MCS9": 390.0}
bitrate["SGI"] = {"MCS0": 32.5, "MCS1": 65.0, "MCS2": 97.5, "MCS3": 130.0, "MCS4": 195.0,
                         "MCS5": 260.0,"MCS6": 292.5, "MCS7": 325.0, "MCS8": 390.0, "MCS9": 433.3}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("TESTING")

def on_message(client, userdata, msg):
    input = msg.payload.decode().split()
    nss = float(input[0][3])
    mcs_index = input[1]
    ppdu_rate = float(input[2])
    GI = input[3]
    interval = int(input[4])
    success = int(input[5])
    ppdu_cnt = int(input[6])
    physical_rate = bitrate[GI][mcs_index] * (100 - ppdu_rate) * 0.01 * nss
    current_rate = ( float(ppdu_cnt * success * packet_size)  / (float(interval) / 1000) ) * 8
    output = {
        "NSS" : nss,
        "MCS" : mcs_index,
        "PPDU" : ppdu_rate,
        "GI" : GI,
        "Interval" : interval,
        "Success" : success,
        "PPDU Count" : ppdu_cnt
    }
    #print(output)
    #print("Physical Rate: " + str(physical_rate))
    print("Current Rate: " + str(current_rate / 1000000) + " Mbits/s")
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