#include "rs485_sniffer.h"
#include "esphome/core/log.h"

namespace esphome {
namespace rs485_sniffer {

static const char *const TAG = "rs485_sniffer";

void RS485Sniffer::setup() {
  ESP_LOGCONFIG(TAG, "Setting up RS485 Sniffer...");
}

void RS485Sniffer::loop() {
  while (available()) {
    uint8_t byte = read();

    // Check for start sequence F4 F5
    if (!this->capturing_ && this->buffer_.size() >= 1 && 
        this->buffer_.back() == 0xF4 && byte == 0xF5) {
      this->buffer_.clear();
      this->buffer_.push_back(0xF4);
      this->buffer_.push_back(0xF5);
      this->capturing_ = true;
      continue;
    }

    if (this->capturing_) {
      this->buffer_.push_back(byte);
      
      // Check for end sequence F4 FB
      if (this->buffer_.size() >= 2 &&
          this->buffer_[this->buffer_.size() - 2] == 0xF4 &&
          this->buffer_[this->buffer_.size() - 1] == 0xFB) {
        
        std::string packet_str = "RS485 packet:";
        for (auto b : this->buffer_) {
          char buf[5];
          sprintf(buf, " %02X", b);
          packet_str += buf;
        }
        ESP_LOGD(TAG, "%s", packet_str.c_str());
        
        this->buffer_.clear();
        this->capturing_ = false;
      }
    }
  }
}

}  // namespace rs485_sniffer
}  // namespace esphome
