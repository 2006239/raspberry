from tkinter import *
import time
tosi = False
window = Tk()
gpsyhteys = False

def aja():
    global gpsyhteys, GPSstatus
    print("testi")
    gpsyhteys = True
    GPSstatus.config(text="GPS_status: online")

def close_window():
    exit()

def aloita_lopeta():
    gpsyhteys = False
    aja()
    if button["text"] == "Aloita":
        button.config(text="Lopeta", fg="red", state="normal")
    else:
        button.config(text="Aloita", command=close_window(), fg="green")


button = Button(window, text = "Aloita", command = aloita_lopeta, font=("Roboto", 50), bg="lightgrey")
button.pack()
button.place(relx=0.5, rely=0.5, anchor=CENTER)
GPSstatus = Label(window, text = "GPS_status: offline")
GPSstatus.place(x=40,y=60)
window.geometry("400x400")
# window.attributes('-fullscreen', True)
window.configure(bg="seashell")
window.mainloop()

