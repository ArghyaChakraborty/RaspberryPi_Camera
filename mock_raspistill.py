#!/usr/bin/python3
import os
import sys
from PIL import Image
import tkinter
import customtkinter

filename = sys.argv[1]
communication_file = sys.argv[2]
coordinates = sys.argv[3].strip("'").split(",")
x = int(coordinates[0])
y = int(coordinates[1])
width = int(coordinates[2])
height = int(coordinates[3])
flag = True

def callback(app):
    global flag
    app.destroy()
    if os.path.exists(communication_file):
        with open(communication_file, "r") as fp:
            content = fp.read()
            if content.strip() == "stop":
                flag = False

while flag:
    app = customtkinter.CTk()
    geometry = str(height)+"x"+str(width)+"+"+str(x)+"+"+str(y)
    app.geometry(geometry)
    print("geometry ", geometry)

    disk_image = Image.open(filename).resize((int(height), int(width)))
    disk_image.load()
    disk_image = disk_image.convert('RGB')

    img = customtkinter.CTkImage(disk_image, size=(int(height), int(width)))
    status_label_image = customtkinter.CTkLabel(master=app, justify=tkinter.LEFT, text="", image=img)
    status_label_image.pack(pady=0, padx=0)
    app.after(1000, lambda: callback(app))
    app.mainloop()
