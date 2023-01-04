'''
    THIS SCRIPT IS USED TO COLLECT NETWORK TRACE WHICH IS USED TO TRAIN THE MACHINE LEARNING MODEL.
    YOU WILL NEED TO RUN 'publisher.py' ON WIFI AP FIRST.
    IT WILL OUTPUT THE FOLLOWING INFORMATION:
    * NSS                               ([1, 2])
    * MCS                               ([0, 9])
    * GI                                (0: GI, 1: SGI)
    * THORUGHPUT                        (in Mbps)
    * AIRTIME_PERCENTAGE                (in percentage [0.0, 1.0])
    * OTHER_DEVICE_AIRTIME_PERCENTAGE   (in percentage [0.0, 1.0])
'''
import sys
import paho.mqtt.client as mqtt

MQTT_PORT = 1883

SEC_TO_US = 1000000
BYTE_TO_BITS = 8
BITS_TO_MEGA = 1024 * 1024

OUTPUT_PATH = 'network_trace.txt'
index = 0

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("TESTING")

def on_message(client, userdata, msg):
    global index
    # record the other device airtime
    other_device_airtime_per = 0.0  # in percentage

    # parsing the received message
    input = msg.payload.decode().split()
    nss = input[0]
    mcs_index = input[1]
    guard_interval = input[2]
    data_len = float(input[3])      # in bytes
    interval = float(input[4])      # in second
    tx_airtime = float(input[5])    # in micro-second

    # parsing GI
    GI_in_num = 0
    if(guard_interval == "SGI"):
        GI_in_num = 1
    else:
        GI_in_num = 0

    throughput = (data_len * BYTE_TO_BITS) / BITS_TO_MEGA   # in Mbps
    airtime_per = tx_airtime / (interval * SEC_TO_US)       # in percentage

    # parsing other device's airtime
    for i in range(6,len(input),2):
        current_device_airtime_per = float(input[i+1]) / (interval * SEC_TO_US)
        # check the value is correct or not
        if current_device_airtime_per < 0 or current_device_airtime_per > 1:
            continue

        # sum up the total used airtime
        other_device_airtime_per += current_device_airtime_per

    # output to file
    output=open(OUTPUT_PATH, 'a')
    output.write(f'{nss[3]} {mcs_index[3]} {GI_in_num} {throughput} {airtime_per} {other_device_airtime_per}\n')
    output.close()

    # output the current state to stdout
    print(f'#{index}')
    print(f'{nss} {mcs_index} {guard_interval}')
    print(f'Throughput: {throughput} Mbps')
    print(f'Airtime: {airtime_per}')
    print(f'Other Device: {other_device_airtime_per}')
    print("-----------------------------------------------")
    index += 1

def main():
    if len(sys.argv) != 2:
        print(f'Usage: $ python3 {sys.argv[0]} <broker IP>')
        return
    
    brokerIP = sys.argv[1]
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(brokerIP, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main() 