import obd
import time
import sys
from tkinter import *
from obd import OBDCommand, Unit
from obd.protocols import ECU
from obd.utils import bytes_to_int
from gpsdclient import GPSDClient
import board
import busio
import adafruit_lis3dh
import multiprocessing
from multiprocessing import Queue
from multiprocessing import Event
# global connection, suoritukset
# connection = obd. OBD(portstr="/tmp/ttyBLE", baudrate=None, protocol=None, fast=True, timeout=0.1, check_voltage=True)
# connection = obd.OBD("/tmp/ttyBLE") # auto-connects to USB or RF port
window = Tk()
def close_window():
    exit()
button = Button(window, text = "testi", command = close_window)
button.pack()
window.mainloop()

def _no_traceback_excepthook(exc_type, exc_val, traceback):
    pass

def gps(elmjono, event):
    tosi = True
    client = GPSDClient(host="127.0.0.1")
    for result in client.dict_stream(convert_datetime=True,  filter=["TPV"]):    
        if tosi is True:
            elmjono.put("<cycle>\n<time> %s" % result.get("time", "").strftime("%d.%m.%Y %H:%M:%S") + " </time>\n<gps>\n<lat> %s" % result.get("lat", "") + " </lat>\n<lon> %s" % result.get("lon", "") + " </lon>\n</gps>")
            tosi = False
        else:
            elmjono.put("</cycle>\n<cycle>\n<time> %s" % result.get("time", "").strftime("%d.%m.%Y %H:%M:%S") + " </time>\n<gps>\n<lat> %s" % result.get("lat", "") + " <\lat>\n<lon> %s" % result.get("lon", "") + " <\lon>\n</gps>")
        if event.is_set():
            break

def accelerometer(elmjono, event):
    if hasattr(board, "ACCELEROMETER_SCL"):
        i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
        lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
    else:
         i2c = board.I2C()  # uses board.SCL and board.SDA
         # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
         lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c)
    lis3dh.range = adafruit_lis3dh.RANGE_2_G
    # Loop forever printing accelerometer values
    while True:
        if event.is_set():
            break
        # Read accelerometer values (in m / s ^ 2).  Returns a 3-tuple of x, y,
        # z axis values.  Divide them by 9.806 to convert to Gs.
        x, y, z = [
             value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration
        ]
        # print("x = %0.3f G, y = %0.3f G, z = %0.3f G" % (x, y, z))			
        elmjono.put("<accelerometer>\n<x> %0.3f </x>\n<y> %0.3f </y>\n<z> %0.3f </z>\n" % (x, y, z) + "</accelerometer>")
        # Small delay to keep things responsive but give time for interrupt processing.
        time.sleep(1)

def yhteys(elmjono, event):
    global connection
    # try:
    while connection.is_connected():  # and (kesto - aloitus) <= aika:
        if event.is_set():
            connection.close()
            break
        cmd = obd.commands.SPEED  # select an OBD command (sensor)
        response = connection.query(cmd)  # send the command, and parse the response
        if not response.is_null():
            temp = "<speed>" +  str(response.value) + "</speed>"
            elmjono.put(temp)  # returns unit-bearing values thanks to Pint
        cmd = obd.commands.THROTTLE_POS
        response = connection.query(cmd)
        if not response.is_null():
            temp = "<throttle_pos>" + str(response.value) + "</throttle_pos>"
            elmjono.put(temp)
        cmd = obd.commands.FUEL_RATE
        response = connection.query(cmd)
        if not response.is_null():
            temp = "<fuel_rate>" + str(response.value) + "</fuel_rate>"
            elmjono.put(temp)
            # cmd = ODO
            # response = connection.query(cmd, force=True)
            # elmjono.put(response.value)
            # except Exception as msg:
            # print('yhteys on suljettu ' + str(msg))

def tulosta(kirjoitusjono, tiedosto, event):
    laskuri = 0
    try:
        with open(tiedosto, 'w') as tiedostopolku:
            while True:
                if event.is_set():
                    tiedostopolku.close()
                    break 
                merkkijono = kirjoitusjono.get()
                if merkkijono is None:
                    time.sleep(1)
                    laskuri = laskuri + 1
                    print("Kirjoutus odottaa dataa ", laskuri)
                else:
                    tiedostopolku.write(f"{merkkijono}\n")
    except Exception as msg:
        print('Tiedostoon tallentaminen loppui', msg)


# try:
# input('CTRL -C to quit.')
obd.logger.setLevel(obd.logging.DEBUG)
connection = obd.OBD("/tmp/ttyBLE") # , baudrate=None, protocol=None, fast=True, timeout=10)
jono = Queue()
aika = 100000000
suoritukset = 0
event = Event()
gpsLukeminen = multiprocessing.Process(target=gps, args=(jono, event, ))
acceleroloop = multiprocessing.Process(target=accelerometer, args=(jono, event, ))
elm327 = multiprocessing.Process(target=yhteys, args=(jono,event, ))
kirjoittaminen = multiprocessing.Process(target=tulosta, args=(jono, "testi00.txt", event, ))

kirjoittaminen.daemon = True
gpsLukeminen.daemon = True
elm327.daemon = True
acceleroloop.daemon = True
gpsLukeminen.start()
elm327.start()
acceleroloop.start()
kirjoittaminen.start()
try:
    input('CTRL -C to quit.')
    while(true):
        time.wait(5)
except KeyboardInterrupt:
    event.set()
    elm327.join()
    acceleroloop.join()
    gpsLukeminen.join()
    kirjoittaminen.join()
    print("Lopetetaan")
    pass
    if sys.excepthook is sys.__excepthook__:
       sys.excepthook = _no_traceback_excepthook
    raise

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
