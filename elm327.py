import subprocess	
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
tiedosto = "testi33.txt"
ekasuoritus = True
gpsyhteys = False
gpss = False
elm327b = False
yhteysjono = Queue()
elm327jono = Queue()

def gps(elmjono,state, event):
    global gpsyhteys, GPSstatus
    status = "yhdistetaan"
    # ekasuoritus = True
    client = GPSDClient(host="127.0.0.1")
    for result in client.dict_stream(convert_datetime=True,  filter=["TPV"]):
        yhteysjono.put(status)
        if result.get("mode", "") == 2:
            status = "GPS_status: 2D scan"
        if result.get("mode", "") == 1:
            status = "GPS_status: no connection"
            gpsyhteys = False
        if result.get("mode", "") == 3: # and gpsyhteys is False:
            # print("gpsyhteys")
            status = "GPS_status: 3D scan"
            gpsyhteys = True
            # window.update()
        if gpsyhteys is True and state.empty() is True:
            elmjono.put("<data>")
            elmjono.put("<cycle>\n<time> %s" % result.get("time", "").strftime("%d.%m.%Y %H:%M:%S") + " </time>\n<gps>\n<lat> %s" % result.get("lat", "") + " </lat>\n<lon> %s" % result.get("lon", "") + " </lon>\n</gps>")
            state.put("jonossa")
        elif gpsyhteys is True:
            temp = result.get("speed", "")
            nopeus = str("{:.2f}".format(float(temp)*3.6))
            elmjono.put("</cycle>\n<cycle>\n<time> %s" % result.get("time", "").strftime("%d.%m.%Y %H:%M:%S") + " </time>\n<gps>\n<lat> %s" % result.get("lat", "") + " </lat>\n<lon> %s" % result.get("lon", "") + " </lon>\n<gpsspeed> " + nopeus + " </gpsspeed>\n</gps>")
            status =  "GPS_status: luetaan"
        if event.is_set():
            status = "GPS_status: lopetetaan"
            break

def accelerometer(elmjono,state, event):
    if hasattr(board, "ACCELEROMETER_SCL"):
        i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
        lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
    else:
        i2c = board.I2C()  # uses board.SCL and board.SDA
        # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c)
    lis3dh.range = adafruit_lis3dh.RANGE_2_G
    # Loop forever printing accelerometer values
    while state.empty() is True:
        time.sleep(0.2)
        if event.is_set():
            break
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
        # print(elmjono)
        # Small delay to keep things responsive but give time for interrupt processing.
        time.sleep(0.27)

def yhteys(elmjono, state, event):
    global connection
    templaskuri = 0
    # try:
    connection = obd.OBD("/tmp/ttyBLE", baudrate="19200") #, protocol="A") 9600, 38400, 19200, 57600, 115200, protocol=None, fast=True, timeout=10)
    while connection.is_connected() is False and state.empty() is True:
        subprocess.call("./ble.sh", shell=True)
        elm327jono.put("ELM327_status: " +connection.status())
        if event.is_set():
            break
        time.sleep(3)
        connection = obd.OBD("/tmp/ttyBLE", baudrate="19200") # , protocol="A") , protocol=None, fast=True, timeout=10)
    elm327jono.put("ELM327_status: " +connection.status())
    while connection.is_connected():  # and (kesto - aloitus) <= aika:
        # elm327.jono.put(obd.status())
        if event.is_set():
            connection.close()
            elm327jono.put("ELM327_status: "+connection.status())
            break
        #  if templaskuri = 0:
        #    templaskuri = 0
        #    connection.close()
        #    while connection.is_connected() is False:
        #        elmjono.put("ELM327_status: "+ connection.status())
        #        connection = obd.OBD("tmp/ttyBLE", baudrate="19200") #, protocol="A")
        #    if event.is_set():
        #        break
        #    subprocess.call("./ble.sh", shell=True)
        # elm327jono.put("ELM327_status: kirjoitetaan")
        cmd = obd.commands.SPEED  # select an OBD command (sensor)
        response = connection.query(cmd)  # send the command, and parse the response
        if not response.is_null():
            # templaskuri=templaskuri+1 
        # else:
            temp = "<speed> " +  str(response.value) + " </speed>"
            elmjono.put(temp)  # returns unit-bearing values thanks to Pint
        cmd = obd.commands.THROTTLE_POS
        response = connection.query(cmd)
        if not response.is_null():
            # templaskuri = templaskuri+1
        # else:
            temp = "<throttle_pos> " + str(response.value) + " </throttle_pos>"
            elmjono.put(temp)
        cmd = obd.commands.FUEL_RATE
        response = connection.query(cmd)
        if not response.is_null():
            # templaskuri = templaskuri+1
        # else:
            temp = "<fuel_rate> " + str(response.value) + " </fuel_rate>"
            elmjono.put(temp)
            # cmd = ODO
            # response = connection.query(cmd, force=True)
            # elmjono.put(response.value)
            # except Exception as msg:
            # print('yhteys on suljettu ' + str(msg))
    elm327jono.put("ELM327_status: "+connection.status())

