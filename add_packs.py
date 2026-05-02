#!/usr/bin/env python3
"""add_packs.py - Expand deye_only.yaml for N battery packs.

Generates ESPHome YAML with configurable number of Deye battery packs.
Each pack maps to a CAN frame (0x150 + N-1) with voltage, current, SOC, SOH.

Usage:
  python add_packs.py --packs 4              # output to stdout
  python add_packs.py --packs 4 -o out.yaml  # write to file
  python add_packs.py                        # default 2 packs
"""

import sys
import argparse
from pathlib import Path

INDENT = {
    "global": "  ",
    "handler_can_id": "    ",
    "handler_lambda": "          ",
    "sensor": "  ",
    "soc_avg": "            ",
}

PACK_CAN_BASE = 0x14F  # Pack N -> CAN ID 0x14F + N


def gen_globals(n_packs):
    """Generate global variables for each pack."""
    lines = []
    for n in range(1, n_packs + 1):
        can_id = f"0x{PACK_CAN_BASE + n:03X}"
        lines.append(f'{INDENT["global"]}# Pack {n} (CAN {can_id})')
        lines.append(f'{INDENT["global"]}- id: pack_{n}_soc_can')
        lines.append(f'{INDENT["global"]}  type: float')
        lines.append(f'{INDENT["global"]}  restore_value: no')
        lines.append(f'{INDENT["global"]}  initial_value: \'0.0\'')
        lines.append(f'{INDENT["global"]}- id: last_pack{n}_soc')
        lines.append(f'{INDENT["global"]}  type: float')
        lines.append(f'{INDENT["global"]}  restore_value: no')
        lines.append(f'{INDENT["global"]}  initial_value: \'0.0\'')
        lines.append(f'{INDENT["global"]}- id: pack_{n}_seen')
        lines.append(f'{INDENT["global"]}  type: bool')
        lines.append(f'{INDENT["global"]}  restore_value: no')
        lines.append(f'{INDENT["global"]}  initial_value: \'false\'')
    return '\n'.join(lines)


def gen_handler(n, indent=""):
    """Generate a single CAN handler for pack N."""
    can_id = PACK_CAN_BASE + n
    lines = []
    lines.append(f'{indent}# Pack {n} - CAN 0x{can_id:03X}')
    lines.append(f'{indent}- can_id: 0x{can_id:03X}')
    lines.append(f'{indent}  then:')
    lines.append(f'{indent}    - lambda: |-')
    lines.append(f'{indent}        // Pack {n} data from CAN frame 0x{can_id:03X}')
    lines.append(f'{indent}        float voltage = ((x[1] << 8) | x[0]) / 10.0;')
    lines.append(f'{indent}        float current = ((x[3] << 8) | x[2]) / 10.0;')
    lines.append(f'{indent}        if(x[3] > 0x80) current = uint16_t(~((x[3] << 8) | x[2]) + 1) / -10.0;')
    lines.append(f'{indent}        float soc = ((x[5] << 8) | x[4]) / 10.0;')
    lines.append(f'{indent}        float soh = ((x[7] << 8) | x[6]) / 10.0;')
    lines.append('')
    lines.append(f'{indent}        // Store raw SOC for averaging')
    lines.append(f'{indent}        id(pack_{n}_soc_can) = soc;')
    lines.append('')
    lines.append(f'{indent}        // Filter: allow update if first reading, 0%, or within 2% tolerance')
    lines.append(f'{indent}        bool should_update = (id(last_pack{n}_soc) == 0.0 || soc == 0.0 || abs(soc - id(last_pack{n}_soc)) <= 2.0);')
    lines.append(f'{indent}        if (should_update) {{')
    lines.append(f'{indent}          id(last_pack{n}_soc) = soc;')
    lines.append(f'{indent}        }}')
    lines.append(f'{indent}        id(pack_{n}_seen) = true;')
    lines.append('')
    lines.append(f'{indent}        // Publish to Home Assistant sensors')
    lines.append(f'{indent}        id(pack_{n}_voltage).publish_state(voltage);')
    lines.append(f'{indent}        id(pack_{n}_current).publish_state(current);')
    lines.append(f'{indent}        id(pack_{n}_soc).publish_state(id(last_pack{n}_soc));')
    lines.append(f'{indent}        id(pack_{n}_soh).publish_state(soh);')
    lines.append('')
    lines.append(f'{indent}        ESP_LOGI("Pack {n} CAN", "V: %.1fV, I: %.1fA, SOC: %.1f%%, SOH: %.1f%%", voltage, current, id(last_pack{n}_soc), soh);')
    lines.append('')
    lines.append(f'{indent}        id(inverter)->send_data(can_id, false, x);')
    return '\n'.join(lines)


