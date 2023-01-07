from tkinter import *
tosi = False
window = Tk()

def aja():
    print("testi")

def close_window():
    exit()

def aloita_lopeta():
    if button["text"] == "Aloita":
        tosi = True
        aja()
        button.config(text="Lopeta", fg="red")
    else:
        tosi = False
        button.config(text="Aloita", command=close_window(), fg="green")

button = Button(window, text = "Aloita", command = aloita_lopeta, font=("Roboto", 50), bg="lightgrey")
button.pack()
button.place(relx=0.5, rely=0.5, anchor=CENTER)
window.geometry("400x400")
# window.attributes('-fullscreen', True)
window.configure(bg="seashell")
window.mainloop()

