import queue
import obd
import time
# from obd import OBDCommand, Unit
# from obd.protocols import ECU
# from obd.utils import bytes_to_int
# OBD(portstr=None, baudrate=None, protocol=None, fast=True, timeout=0.1, check_voltage=True):
# connection = obd.OBD("/tmp/ttyBLE") # auto-connects to USB or RF port
# global connection,  aika, suoritukset

from threading import Thread

def new_rpm(rpmarvo):
     suoritus +=1
     elmrpm.push(rpmarvo.value)

def new_pedal(pedalarvo):
     suoritus += 1
     elmpedal.push(pedalarvo.value)

def yhteys(elmjono):
    global suoritukset, aika, connection
    try:
        # if (kesto - aloitus) <= aika:
        connection.watch(obd.commands.RPM, callback=new_rpm)
        connection.watch(obdcommands.TROTTHLE_POS, callback=new_pedal)
        connection.start()
        time.sleep(aika)
        # suoritukset += 2
        # kesto = time.time_ns()
    except Exception as msg:
        # aika = kesto-aloitus
        print('yhteys on suljettu ')


def tulosta(kirjoitusjono, tiedosto):
    try:
        with open(tiedosto, 'a') as tiedostopolku:
            while True:
                merkkijono = kirjoitusjono.get(block=False)
                if merkkijono is None:
                    break
                else:
                    tiedostopolku.write(str(merkkijono))
    except Exception as msg:
        print('Tiedostoon tallentaminen epäonnistui')


# obd.logger.setLevel(obd.logging.DEBUG)
connection = obd.Async("/tmp/ttyBLE", baudrate=None, protocol=None, fast=True, timeout=10)
jono = queue.Queue()
aika = 10000000000
suoritukset = 0

connection.watch(obd.commands.RPM, callback=new_rpm)
connection.start()
connection.watch(obd.commands.THROTTLE_POS, callback=new_pedal)
connection.start()

lukeminen = Thread(target=yhteys(jono))
kirjoittaminen = Thread(target=tulosta(jono, "elm327.txt"))
lukeminen.daemon = True
kirjoittaminen.daemon = True
lukeminen.start()
kirjoittaminen.start()
try:
    input('CTRL - C to quit.')
except KeyboardInterrupt:
    pass
#print(aika/1000000000, ' s =', suoritukset, ' datan lukemista')
connection.close()
lukeminen.join()
kirjoittaminen.join()

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
