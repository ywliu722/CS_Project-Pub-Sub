# Rate-Aware Video Streaming: Decision Module (MQTT Pub-Sub)

> An MQTT pub-sub module that estimates per-station goodput from live Wi-Fi rate
> info and selects the best sustainable streaming quality, on a Wi-Fi
> edge-computing platform.

## Background

The decision module of a **solo** undergraduate CS capstone on *proactive
radio-aware adaptation for VR video streaming*. The companion driver
([CS_Project-openwrt-mt7915-csi](https://github.com/ywliu722/CS_Project-openwrt-mt7915-csi))
publishes per-station rate info from the router over MQTT; this module
subscribes, estimates achievable goodput, and tells the
[streaming server](https://github.com/ywliu722/CS_Project-Linux_Trinus) what
quality to serve — before congestion causes a stall.

## What This Does

- **Subscribes** (MQTT) to per-station rate info from the router: MCS index, NSS,
  guard interval, bandwidth, airtime
- **Estimates goodput**: from Wi-Fi airtime-fairness, derives the station's max
  usable airtime, multiplies its airtime-occupancy ratio by the peak rate for the
  current Tx rate → live goodput estimate
- **Selects quality**: maps goodput to the highest streaming quality it can
  sustain and publishes the choice to the streaming server
- Per-rate peak throughput and per-quality minimum rates were **measured
  experimentally** (iPerf3 with pinned `fixed_rate`; Wireshark throughput stats)

## Why MQTT

The router and the edge platform are separate machines, so the rate info has to
travel over the network. MQTT is lightweight and well-suited to embedded / IoT
messaging, which fits the router as the publisher and the decision module as the
subscriber. Broker: Mosquitto; client: paho-mqtt.

## Architecture

```
[Router] mt7915 debugfs stats ─► MQTT publisher ──┐ (MQTT)
                                                   ▼
                                 [Edge] Decision module (subscriber)
                                 goodput estimate ─► best quality
                                                   │ (publish)
                                                   ▼
                                 LinusTrinus streaming server
```

## Tech Stack

- **Messaging:** MQTT (paho-mqtt + Mosquitto broker)
- **Language:** Python 3.9
- **Runs on:** edge platform (Ubuntu 20.04 PC) ↔ OpenWrt router

## What I Learned

- Designing a real-time sensing → decision pipeline under latency constraints
- Why a lightweight pub-sub protocol (MQTT) fits embedded / IoT messaging
- Turning an airtime-fairness model into a measured, working goodput estimator

## Status

Solo undergraduate capstone (2021–22). Demonstrated with a real VR streaming
workload — [demo video](https://www.youtube.com/watch?v=0c7IfljchAo).
