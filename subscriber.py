import json
import paho.mqtt.client as mqtt

'''
bitrate= {"GI": {}, "SGI": {}}
bitrate["GI"] = {"MCS0": 29.3, "MCS1": 58.5, "MCS2": 87.8, "MCS3": 117.0, "MCS4": 175.5,
                         "MCS5": 234.0,"MCS6": 263.3, "MCS7": 292.5, "MCS8": 351.0, "MCS9": 390.0}
bitrate["SGI"] = {"MCS0": 32.5, "MCS1": 65.0, "MCS2": 97.5, "MCS3": 130.0, "MCS4": 195.0,
                         "MCS5": 260.0,"MCS6": 292.5, "MCS7": 325.0, "MCS8": 390.0, "MCS9": 433.3}
'''

# throughput of each rate from experiment
throughput = {"NSS1": {"GI": {}, "SGI": {}}, 
              "NSS2": {"GI": {}, "SGI": {}}}
throughput["NSS1"]["GI"] = {"MCS0": 24.7, "MCS1": 49.5, "MCS2": 74.75, "MCS3": 99.65, "MCS4": 147.0,
                            "MCS5": 195.5,"MCS6": 220.0, "MCS7": 244.0, "MCS8": 298.5, "MCS9": 326.0}
throughput["NSS1"]["SGI"] = {"MCS0": 27.4, "MCS1": 55.0, "MCS2": 82.25, "MCS3": 110.0, "MCS4": 160.5,
                             "MCS5": 217.0,"MCS6": 244.5, "MCS7": 268.5, "MCS8": 327.0, "MCS9": 359.5}

throughput["NSS2"]["GI"] = {"MCS0": 47.85, "MCS1": 96.7, "MCS2": 143.0, "MCS3": 181.0, "MCS4": 260.0,
                            "MCS5": 357.5,"MCS6": 390.5, "MCS7": 462.0, "MCS8": 537.0, "MCS9": 598.0}
throughput["NSS2"]["SGI"] = {"MCS0": 54.25, "MCS1": 109.5, "MCS2": 161.5, "MCS3": 216.0, "MCS4": 324.0,
                             "MCS5": 418.0,"MCS6": 458.0, "MCS7": 504.0, "MCS8": 580.5, "MCS9": 623.5}
 
multi_device = True
bw_1080 = 49    # required bandwidth for 1080p
bw_720 = 25     # required bandwidth for 720p
alpha = 1/4
history_airtime = -1
other_history_airtime = {}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("TESTING")

def on_message(client, userdata, msg):
    input = msg.payload.decode().split()
    nss = input[0]
    mcs_index = input[1]
    GI = input[2]
    data_len = float(input[3])
    interval = float(input[4])
    tx = float(input[5])
    global other_history_airtime
    sum_other = 0
    multi_tx = 0
    if(multi_device):
        multi_tx = float(input[6])
        for i in range(7,len(input),2):
            if input[i] not in other_history_airtime:
                other_history_airtime[input[i]] = float(input[i+1]) / (interval * 1000000)
            else:
                other_history_airtime[input[i]] = alpha * (float(input[i+1]) / (interval * 1000000)) + (1-alpha) * other_history_airtime[input[i]]
            sum_other += other_history_airtime[input[i]]

    global history_airtime
    max_throughput = throughput[nss][GI][mcs_index]
    airtime_percentage = tx / (interval * 1000000)
    multi_airtime = multi_tx / (interval * 1000000)

    # check if it is the first interval
    if history_airtime == -1:
        history_airtime = airtime_percentage
    else:
        # airtime(t) = a * measured_airtime(t) + (1-a) * airtime(t-1)
        history_airtime = alpha*airtime_percentage + (1-alpha)*history_airtime
    
    # divide the left airtime to devices by the percentage of current airtime
    if (history_airtime + multi_airtime) >=0.75 :        
        goodput = max_throughput * history_airtime
    else:
        left_airtime = 0.75 - (history_airtime + multi_airtime)
        partial = history_airtime / (history_airtime + multi_airtime)
        goodput = max_throughput * (history_airtime + left_airtime * partial)

    # decide the video rate
    if goodput > bw_1080:
        video_quality = "1080p"
    else:
        video_quality = "720p"
    output = {
        "quality" : video_quality
    }
    
    print(output)
    print(history_airtime, multi_airtime, history_airtime+multi_airtime)
    print(multi_airtime, sum_other)
    print(goodput)
    '''
    print("Current Rate: " + str((data_len * 8 / 1000000)/interval) + " Mbits/s")
    if(multi_device):
        print("Tx: " + str(tx))
        print("Tx percentage: " + str(( tx/ (interval * 1000000))*100) + "%")
        print("Tx_2: " + str(multi_tx))
        print("Tx_2 percentage: " + str(( multi_tx/ (interval * 1000000))*100) + "%")
        print("Tx_total percentage: " + str(( (tx + multi_tx)/ (interval * 1000000))*100) + "%")
    else:
        print("Tx: " + str(tx))
        print("Tx percentage: " + str(( tx/ (interval * 1000000))*100) + "%")
    '''
    print("-----------------------------------------------")
    
    '''
    try:
        input_file = open ('output.json','r')
        json_array = json.load(input_file)
        input_file.close()
        current_quality = json_array['quality']
        if current_quality != video_quality:
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