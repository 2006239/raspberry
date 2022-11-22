import queue
import obd
import time
from obd import OBDCommand, Unit
from obd.protocols import ECU
from obd.utils import bytes_to_int
from gpsdclient import GPSDClient
# OBD(portstr=None, baudrate=None, protocol=None, fast=True, timeout=0.1, check_voltage=True):
# connection = obd.OBD("/tmp/ttyBLE") # auto-connects to USB or RF port
# global connection,  aika, suoritukset

from threading import Thread


def odo(messages):
    #    """ decoder for Odometer messages """
    d = messages[0].data  # only operate on a single message
    d = d[2:]  # chop off mode and PID bytes
    v = bytes_to_int(d) / 4.0  # helper function for converting byte arrays to ints
    return v * Unit.KM  # construct a Pint Quantity


ODO = OBDCommand("ODO", "Odometer", b"01A6", 4, odo, ECU.ENGINE, True)
#  o = obd.OBD()

# use the `force` parameter when querying
# response = o.query(c, force=True)
# print(response.value)


def gps(elmjono):
    client = GPSDClient(host="127.0.0.1")
    for result in client.dict_stream(convert_datetime=True,  filter=["TPV"]):
        elmjono.put("<time> %s" % result.get("time", "") + "{ lat: %s" % result.get("lat", "") + ", long: %s }" % result.get("lon", "") + "</time>")


def yhteys(elmjono):
    global suoritukset, aika, connection
    kesto = 0
    aloitus = time.time_ns()
    try:
        while connection.is_connected() and (kesto - aloitus) <= aika:
            cmd = obd.commands.SPEED  # select an OBD command (sensor)
            response = connection.query(cmd)  # send the command, and parse the response
            elmjono.put(response.value)  # returns unit-bearing values thanks to Pint

            cmd = obd.commands.THROTTLE_POS
            response = connection.query(cmd)
            elmjono.put(response.value)

            cmd = obd.commands.RPM
            response = connection.query(cmd)
            elmjono.put(response.value)

            cmd = obd.commands.FUEL_RATE
            response = connection.query(cmd)
            elmjono.put(response.value)

            # cmd = obd.commands.RUNTIME
            # response = connection.query(cmd)
            # elmjono.put(response.value)

            cmd = ODO
            response = connection.query(cmd, force=True)
            elmjono.put(response.value)

            suoritukset += 5
            kesto = time.time_ns()
    except Exception as msg:
        aika = kesto-aloitus
        print('yhteys on suljettu ' + str(msg))


def tulosta(kirjoitusjono, tiedosto):
    try:
        with open(tiedosto, 'a') as tiedostopolku:
            while True:
                merkkijono = kirjoitusjono.get(block=False)
                if merkkijono is None:
                    break
                else:
                    tiedostopolku.write(f"{merkkijono};\n")

    except Exception as msg:
        print('Tiedostoon tallentaminen loppui')


obd.logger.setLevel(obd.logging.DEBUG)
connection = obd.OBD("/tmp/ttyBLE", baudrate=None, protocol=None, fast=False, timeout=5)
jono = queue.Queue()
aika = 10000000000*6
suoritukset = 0
gpsLukeminen = Thread(target=gps(jono))
lukeminen = Thread(target=yhteys(jono))
kirjoittaminen = Thread(target=tulosta(jono, "elm327.txt"))
gpsLukeminen.daemon = True
lukeminen.daemon = True
kirjoittaminen.daemon = True
gpsLukeminen.start()
lukeminen.start()
kirjoittaminen.start()
try:
    input('CTRL - C to quit.')
except KeyboardInterrupt:
    pass
print(aika/1000000000, ' s =', suoritukset, ' datan lukemista')
connection.close()
gpsLukeminen.join()
lukeminen.join()
kirjoittaminen.join()


# def odo(messages):
#    """ decoder for Odometer messages """
#    d = messages[0].data # only operate on a single message
#    d = d[2:] # chop off mode and PID bytes
#    v = bytes_to_int(d) / 4.0  # helper function for converting byte arrays to ints
#    return v * Unit.KM # construct a Pint Quantity

# c = OBDCommand("ODO", "Odometer", b"01A6", 4, odo, ECU.ENGINE, True)
# o = obd.OBD()

# use the `force` parameter when querying
# response = o.query(c, force=True)
# print(response.value)
