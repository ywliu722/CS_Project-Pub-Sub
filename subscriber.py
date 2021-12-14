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
bw_900 = 33     # required bandwidth for 900p
bw_720 = 25     # required bandwidth for 720p
bw_540 = 10     # required bandwidth for 540p
bw_360 = 2.5    # required bandwidth for 360p
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
    interval = float(input[3])
    tx = float(input[4])
    global other_history_airtime
    sum_other = 0
    other=[]
    n_device = 1 + (len(input) - 5)/2
    if(multi_device):
        for i in range(5,len(input),2):
            # check the value is correct or not
            if float(input[i+1]) / (interval * 1000000) < 0 or float(input[i+1]) / (interval * 1000000) > 1:
                continue
            # check if the device is connected for the first time
            if input[i] not in other_history_airtime:
                other_history_airtime[input[i]] = float(input[i+1]) / (interval * 1000000)
            else:
                other_history_airtime[input[i]] = alpha * (float(input[i+1]) / (interval * 1000000)) + (1-alpha) * other_history_airtime[input[i]]
            # sum up all the other devices' moving average of airtime percentage
            sum_other += other_history_airtime[input[i]]
            other.append(other_history_airtime[input[i]])

    global history_airtime
    max_throughput = throughput[nss][GI][mcs_index]
    airtime_percentage = tx / (interval * 1000000)

    # check if it is the first interval
    if history_airtime == -1:
        history_airtime = airtime_percentage
    else:
        # airtime(t) = a * measured_airtime(t) + (1-a) * airtime(t-1)
        history_airtime = alpha*airtime_percentage + (1-alpha)*history_airtime
    
    # divide the left airtime to devices by the percentage of current airtime
    if (history_airtime + sum_other) >=0.75 :        
        goodput = max_throughput * history_airtime

    # other devices use exceeded to their fairness part
    elif sum_other > 0.75 * ( ( n_device -1 ) / n_device):
        goodput = max_throughput * (0.75-sum_other) # make sure that we get the best quality
    else:
        exceed = 0
        for air in other:
            if air > 0.75 * (1/n_device):
                exceed += air
        exceed += history_airtime
        # distribute the left airtime to those devices that use airtime exceeded their fairness part
        goodput = max_throughput * ( 0.75*(1/n_device) + (0.75-sum_other)*(history_airtime/exceed) )


    # decide the video rate
    if goodput > bw_1080:
        video_quality = "1080p"
    elif goodput > bw_900:
        video_quality = "900p"
    elif goodput > bw_720:
        video_quality = "720p"
    else:
        video_quality = "540p"

    output = {
        "quality" : video_quality
    }
    
    '''
    output_data=open('output.txt', 'a')
    output_data.write(f'{nss} {mcs_index} {GI} {history_airtime} {sum_other} {video_quality}\n')
    print(f'{nss} {mcs_index} {GI} {history_airtime} {sum_other} {video_quality}')
    '''

    print(output)
    print(n_device)
    print(history_airtime, sum_other, history_airtime+sum_other)
    print(goodput)
    print("-----------------------------------------------")


    # output the quality
    try:
        input_file = open ('/home/ywliu722/LinusTrinus/test.json','r')
        json_array = json.load(input_file)
        input_file.close()
        current_quality = json_array['quality']
        if current_quality != video_quality:
            output_file = open("/home/ywliu722/LinusTrinus/test.json","w")
            json.dump(output, output_file)
            output_file.close()
    except:
        pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.238", 1883, 60)
client.loop_forever()