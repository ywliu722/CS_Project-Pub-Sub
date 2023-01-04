tcpdump -r ~/output.pcap -ttttt > output.txt
python3 pcap_parsing.py output.txt fps.txt
rm output.txt
