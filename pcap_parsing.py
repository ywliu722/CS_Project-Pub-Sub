'''
This script is mainly used to parsing the pcap file output to get the fps of each time interval.

First, we get the pcap file output using: $tcpdump -r <pcap_file> -ttttt tcp port 7777 > <tcpdump_output>,
or we can just get the output rather than store the pcap file first.
-ttttt argument for timestamp using delta between each packet and the first packet
tcp port 7777 argument for VR client side port


Then, using this script to get the fps in each time interval.
Usage: $python3 pcap_parsing <tcpdump_output> <fps_output>
'''
import sys

if len(sys.argv) != 3:
    print(f'Usage: $python3 {sys.argv[0]} <tcpdump_output> <fps_output>')
    exit(1)

input_file=open(sys.argv[1], 'r')
lines=input_file.readlines()
input_file.close()

last_ack = -1
last_timestamp = 0
frame = 0

output_file = open(sys.argv[2], 'w')

for line in lines:
    tmp = line.split(',')
    ack_num = 0
    timestamp = int(tmp[0].split()[0].split('.')[1])
    print(timestamp)
    pkt_len = int(tmp[-1][:-1].split()[1])
    print(pkt_len)
    if pkt_len <= 0:
        continue
    if "ack" in tmp[1]:
        ack_num = int(tmp[1].split()[1])
    elif "ack" in tmp[2]:
        ack_num = int(tmp[2].split()[1])
    else:
        continue
    
    if last_ack != ack_num and last_ack != -1 :
        if timestamp < last_timestamp:
            output_file.write(f'{frame}\n')
            frame = 1
        else:
            frame += 1
        last_timestamp = timestamp

    last_ack = ack_num

output_file.write(f'{frame}\n')
output_file.close()