import tkinter as tk
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
import threading
tiedosto = "testi03.txt"
ekasuoritus = True
gpsyhteys = False
gps = False
elm327b = False
yhteysjono = Queue()
elm327jono = Queue()

def gps(elmjono, event):
    global gpsyhteys, GPSstatus
    ekasuoritus = True
    client = GPSDClient(host="127.0.0.1")
    for result in client.dict_stream(convert_datetime=True,  filter=["TPV"]):
        # while result.get("mode", "") != 3:
        if result.get("mode", "") == 2:
                yhteysjono.put("GPS_status: 2D scan")
        if result.get("mode", "") == 1:
                yhteysjono.put("GPS_status: no connection")
                gpsyhteys = False
        if result.get("mode", "") == 3: # and gpsyhteys is False:
            print("gpsyhteys")
            yhteysjono.put("GPS_status: 3D scan")
            gpsyhteys = True
            # window.update()
        if ekasuoritus is True and gpsyhteys is True:
            elmjono.put("<data>")
            elmjono.put("<cycle>\n<time> %s" % result.get("time", "").strftime("%d.%m.%Y %H:%M:%S") + " </time>\n<gps>\n<lat> %s" % result.get("lat", "") + " </lat>\n<lon> %s" % result.get("lon", "") + " </lon>\n</gps>")
            ekasuoritus = False
            # yhteysjono.put("GPS_status: luetaan")
        elif gpsyhteys is True:
            elmjono.put("</cycle>\n<cycle>\n<time> %s" % result.get("time", "").strftime("%d.%m.%Y %H:%M:%S") + " </time>\n<gps>\n<lat> %s" % result.get("lat", "") + " </lat>\n<lon> %s" % result.get("lon", "") + " </lon>\n</gps>")
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
    while ekasuoritus is True:
        time.sleep(0.2)
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
        time.sleep(0.27)

def yhteys(elmjono, event):
    global connection
    # try:
    connection = obd.OBD("/tmp/ttyBLE")  # , baudrate=None, protocol=None, fast=True, timeout=10)
    while connection.is_connected() is False and ekasuoritus is True:
         elm327jono.put("ELM327_status: " +connection.status())
         time.sleep(3)
         connection = obd.OBD("/tmp/ttyBLE")
    elm327jono.put("ELM327_status: " +connection.status())
    while connection.is_connected():  # and (kesto - aloitus) <= aika:
        # elm327.jono.put(obd.status())
        if event.is_set():
            connection.close()
            elm327jono.put("ELM327_status: "+connection.status())
            break
        # elm327jono.put("ELM327_status: kirjoitetaan")
        cmd = obd.commands.SPEED  # select an OBD command (sensor)
        response = connection.query(cmd)  # send the command, and parse the response
        if not response.is_null():
            temp = "<speed> " +  str(response.value) + " </speed>"
            elmjono.put(temp)  # returns unit-bearing values thanks to Pint
        cmd = obd.commands.THROTTLE_POS
        response = connection.query(cmd)
        if not response.is_null():
            temp = "<throttle_pos> " + str(response.value) + " </throttle_pos>"
            elmjono.put(temp)
        cmd = obd.commands.FUEL_RATE
        response = connection.query(cmd)
        if not response.is_null():
            temp = "<fuel_rate> " + str(response.value) + " </fuel_rate>"
            elmjono.put(temp)
            # cmd = ODO
            # response = connection.query(cmd, force=True)
            # elmjono.put(response.value)
            # except Exception as msg:
            # print('yhteys on suljettu ' + str(msg))
    elm327jono.put("ELM327_status: "+connection.status())

def tulosta(kirjoitusjono, tiedosto, event):
    laskuri = 0
    merkkijono = ""
    try:
        with open(tiedosto, 'w') as tiedostopolku:
            while True:
                if event.is_set():
                    tiedostopolku.write("</cycle>")
                    tiedostopolku.write("</data>")
                    tiedostopolku.close()
                    break
                while kirjoitusjono.empty() is True:
                    time.sleep(1)
                    laskuri = laskuri + 1
                    print("Tiedostoon kirjoitus odottaa dataa ("+ str(laskuri) + ")")
                else:
                    print(merkkijono)
                    merkkkijono = kirjoitusjono.get(False)
                    tiedostopolku.write(f"{merkkijono}\n")
    except Exception as msg:
        print('Tiedostoon tallentaminen loppui:', msg)


def aja():
    global window, gpslukeminen, acceleroloop, elm327, kirjoittaminen, event
    obd.logger.setLevel(obd.logging.DEBUG)
    # connection = obd.OBD("/tmp/ttyBLE")  # , baudrate=None, protocol=None, fast=True, timeout=10)
    # elm327jono.put("ELM327_status: "+connection.status())
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

def paivita():
    global gps, elm327b
    if yhteysjono.empty() is False: #  and ekasuoritus is False:
        temp = yhteysjono.get(False)
        # print(temp)
        gps=True
        GPSstatus_string.set(temp)
        # button.config(text="Lopeta", command=close_window, fg="red", state="normal")
        window.update_idletasks()
    if elm327jono.empty() is False: # and ekasuoritus is False:
        temp2 = elm327jono.get(False)
        # print(temp2)
        elm327b = True
        ELM327status_string.set(temp2)
        window.update_idletasks()
    if gps and elm327b and ekasuoritus is False:
        button.config(text="Lopeta", command=close_window, fg="red", state="normal")
        window.update_idletasks()
        window.after(1000, paivita)
    else:
        window.after(100, paivita)

def aloita_lopeta():
    if button['text'] == "Aloita":
        aja()
        threading.Thread(target=paivita).start()
        button.config(text="Yhdistetään...", fg="green", state="disabled")
    else:
        button.config(text="Aloita", command=close_window, fg="green")


if __name__ == '__main__':
    window = tk.Tk()
    GPSstatus_string = tk.StringVar(window)
    ELM327status_string=tk.StringVar(window)
    GPSstatus_string.set("GPS_status: offline")
    ELM327status_string.set("ELM327_status: offline")
    GPSstatus = tk.Label(window, textvariable=GPSstatus_string)
    ELM327status = tk.Label(window, textvariable=ELM327status_string)
    button = tk.Button(window, text="Aloita", command=aloita_lopeta, font=("Roboto", 50), bg="lightgrey")
    button.pack()
    button.place(relx=0.5, rely=0.5, anchor="center")
    window.title("OBD2, GPS ja kiihtyvyysanturin lukeminen ")
    window.geometry("400x400")
    # GPSstatus=Label(window, text = "GPS_status: offline")
    GPSstatus.place(x = 40,y = 60)
    ELM327status.place(x = 40,y = 80)
    # window.attributes('-fullscreen', True)
    window.configure(bg="seashell")

    window.mainloop()







