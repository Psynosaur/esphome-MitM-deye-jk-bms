# 🔌 ESPHome MitM Deye

[![ESPHome](https://img.shields.io/badge/ESPHome-Compatible-blue?logo=esphome)](https://esphome.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ESP32-C6](https://img.shields.io/badge/ESP32-C6-red?logo=espressif)](https://www.espressif.com/en/products/socs/esp32-c6)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-blue?logo=home-assistant)](https://www.home-assistant.io/)

**Man In The Middle Adapter for Deye Communication Protocol**

> 🙏 **Special Thanks**: This project is a detached fork based on the excellent work by [**Adminius**](https://github.com/Adminius/mitpylon). The original concept and implementation foundation were created by Adminius, and this project builds upon that solid foundation with additional features and enhancements.

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK!**

This software modifies critical battery management communication. The author is not responsible for any damage to equipment, property, or injury that may result from using this software. Ensure you understand the implications before deployment.

## 🎯 Overview

The Deye BMS communication protocol has limitations - it doesn't allow dynamic charge voltage settings (fixed at 58.4V). This ESPHome-based solution intercepts and modifies CAN bus messages between your BMS and Deye inverter, providing enhanced control capabilities.

### 🔧 Key Capabilities

- **Dynamic Charge Voltage Control**: Override the fixed 58.4V charge voltage
- **Current Limit Management**: Modify charge/discharge currents without RS485
- **Multi-Pack SOC Averaging**: Intelligent SOC calculation from multiple battery packs
- **Advanced Charge Control**: Force charge modes, discharge protection, and balancing schedules
- **Real-time Monitoring**: Full integration with Home Assistant for monitoring and control

## ✨ Features

### Battery Management
- 🔋 **Multi-Pack SOC Averaging**: Combines SOC from JK BMS + Pack 1 + Pack 2 for accurate readings
- ⚡ **Dynamic Current Control**: Modify charge (0-200A) and discharge (0-200A) currents
- 🎛️ **Voltage Offset Compensation**: Adjustable voltage offset (default 0.4V) for cable drop compensation
- 🔄 **Intelligent Charge Modes**: Force charge control with BMS override capabilities

### Safety & Control
- 🛡️ **Charge/Discharge Enable/Disable**: Manual control over battery operations
- 🔍 **Connection Monitoring**: Real-time BMS and inverter connection status
- 📊 **Advanced Logging**: Detailed SOC filtering and debugging information

### Home Assistant Integration
- 📱 **Full Dashboard Control**: All parameters controllable via Home Assistant
- 📈 **Real-time Monitoring**: Live battery voltage, current, temperature, and power
- 🔔 **Status Notifications**: Connection status and system health monitoring
- 🎛️ **Dynamic Configuration**: Adjust settings without reflashing firmware

## 🔧 Hardware Requirements

### Essential Components
- **ESP32-C6 Development Board** (recommended for dual CAN bus support)
- **2x CAN Transceiver Boards**:
  - **5V Systems**: TJA1050 with 4.7kΩ resistor on RX pin
  - **3.3V Systems**: SN65HVD230 (VP230)

### Alternative Setup
- **ESP32 (any variant)** + **MCP2515 CAN Controller**
- **1x CAN Transceiver Board** (same specifications as above)

### Tested Configuration
- **BMS**: Deye SE-G5.1 Pro BMS
- **Inverter**: Deye SUN8K Single Phase / SUN12K Three Phase
- **ESP32-C6** with dual internal CAN controllers

## 📋 CAN Frame Modifications

The system intercepts and modifies these critical CAN frames:

| Frame ID | Purpose | Modifications |
|----------|---------|---------------|
| `0x351` | Charge voltage & current limits | Voltage offset, current limiting |
| `0x355` | State of Charge (SOC) | Multi-pack averaging, 1% discharge hack |
| `0x35C` | Charge control flags | Force charge override, enable/disable control |
| `0x371` | Charge current override | Dynamic current control |

All other frames are passed through transparently to maintain full BMS functionality.

## 🔌 Connection Diagram

![Connection Diagram](connection.png "ESP32-C6 Dual CAN Bus Connection")

## 🏠 Home Assistant Integration

The system provides comprehensive Home Assistant integration with real-time monitoring and control:

### Sensors
- Battery voltage, current, temperature, and power
- SOC from multiple sources (JK BMS, Pack 1, Pack 2, Combined)
- Charge/discharge current limits
- Connection status (BMS, Inverter)

### Controls
- Charge/discharge current limits
- Voltage offset adjustment
- Force charge modes
- Enable/disable charging/discharging
- Charge scheduling and SOC limits

![Home Assistant Dashboard 1](https://i.imgur.com/rx5Eb2X.png)
![Home Assistant Dashboard 2](https://i.imgur.com/EDk8vfV.png)

## 🚀 Installation

### Prerequisites
- [ESPHome](https://esphome.io/) installed and configured
- Home Assistant with ESPHome integration
- ESP32-C6 development board
- CAN transceiver hardware

### Setup Steps

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Psynosaur/esphome-MitM-deye-jk-bms.git
   cd esphome-MitM-deye-jk-bms
   ```

2. **Configure your secrets** (create `secrets.yaml`):
   ```yaml
   wifi_ssid: "YourWiFiSSID"
   wifi_password: "YourWiFiPassword"
   api_key: "your-32-character-api-key"
   ota_key: "your-ota-password"
   ```

3. **Adjust configuration** in `mitmdeye.yaml`:
   - Update IP address settings
   - Modify current limits if needed
   - Configure Home Assistant entity IDs

4. **Flash to ESP32-C6**:
   ```bash
   esphome run mitmdeye.yaml
   ```

5. **Connect hardware** according to the connection diagram

6. **Add to Home Assistant** via ESPHome integration

## ⚙️ Configuration

### Key Parameters

```yaml
substitutions:
  offset_voltage: "0.4"      # Voltage offset compensation
  charge_current: "200"      # Maximum charge current (A)
  discharge_current: "200"   # Maximum discharge current (A)
```

### Home Assistant Entity Configuration

Update these entity IDs to match your setup:
```yaml
sensor.jk_bms_state_of_charge          # JK BMS SOC
sensor.deye_pcs_can_bus_pack_1_soc     # Pack 1 SOC
sensor.deye_pcs_can_bus_pack_2_soc     # Pack 2 SOC
```

## 🔍 Monitoring & Debugging

The system provides extensive logging for troubleshooting:

- **SOC Values**: Real-time logging of all SOC sources and combined average
- **CAN Traffic**: Optional logging of all CAN frame traffic
- **Connection Status**: BMS and inverter connectivity monitoring
- **Filter Status**: SOC filtering and validation logging

Enable debug logging by changing the logger level:
```yaml
logger:
  level: DEBUG
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests, report issues, or suggest improvements.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with your hardware
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Adminius](https://github.com/Adminius/mitpylon)**: Original creator and inspiration for this project
- **ESPHome Community**: For the excellent framework and support
- **Home Assistant Community**: For integration guidance and testing
- **Deye/JK BMS Communities**: For protocol documentation and testing
