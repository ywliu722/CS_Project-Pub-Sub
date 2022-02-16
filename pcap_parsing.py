input_file=open('test.txt', 'r')
lines=input_file.readlines()
input_file.close()

last_ack=0
last_pkt=""
last_timestamp=0
fps=[]
frame=0

output_file = open('fps.txt', 'w')

for line in lines:
    tmp = line.split(',')
    ack_num=""
    timestamp = int(tmp[0].split()[0].split('.')[1])
    pkt_len = int(tmp[-1][:-1].split()[1])
    if pkt_len <= 0:
        continue
    if "ack" in tmp[1]:
        ack_num = int(tmp[1].split()[1])
    elif "ack" in tmp[2]:
        ack_num = int(tmp[2].split()[1])
    else:
        continue
    
    if last_ack != ack_num and last_pkt != "" :
        if timestamp < last_timestamp:
            fps.append(frame)
            output_file.write(f'{frame}\n')
            frame=1
        else:
            frame += 1
        last_timestamp=timestamp
        #print(last_pkt)

    last_ack = ack_num
    last_pkt=f'{timestamp} {ack_num}'
#print(last_pkt)
fps.append(frame)

output_file.write(f'{frame}\n')
output_file.close()