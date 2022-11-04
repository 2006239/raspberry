import obd
#from obd import OBDCommand, Unit
#from obd.protocols import ECU
#from obd.utils import bytes_to_int
#OBD(portstr=None, baudrate=None, protocol=None, fast=True, timeout=0.1, check_voltage=True):
#connection = obd.OBD("/tmp/ttyBLE") # auto-connects to USB or RF port
connection = obd.OBD("/tmp/ttyBLE", baudrate=38400,protocol="6", fast=False, timeout=40)

cmd = obd.commands.SPEED # select an OBD command (sensor)
response = connection.query(cmd) # send the command, and parse the response
print(response.value) # returns unit-bearing values thanks to Pint

cmd = obd.commands.THROTTLE_POS
response=connection.query(cmd)
print(response.value)

#cmd = obd.commands.RUN_TIME
#cmd = obd.commands.ELM_VERSION
#cmd = obd.commands.

#def odo(messages):
#    """ decoder for Odometer messages """
#    d = messages[0].data # only operate on a single message
#    d = d[2:] # chop off mode and PID bytes
#    v = bytes_to_int(d) / 4.0  # helper function for converting byte arrays to ints
#    return v * Unit.KM # construct a Pint Quantity

#c = OBDCommand("ODO", "Odometer", b"01A6", 4, uas(0x25), ECU.ENGINE, True)
#o = obd.OBD()

# use the `force` parameter when querying
#response = o.query(c, force=True)
#print(response.value)
connection.close()
