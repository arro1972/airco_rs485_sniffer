# ESPHome RS485 Sniffer Component

An ESPHome component for sniffing the RS$*% communication between an AEH-W4A1 wifi module and the Hisense airco unit including start/stop sequences.

## Installation

Add this to your ESPHome configuration:

```yaml
external_components:
  - source: github://arro1972/airco_rs485_sniffer
    components: [rs485_sniffer]

uart:
  id: uart_bus
  rx_pin: GPIO3
  baud_rate: 9600

rs485_sniffer:
  uart_id: uart_bus
