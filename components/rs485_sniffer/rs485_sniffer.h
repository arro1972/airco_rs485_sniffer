#pragma once
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"

namespace esphome {
namespace rs485_sniffer {

class RS485Sniffer : public esphome::Component, public esphome::uart::UARTDevice {
 public:
  void setup() override;
  void loop() override;
  void set_uart_parent(esphome::uart::UARTComponent *parent) { this->parent_ = parent; }

 protected:
  std::vector<uint8_t> buffer_;
  bool capturing_ = false;
};

}  // namespace rs485_sniffer
}  // namespace esphome
