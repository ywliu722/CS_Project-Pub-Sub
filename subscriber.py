import json
import paho.mqtt.client as mqtt

# theoratical bitrate of each rate
bitrate = {"NSS1": {"GI": {}, "SGI": {}}, 
              "NSS2": {"GI": {}, "SGI": {}}}
bitrate["NSS1"]["GI"] = {"MCS0": 29.3, "MCS1": 58.5, "MCS2": 87.8, "MCS3": 117.0, "MCS4": 175.5,
                            "MCS5": 234.0,"MCS6": 263.3, "MCS7": 292.5, "MCS8": 351.0, "MCS9": 390}
bitrate["NSS1"]["SGI"] = {"MCS0": 32.5, "MCS1": 65.0, "MCS2": 97.5, "MCS3": 130.0, "MCS4": 195.0,
                             "MCS5": 260.0,"MCS6": 292.5, "MCS7": 325.0, "MCS8": 390.0, "MCS9": 433.3}

bitrate["NSS2"]["GI"] = {"MCS0": 58.5, "MCS1": 117.0, "MCS2": 175.5, "MCS3": 234.0, "MCS4":351.0,
                            "MCS5": 468.0,"MCS6": 526.5, "MCS7": 585.0, "MCS8": 702.0, "MCS9": 780.0}
bitrate["NSS2"]["SGI"] = {"MCS0": 65.0, "MCS1": 130.0, "MCS2": 195.0, "MCS3": 260.0, "MCS4": 390.0,
                             "MCS5": 520.0,"MCS6": 585.0, "MCS7": 650.0, "MCS8": 780.0, "MCS9": 866.7}

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
bw_1080 = 60    # required bandwidth for 1080p
bw_900 = 40     # required bandwidth for 900p
bw_720 = 30     # required bandwidth for 720p
bw_540 = 20     # required bandwidth for 540p
bw_360 = 10    # required bandwidth for 360p
alpha = 1/2
max_airtime = 0.6
min_airtime = 0.4
history_airtime = -1
other_history_airtime = {}

last_delta_per = 0.0    # delta between current throughput and required bandwidth
last_slope = 0.0        # slope of two delta
current_require_bw = 60
startup = True

bw_meet_threshold = 0.9

output_path = '/home/nems/yw/CS_Project-Linux_Trinus/test.json'

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("TESTING")

