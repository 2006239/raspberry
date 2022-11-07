import obd
import time
# from obd import OBDCommand, Unit
# from obd.protocols import ECU
# from obd.utils import bytes_to_int
# OBD(portstr=None, baudrate=None, protocol=None, fast=True, timeout=0.1, check_voltage=True):
# connection = obd.OBD("/tmp/ttyBLE") # auto-connects to USB or RF port
# global connection,  aika, suoritukset

from threading import Thread


def yhteys():
    global suoritukset, aika, connection
    kesto = 0
    aloitus = time.time_ns()
    try:
        while connection.is_connected() and (kesto - aloitus) <= aika:
            cmd = obd.commands.SPEED  # select an OBD command (sensor)
            response = connection.query(cmd)  # send the command, and parse the response
            print(response.value)  # returns unit-bearing values thanks to Pint

            cmd = obd.commands.THROTTLE_POS
            response = connection.query(cmd)
            print(response.value)
            suoritukset += 2
            kesto = time.time_ns()
    except Exception as msg:
        aika = kesto-aloitus
        print('yhteys on suljettu ', msg)


obd.logger.setLevel(obd.logging.DEBUG)
connection = obd.OBD("/tmp/ttyBLE", baudrate=None, protocol=None, fast=True, timeout=10)
aika = 1000000000
suoritukset = 0
lukeminen = Thread(target=yhteys())
yhteys.daemon = True
lukeminen.start()
try:
    input('CTRL – C to quit.')
except KeyboardInterrupt:
    pass
print(aika/1000000000, ' s >', suoritukset, ' datan lukemista')
lukeminen.join()
connection.close()

# cmd = obd.commands.RUN_TIME
# cmd = obd.commands.ELM_VERSION
# cmd = obd.commands.

# def odo(messages):
#    """ decoder for Odometer messages """
#    d = messages[0].data # only operate on a single message
#    d = d[2:] # chop off mode and PID bytes
#    v = bytes_to_int(d) / 4.0  # helper function for converting byte arrays to ints
#    return v * Unit.KM # construct a Pint Quantity

# c = OBDCommand("ODO", "Odometer", b"01A6", 4, uas(0x25), ECU.ENGINE, True)
# o = obd.OBD()

# use the `force` parameter when querying
# response = o.query(c, force=True)
# print(response.value)