def gen_all_handlers(n_packs):
    """Generate CAN handlers for all packs."""
    lines = []
    for n in range(1, n_packs + 1):
        if n > 1:
            lines.append('')
        lines.append(gen_handler(n, indent=INDENT["handler_can_id"]))
    return '\n'.join(lines)


def gen_sensors(n_packs):
    """Generate sensor blocks for all packs."""
    lines = []
    for n in range(1, n_packs + 1):
        can_id = f"0x{PACK_CAN_BASE + n:03X}"
        lines.append(f'{INDENT["sensor"]}# Pack {n} sensors from CAN {can_id}')
        lines.append(f'{INDENT["sensor"]}- platform: template')
        lines.append(f'{INDENT["sensor"]}  name: "Pack {n} Voltage"')
        lines.append(f'{INDENT["sensor"]}  id: "pack_{n}_voltage"')
        lines.append(f'{INDENT["sensor"]}  unit_of_measurement: \'V\'')
        lines.append(f'{INDENT["sensor"]}  device_class: \'voltage\'')
        lines.append(f'{INDENT["sensor"]}  state_class: \'measurement\'')
        lines.append(f'{INDENT["sensor"]}  accuracy_decimals: 1')
        lines.append('')
        lines.append(f'{INDENT["sensor"]}- platform: template')
        lines.append(f'{INDENT["sensor"]}  name: "Pack {n} Current"')
        lines.append(f'{INDENT["sensor"]}  id: "pack_{n}_current"')
        lines.append(f'{INDENT["sensor"]}  unit_of_measurement: \'A\'')
        lines.append(f'{INDENT["sensor"]}  device_class: \'current\'')
        lines.append(f'{INDENT["sensor"]}  state_class: \'measurement\'')
        lines.append(f'{INDENT["sensor"]}  accuracy_decimals: 1')
        lines.append('')
        lines.append(f'{INDENT["sensor"]}- platform: template')
        lines.append(f'{INDENT["sensor"]}  name: "Pack {n} SOC"')
        lines.append(f'{INDENT["sensor"]}  id: "pack_{n}_soc"')
        lines.append(f'{INDENT["sensor"]}  unit_of_measurement: \'%\'')
        lines.append(f'{INDENT["sensor"]}  device_class: \'battery\'')
        lines.append(f'{INDENT["sensor"]}  state_class: \'measurement\'')
        lines.append(f'{INDENT["sensor"]}  accuracy_decimals: 1')
        lines.append('')
        lines.append(f'{INDENT["sensor"]}- platform: template')
        lines.append(f'{INDENT["sensor"]}  name: "Pack {n} SOH"')
        lines.append(f'{INDENT["sensor"]}  id: "pack_{n}_soh"')
        lines.append(f'{INDENT["sensor"]}  unit_of_measurement: \'%\'')
        lines.append(f'{INDENT["sensor"]}  device_class: \'battery\'')
        lines.append(f'{INDENT["sensor"]}  state_class: \'measurement\'')
        lines.append(f'{INDENT["sensor"]}  accuracy_decimals: 1')
        if n < n_packs:
            lines.append('')
    return '\n'.join(lines)


