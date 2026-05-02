# ESPHome MitM Deye

Man-in-the-middle adapter intercepting CAN bus messages between Deye BMS and inverter for enhanced control.

Based on [Adminius/mitpylon](https://github.com/Adminius/mitpylon).

## Disclaimer

**USE AT YOUR OWN RISK.** This modifies critical battery management communication. No liability for damage to equipment or property.

## Overview

The Deye BMS protocol has a fixed charge voltage (58.4V). This adapter sits on the CAN bus between BMS and inverter, modifying frames to enable dynamic control.

### Capabilities

- Dynamic charge voltage override via adjustable offset
- Charge/discharge current limiting without RS485
- Multi-pack SOC averaging (JK BMS + Pack 1 + Pack 2)
- Force charge, discharge protection, charge scheduling
- Full Home Assistant integration (monitoring + control)

## Hardware

### Required

- **ESP32-C6** (dual internal CAN controllers)
- **2x CAN transceivers**:
  - 5V: TJA1050 with 4.7k resistor on RX
  - 3.3V: SN65HVD230 (VP230)

### Alternative

- Any ESP32 + MCP2515 CAN controller + 1x transceiver

### Tested

- Deye SE-G5.1 Pro BMS
- Deye SUN8K / SUN12K inverters
- ESP32-C6

## CAN Frames Modified

| Frame  | Purpose                        | Modification                              |
|--------|--------------------------------|-------------------------------------------|
| 0x351  | Charge voltage & current limits| Voltage offset, current limiting          |
| 0x355  | State of Charge (SOC)          | Multi-pack averaging, 1% protection hack  |
| 0x35C  | Charge control flags           | Force charge, enable/disable              |
| 0x371  | Charge current override        | Dynamic current control                   |

All other frames pass through transparently.

## Connection Diagram

![Connection Diagram](connection.png)

## Home Assistant Integration

**Sensors:** battery voltage, current, temperature, power, SOC (JK BMS, Pack 1, Pack 2, Combined), charge/discharge limits, BMS/inverter connection status

**Controls:** charge/discharge current limits, voltage offset, force charge, enable/disable, charge scheduling, SOC limits

## Installation

1. Clone: `git clone https://github.com/Psynosaur/esphome-MitM-deye-jk-bms.git`
2. Create `secrets.yaml`:
   ```yaml
   wifi_ssid: "YourWiFiSSID"
   wifi_password: "YourWiFiPassword"
   api_key: "your-32-character-api-key"
   ota_key: "your-ota-password"
   ```
3. Adjust `mitmdeye.yaml`: IP address, current limits, entity IDs
4. Flash: `esphome run mitmdeye.yaml`
5. Connect hardware per connection diagram
6. Add to Home Assistant via ESPHome integration

## Configuration

```yaml
substitutions:
  offset_voltage: "0.4"      # Voltage drop compensation
  charge_current: "200"      # Max charge current (A)
  discharge_current: "200"   # Max discharge current (A)
```

## Debugging

Set logger level to DEBUG for SOC values, CAN traffic, connection status, and filter logging.

## Contributing

Fork, branch, test on hardware, submit PR.

## License

MIT - see [LICENSE](LICENSE).

## Acknowledgments

- [Adminius](https://github.com/Adminius/mitpylon) - original creator
- ESPHome and Home Assistant communities
- Deye/JK BMS communities for protocol documentation