def on_message(client, userdata, msg):
    global history_airtime
    global other_history_airtime
    global max_airtime
    global last_delta_per, last_slope
    global current_require_bw
    global startup

    # parsing the received message
    input = msg.payload.decode().split()
    nss = input[0]
    mcs_index = input[1]
    GI = input[2]
    data_len = float(input[3])
    interval = float(input[4])
    tx = float(input[5])
    
    total_airtime = 0.0
    sum_other = 0
    other=[]
    airtime_list="" # every airtime percentage
    moving_airtime_list=""
    n_device = 1 + (len(input) - 6)/2
    if(multi_device):
        for i in range(6,len(input),2):
            # check the value is correct or not
            if float(input[i+1]) / (interval * 1000000) < 0 or float(input[i+1]) / (interval * 1000000) > 1:
                continue

            # sum up the total used airtime
            total_airtime += (float(input[i+1]) / (interval * 1000000))

            # check if the device is connected for the first time
            if input[i] not in other_history_airtime:
                other_history_airtime[input[i]] = float(input[i+1]) / (interval * 1000000)
            else:
                other_history_airtime[input[i]] = alpha * (float(input[i+1]) / (interval * 1000000)) + (1-alpha) * other_history_airtime[input[i]]
            # sum up all the other devices' moving average of airtime percentage
            sum_other += other_history_airtime[input[i]]
            other.append(other_history_airtime[input[i]])
            airtime_list = airtime_list + " " + str(float(input[i+1]) / (interval * 1000000)) # every airtime percentage
            moving_airtime_list = moving_airtime_list + " " + str(other_history_airtime[input[i]]) # every moving average of airtime percentage

    current_throughput = (data_len * 8 / 1000000) / interval

    
    max_throughput = throughput[nss][GI][mcs_index]
    airtime_percentage = tx / (interval * 1000000)
    total_airtime += airtime_percentage
    airtime_list = str(airtime_percentage) + airtime_list # every airtime percentage
    # check if it is the first interval
    if history_airtime == -1:
        history_airtime = airtime_percentage
    else:
        # airtime(t) = a * measured_airtime(t) + (1-a) * airtime(t-1)
        history_airtime = alpha*airtime_percentage + (1-alpha)*history_airtime
    
    moving_airtime_list = str(history_airtime) + moving_airtime_list # every airtime percentage

    # divide the left airtime to devices by the percentage of current airtime
    if (history_airtime + sum_other) >= max_airtime :        
        goodput = max_throughput * ( max_airtime - sum_other)

    # other devices use exceeded to their fairness part
    elif sum_other > max_airtime * ( ( n_device -1 ) / n_device):
        goodput = max_throughput * ( max_airtime - sum_other) # make sure that we get the best quality
    else:
        exceed = 0
        for air in other:
            if air > max_airtime * (1/n_device):
                exceed += air
        if history_airtime > max_airtime * (1/n_device):
            exceed += history_airtime
        # distribute the left airtime to those devices that use airtime exceeded their fairness part
        if exceed == 0: # if there is no device exceeds their own fairness part, then every device get the same airtime
            goodput = max_throughput * ( max_airtime * (1/n_device))
        else:   # if there is any device exceeds the fairness part, then evenly distribute the last airtime to those exceeded devices
            goodput = max_throughput * ( max_airtime * (1/n_device) + (max_airtime - sum_other - history_airtime)*(history_airtime/exceed) )

    ## [proactive part]
    current_delta_per = (current_throughput - current_require_bw) / current_require_bw
    current_slope = current_delta_per - last_delta_per
    if last_slope > current_slope and current_delta_per < 0:
        goodput = current_throughput * 0.9
    last_delta_per = current_delta_per
    last_slope = current_slope

    ## [reactive part]
    # modify the quality to lower one if the current throughput does not meet the requirement
    if current_throughput < current_require_bw * bw_meet_threshold and not startup and total_airtime > min_airtime:
        goodput = current_throughput
        max_airtime = total_airtime

    # if the current throughput meets the requirement and if the total used airtime is more than max_airtime, then let the total airtime be the max_airtime
    # this might need some modification
    ## [TODO]
    elif current_throughput > current_require_bw * bw_meet_threshold and total_airtime > max_airtime:
        max_airtime = total_airtime

    if startup and current_throughput > 1.0:
        startup = False

    # decide the video rate
    if goodput > bw_1080:
        video_quality = "1080p"
        current_require_bw = bw_1080
    elif goodput > bw_900:
        video_quality = "900p"
        current_require_bw = bw_900
    elif goodput > bw_720:
        video_quality = "720p"
        current_require_bw = bw_720
    elif goodput > bw_540:
        video_quality = "540p"
        current_require_bw = bw_540
    else:
        video_quality = "360p"
        current_require_bw = bw_360

    output = {
        "quality" : video_quality
    }
    
    
    # for output airtime
    output_airtime=open('airtime.txt', 'a')
    output_airtime.write(f'{video_quality} {bitrate[nss][GI][mcs_index]} {airtime_list}\n')
    output_airtime.close()

    '''
    output_moving = open('moving.txt', 'a')
    output_moving.write(f'{video_quality} {moving_airtime_list}\n')
    output_moving.close()
    '''

    output_throughput = open('throughput.txt', 'a')
    output_throughput.write(f'{video_quality} {current_throughput}\n')
    output_throughput.close()


    print(output)    
    print(history_airtime, sum_other, history_airtime+sum_other)
    print(f'Total used airtime: {total_airtime}')
    print(f'Maximum airtime: {max_airtime}')
    print(f'Current throughput: {current_throughput}')
    print(f'Goodput: {goodput}')
    print("-----------------------------------------------")

    
    # output the quality
    try:
        
        input_file = open (output_path,'r')
        json_array = json.load(input_file)
        input_file.close()
        current_quality = json_array['quality']
        if current_quality != video_quality:
            output_file = open(output_path,"w")
            json.dump(output, output_file)
            output_file.close()
        
    except:
        pass
    

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.66", 1883, 60)
client.loop_forever()
