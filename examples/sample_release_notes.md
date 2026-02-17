---
title: "ECG2 VECU Release Notes"
version: "1.0.0"
date: "2026-02-17"
author: "Virtual ECU Engineering Team"
confidentiality: "Ford Confidential"
document_number: "VECU-RN-001"
revision: "A"
---

# ECG2 VECU Release Notes

## Overview

This document contains the release notes for the ECG2 Virtual Electronic Control Unit (VECU) software release version 1.0.0. The VECU provides a simulation environment for automotive embedded software development and testing.

## Release Information

| Field | Value |
|-------|-------|
| Release Version | 1.0.0 |
| Release Date | February 17, 2026 |
| Platform | Linux x86_64 |
| Build Number | 20260217.001 |

## New Features

### Hardware Abstraction Layer

The new Hardware Abstraction Layer (HAL) provides improved support for:

- CAN bus communication interfaces
- LIN bus protocol support
- Ethernet AVB/TSN networking
- GPIO simulation with timing accuracy

### Memory Management

Enhanced memory management features include:

1. Dynamic memory allocation tracking
2. Memory protection unit (MPU) emulation
3. Cache simulation for performance analysis
4. DMA controller support

## Bug Fixes

| Issue ID | Description | Severity |
|----------|-------------|----------|
| VECU-1234 | Fixed CAN message timing inconsistency | High |
| VECU-1256 | Resolved memory leak in diagnostic module | Medium |
| VECU-1278 | Corrected SPI clock phase configuration | Medium |
| VECU-1299 | Fixed watchdog timer reset behavior | High |

## Known Issues

The following issues are known in this release:

- **VECU-1350**: Ethernet TSN synchronization may have up to 10μs jitter under heavy load
- **VECU-1367**: USB device enumeration takes longer than expected on first connection
- **VECU-1389**: PWM frequency accuracy limited to 0.1% at frequencies above 100kHz

## System Requirements

### Minimum Requirements

- Operating System: Ubuntu 22.04 LTS or later
- CPU: x86_64 with SSE4.2 support
- RAM: 8 GB minimum
- Disk Space: 20 GB free space

### Recommended Requirements

- Operating System: Ubuntu 24.04 LTS
- CPU: x86_64 with AVX2 support, 8+ cores
- RAM: 32 GB
- Disk Space: 100 GB SSD

## Installation

### Prerequisites

Before installing, ensure the following dependencies are installed:

```bash
sudo apt update
sudo apt install build-essential cmake libboost-all-dev
```

### Installation Steps

1. Extract the release package
2. Run the installation script
3. Configure environment variables
4. Verify installation

## API Changes

### Deprecated APIs

The following APIs are deprecated and will be removed in version 2.0:

| API | Replacement | Notes |
|-----|-------------|-------|
| `vecu_init_v1()` | `vecu_init()` | Use new initialization API |
| `can_send_raw()` | `can_send_message()` | Improved type safety |
| `gpio_set_fast()` | `gpio_set()` | Unified GPIO interface |

### New APIs

- `vecu_init()` - New unified initialization function
- `can_send_message()` - Type-safe CAN transmission
- `lin_schedule_table()` - LIN schedule management
- `eth_tsn_configure()` - TSN stream configuration

## Performance Improvements

Performance benchmarks compared to previous release:

| Metric | v0.9.0 | v1.0.0 | Improvement |
|--------|--------|--------|-------------|
| CAN throughput | 5,000 msg/s | 8,500 msg/s | +70% |
| Boot time | 12.5s | 4.2s | -66% |
| Memory usage | 2.1 GB | 1.4 GB | -33% |
| CPU utilization | 85% | 62% | -27% |

## Documentation

The following documentation is included with this release:

- User Guide (PDF)
- API Reference (HTML)
- Integration Manual (PDF)
- Quick Start Guide (PDF)

## Support

For technical support, please contact:

- Email: vecu-support@example.com
- Issue Tracker: https://issues.example.com/vecu
- Documentation: https://docs.example.com/vecu

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-02-17 | Engineering Team | Initial release |
| 0.9.0 | 2026-01-15 | Engineering Team | Beta release |
| 0.8.0 | 2025-12-01 | Engineering Team | Alpha release |
