import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("TESTING")

def on_message(client, userdata, msg):
    input = msg.payload.decode().split()
    mcs_index = input[0]
    ppdu_rate = float(input[1])
    output = {
        "MCS" : mcs_index,
        "PPDU" : ppdu_rate
    }
    try:
        output_file = open("output.json","w")
        json.dump(output, output_file)
        output_file.close()
        print(output)
    except:
        pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.15", 1883, 60)
client.loop_forever()