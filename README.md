# CS_Project-Pub-Sub

* Publisher on AP is to fetch the needed indexes from the driver of AP and send them to subscribers.
* Subscriber on edge system is to receive the data from publisher, calculate goodput and output the quality as JSON file in VR streaming server folder.

## Current Indexes
1. NSS (in float form)
2. MCS index
3. GI (Guard Interval)
4. Read interval (for calculating the percentage of airtime/interval)
5. Tx airtime of devices
