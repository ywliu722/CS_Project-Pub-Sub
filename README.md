# OpenWrt MT7915 Rate-Info Driver Extension

> A modified OpenWrt mt76/mt7915 driver that exposes per-station Wi-Fi rate
> information — MCS, MIMO mode, bandwidth, and transmit airtime — via debugfs,
> feeding a rate-aware video-streaming adaptation system.

## Background

The driver layer of a **solo** undergraduate CS capstone on *proactive
radio-aware quality adaptation for VR video streaming over a Wi-Fi
edge-computing platform*. Rather than reacting to application-layer stalls after
they happen, the system reads link-layer rate info from the router and adjusts
streaming quality **before** the channel degrades the experience.

The metrics extracted here feed the
[decision module](https://github.com/ywliu722/CS_Project-Pub-Sub).

## What This Does

- Extends the MediaTek **mt7915** driver (mt76) to surface per-station rate info
  through the debugfs `stats` file: MCS index, MIMO mode, bandwidth
- **Adds transmit airtime**, which the driver did not expose: traced the
  TX-completion path (`mt7915_tx_complete_status` →
  `struct ieee80211_tx_status.info->tx_time_est`), cached it in
  `struct mt7915_sta`, and emitted it from `mt7915_sta_stats_read`
- Patched firmware/driver to fix a guard-interval control issue so a fixed Tx
  rate could be pinned via debugfs `fixed_rate` for controlled measurements

## Tech Stack

- **Platform:** OpenWrt 21.02
- **Hardware:** BPI-R64 — MediaTek MT7622 SoC + MT7915 NIC (802.11ax-capable; run in 802.11ac for this project)
- **Driver base:** mt76 (mainline Linux Wi-Fi driver for MediaTek chips)
- **Languages:** C (driver), Shell (build / flash)
- **Flashing:** OpenWrt buildroot image written over TFTP + U-Boot / Minicom

## Pipeline

```
MT7915 NIC ─► mt76/mt7915 driver ─► debugfs `stats` (MCS, MIMO, BW, +airtime)
                                          │
                                          ▼
                                MQTT publisher (on router)
                                          │
                                          ▼
                          Decision module on edge platform
```

## Related Repos

- [CS_Project-Pub-Sub](https://github.com/ywliu722/CS_Project-Pub-Sub) — MQTT decision module that consumes this rate info
- [CS_Project-Linux_Trinus](https://github.com/ywliu722/CS_Project-Linux_Trinus) — the VR streaming server that acts on the decisions

## What I Learned

- Linux Wi-Fi driver internals (mt76) and the mac80211 TX-status path
- debugfs as a kernel → userspace telemetry interface
- Modifying a vendor driver inside the OpenWrt build system

## Status

Solo undergraduate capstone (2021–22). Working prototype, validated with a real
VR streaming workload. Not actively maintained.