def gen_soc_averaging(n_packs):
    """Generate SOC averaging C++ code for the 0x355 handler."""
    i = INDENT["soc_avg"]
    lines = []

    # Per-pack SOC reading
    for n in range(1, n_packs + 1):
        lines.append(f'{i}// Pack {n} SOC from CAN frame')
        lines.append(f'{i}bool pack{n}_available = id(pack_{n}_seen);')
        lines.append(f'{i}float pack{n}_soc = pack{n}_available ? id(last_pack{n}_soc) : 0.0;')
        lines.append('')
        lines.append(f'{i}ESP_LOGI("SOC Source", "Pack {n}: %.1f%% (%s)", pack{n}_soc, pack{n}_available ? "Available" : "Unavailable");')
        if n < n_packs:
            lines.append('')

    lines.append('')
    lines.append(f'{i}// Sum available pack SOCs')
    lines.append(f'{i}int count = 0;')
    lines.append(f'{i}float total = 0.0;')
    lines.append('')

    for n in range(1, n_packs + 1):
        lines.append(f'{i}if (pack{n}_available) {{')
        lines.append(f'{i}  total += pack{n}_soc;')
        lines.append(f'{i}  count++;')
        lines.append(f'{i}}}')

    lines.append('')
    lines.append(f'{i}// Calculate combined average')
    lines.append(f'{i}int combined;')
    lines.append(f'{i}if (count > 0) {{')
    lines.append(f'{i}  combined = (int)round(total / count);')
    lines.append(f'{i}  // Minimum SOC protection: prevent inverter trip at 1%')
    lines.append(f'{i}  int protected_combined = (combined <= 1) ? 2 : combined;')
    lines.append(f'{i}  id(last_combined_soc) = protected_combined;')
    lines.append(f'{i}  id(last_combined_soc_sensor).publish_state(protected_combined);')
    lines.append(f'{i}  combined = protected_combined;')
    lines.append(f'{i}}} else {{')
    lines.append(f'{i}  // No packs available, use last known good value')
    lines.append(f'{i}  combined = id(last_combined_soc);')
    lines.append(f'{i}  ESP_LOGW("SOC Fallback", "No valid SOC sources, using last known value: %d%%", combined);')
    lines.append(f'{i}  if (combined <= 1) {{')
    lines.append(f'{i}    ESP_LOGW("SOC Protection", "Fallback SOC was %d%%, forcing to 2%% to prevent inverter trip", combined);')
    lines.append(f'{i}    combined = 2;')
    lines.append(f'{i}    id(last_combined_soc) = 2;')
    lines.append(f'{i}  }}')
    lines.append(f'{i}}}')

    lines.append('')
    lines.append(f'{i}// Send modified SOC to inverter')
    lines.append(f'{i}id(invSoc) = combined;')
    lines.append(f'{i}uint8_t socByte0 = combined & 0xFF;')
    lines.append(f'{i}uint8_t socByte1 = (combined >> 8) & 0xFF;')
    lines.append(f'{i}ESP_LOGI("SOC Result", "Combined: %d%% from %d pack(s)", combined, count);')
    lines.append(f'{i}std::vector<uint8_t> data{{socByte0, socByte1, x[2], x[3], x[4], x[5], x[6], x[7]}};')
    lines.append(f'{i}id(inverter)->send_data(can_id, false, data);')

    return '\n'.join(lines)


def expand_template(template_path, n_packs):
    """Read template and replace all markers."""
    content = template_path.read_text(encoding='utf-8')

    content = content.replace('{{ PACK_COUNT }}', str(n_packs))
    content = content.replace('{{ PACK_GLOBALS }}', gen_globals(n_packs))
    content = content.replace('{{ PACK_HANDLERS }}', gen_all_handlers(n_packs))
    content = content.replace('{{ PACK_SENSORS }}', gen_sensors(n_packs))
    content = content.replace('{{ SOC_AVERAGING }}', gen_soc_averaging(n_packs))

    return content


def main():
    parser = argparse.ArgumentParser(
        description='Generate ESPHome YAML for MitM-Deye with N battery packs'
    )
    parser.add_argument(
        '--packs', '-n', type=int, default=2,
        help='Number of battery packs (default: 2)'
    )
    parser.add_argument(
        '--template', '-t', default=None,
        help='Template YAML file path (default: deye_only.yaml next to script)'
    )
    parser.add_argument(
        '--output', '-o', default=None,
        help='Output file path (default: stdout)'
    )
    args = parser.parse_args()

    if args.packs < 1:
        print("Error: --packs must be >= 1", file=sys.stderr)
        sys.exit(1)

    if args.packs > 16:
        print("Error: --packs must be <= 16 (CAN ID 0x150-0x15F)", file=sys.stderr)
        sys.exit(1)

    # Resolve template path
    if args.template:
        template_path = Path(args.template)
    else:
        template_path = Path(__file__).parent / 'deye_only.yaml'

    if not template_path.exists():
        print(f"Error: template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    result = expand_template(template_path, args.packs)

    if args.output:
        Path(args.output).write_text(result, encoding='utf-8')
        print(f"Generated {args.packs}-pack config: {args.output}")
    else:
        print(result)


if __name__ == '__main__':
    main()
