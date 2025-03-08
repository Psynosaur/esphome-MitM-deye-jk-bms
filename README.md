# MitM Deye
Man In The Middle Adapter For Deye Communction Protocol

# WARNING
I'm not responsible for any damaged caused by this software.

Use it at your own risk!

# Idea behind it
Deye BMS does not allow setting request charge voltage, it is 58.4V always.

We intercept the message and change it to a value of our liking.

We also can change current limits without using the RS485 on inverter.

The rest of the frames are just passed on for each battery in my 2 pack array.

# Features
- Modify charge current: from 0 amps to the values that BMS allows
- Modify discharge current: from 0 amps to the values that BMS allows
- Set offset to charge voltage (default 0.5V) to compensate voltage drop or fix voltage issues on some inverters, like Deye SUN12K
- Set charge limit to SoC 90% and automaticaly charge to 100% on each sunday for balancing
- Enable/Disable charging
- Enable/Disable discharging
- Control SoC 100% (don't send 100% to inverter until float voltage state is reached)

# Limitations
We only modify these frames

    0x351, 0x355
    
# Requirements 
    - ESP32 C6
    - MCP2515 if not using ESP32 C6
    - CAN transceiver boards
        - 5V => TJA1050 CAN transciever boards with a 4k7Ω resistor on RX pin to ESP32
        - 3.3V => SN65HVD230 VP230 
        
This YAML was tested on ESP32 C6 with 2 CAN-Bus transceiver and modified ESPHome esp32_can component, to handle 2x internal CAN-busses

![Connection diagram](connection.png "Connection diagram")

Tested with Deye SE-G5.1 Pro BMS and Deye SUN8K single phase inverter

## Home assistant:
![mitm2](https://i.imgur.com/rx5Eb2X.png)
![mitm](https://i.imgur.com/EDk8vfV.png)

## Plans:
  - Build JK battery...
  - Add JK inverter BMS into the mix: 
    - 2xDeye - 200Ah 
    - 1xJK200A - 280Ah (CAN/RS485)
