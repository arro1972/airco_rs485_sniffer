import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ID

DEPENDENCIES = ['uart']

rs485_sniffer_ns = cg.esphome_ns.namespace('rs485_sniffer')
RS485Sniffer = rs485_sniffer_ns.class_('RS485Sniffer', cg.Component, uart.UARTDevice)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(RS485Sniffer),
    cv.Required(uart.CONF_UART_ID): cv.use_id(uart.UARTComponent),
}).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    
    uart_component = await cg.get_variable(config[uart.CONF_UART_ID])
    cg.add(var.set_uart_parent(uart_component))