def tulosta(elmjono, state, tiedosto, event):
    laskuri = 0
    merkkijono = ""
    # try:
    with open(tiedosto, 'w') as tiedostopolku:
        while True:
            if event.is_set():
                tiedostopolku.write("</cycle>")
                tiedostopolku.write("</data>")
                tiedostopolku.close()
                break
            while elmjono.empty():
                time.sleep(1)
                laskuri = laskuri + 1
                # print("Tiedostoon kirjoitus odottaa dataa ("+ str(laskuri) + ")")
            # print(elmjono.qsize())
            merkkijono = elmjono.get(block=False)
            print(merkkijono)
            tiedostopolku.write(f"{merkkijono}\n")
#    except Exception as msg:
        print('Tiedostoon tallentaminen loppui.')  # , msg)


def aja():
    global window, gpslukeminen, acceleroloop, elm327, kirjoittaminen, event
    # obd.logger.setLevel(obd.logging.DEBUG)
    # connection = obd.OBD("/tmp/ttyBLE")  # , baudrate=None, protocol=None, fast=True, timeout=10)
    # elm327jono.put("ELM327_status: "+connection.status())
    subprocess.call("./ble.sh", shell=True)
    time.sleep(3)
    state = multiprocessing.Queue()
    jono = multiprocessing.Queue()
    event = Event()
    gpslukeminen = multiprocessing.Process(target=gps, args=(jono, state, event,))
    acceleroloop = multiprocessing.Process(target=accelerometer, args=(jono, state, event,))
    elm327 = multiprocessing.Process(target=yhteys, args=(jono, state, event,))
    kirjoittaminen = multiprocessing.Process(target=tulosta, args=(jono, state, tiedosto, event,))
    kirjoittaminen.daemon = True
    gpslukeminen.daemon = True
    elm327.daemon = True
    acceleroloop.daemon = 							True
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
    global gpss, elm327b
    if yhteysjono.empty() is False: #  and ekasuoritus is False:
        temp = yhteysjono.get(False)
        # print(temp)
        gpss = True
        GPSstatus_string.set(temp)
        # button.config(text="Lopeta", command=close_window, fg="red", state="normal")
        window.update_idletasks()
    if elm327jono.empty() is False: # and ekasuoritus is False:
        temp2 = elm327jono.get(False)
        # print(temp2)
        elm327b = True
        ELM327status_string.set(temp2)
        window.update_idletasks()
    if gpss and elm327b: # and ekasuoritus is False:
        button.config(text="Lopeta", command=close_window, fg="red", state="normal")
        window.update_idletasks()
        window.after(1000, paivita)
    else:
        window.after(100, paivita)

def aloita_lopeta():
    if button['text'] == "Aloita":
        aja()
        threading.Thread(target=paivita, args=()).start()
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







