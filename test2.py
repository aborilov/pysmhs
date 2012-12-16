from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD
from serial import STOPBITS_ONE, STOPBITS_TWO
from serial import FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
from pymodbus.client.sync import ModbusSerialClient as Modbus


STATUS_REGS = (3598, 100)
conf = {'port': '/dev/plc'}
conf['baudrate'] = '9600'
conf['bytesize'] = SEVENBITS
conf['parity'] = PARITY_EVEN
conf['timeout'] = 0.03
conf['stopbits'] = STOPBITS_ONE
client = Modbus(method='ascii', **conf)
client.connect()
print "Connecting to ModBus"
rr = client.read_holding_registers(*STATUS_REGS)
assert(rr.function_code < 0x80)
rv = []
rv = list(rr.registers)
print rv
