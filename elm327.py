from tkinter import *
import obd
import time
import sys
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
tiedosto = "testi01.txt"
ekasuoritus = False
gpsyhteys = False
window = Tk()

def gps(elmjono, event):
    ekasuoritus = True
    client = GPSDClient(host="127.0.0.1")
    for result in client.dict_stream(convert_datetime=True,  filter=["TPV"]):
        if result.get("mode", "") == "3":
            GPSstatus=Label(window, text = "GPS_status: online")
        if ekasuoritus is True and gpsyhteys is True:
            elmjono.put("<cycle>\n<time> %s" % result.get("time", "").strftime("%d.%m.%Y %H:%M:%S") + " </time>\n<gps>\n<lat> %s" % result.get("lat", "") + " </lat>\n<lon> %s" % result.get("lon", "") + " </lon>\n</gps>")
            ekasuoritus = False
        elif gpsyhteys is True:
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
    # global connection
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


def aja():
    global connection,gpslukeminen,acceleroloop,elm327,kirjoittaminen,event,GPSstatus
    obd.logger.setLevel(obd.logging.DEBUG)
    connection = obd.OBD("/tmp/ttyBLE")  # , baudrate=None, protocol=None, fast=True, timeout=10)
    jono = Queue()
    event = Event()
    gpslukeminen = multiprocessing.Process(target=gps, args=(jono, event,))
    acceleroloop = multiprocessing.Process(target=accelerometer, args=(jono, event,))
    elm327 = multiprocessing.Process(target=yhteys, args=(jono, event,))
    kirjoittaminen = multiprocessing.Process(target=tulosta, args=(jono, tiedosto, event,))

    kirjoittaminen.daemon = True
    gpslukeminen.daemon = True
    elm327.daemon = True
    acceleroloop.daemon = True
    gpslukeminen.start()
    elm327.start()
    acceleroloop.start()
    kirjoittaminen.start()

def close_window():
    event.set()
    elm327.join()
    acceleroloop.join()
    gpslukeminen.join()
    kirjoittaminen.join()
    exit()


def aloita_lopeta():
    laskuri = 0
    if button["text"] == "Aloita":
        aja()
        button.config(text="Lopeta", fg="red", state="normal")
    else:
        button.config(text="Aloita", command=close_window, fg="green")


button = Button(window, text="Aloita", command=aloita_lopeta, font=("Roboto", 50), bg="lightgrey")
button.pack()
button.place(relx=0.5, rely=0.5, anchor=CENTER)
window.title("OBD2, GPS ja kiihtyvyysanturin lukeminen ")
window.geometry("400x400")
GPSstatus=Label(window, text = "GPS_status: offline")
GPSstatus.place(x = 40,y = 60)
# window.attributes('-fullscreen', True)
window.configure(bg="seashell")
window.mainloop()






