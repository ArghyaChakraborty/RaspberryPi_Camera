#!/usr/bin/python3
import os
import time
import subprocess
from subprocess import check_output
from threading import Thread
import tkinter
import customtkinter
from PIL import Image

IMAGE_SAVE_DIRECTORY = "~/Images/"
DEFAULT_IMAGE = "images/rpi_logo.jpg"
DEFAULT_TIMER_MS = 500
DEFAULT_CAMERA_ANGLE_DEGREES = 90
DEFAULT_SHARPNESS = 0
DEFAULT_CONTRAST = 0
DEFAULT_BRIGHTNESS = 50
DEFAULT_SATURATION = 0

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

'''
-w, --width	: Set image width <size> X
-h, --height	: Set image height <size> X

-t, --timeout	: Time (in ms) before takes picture and shuts down (if not specified, set to 5s)

-sh, --sharpness	: Set image sharpness (-100 to 100) X
-co, --contrast	: Set image contrast (-100 to 100) X
-br, --brightness	: Set image brightness (0 to 100) X
-sa, --saturation	: Set image saturation (-100 to 100)

'''

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # declare class variables
        self.capture_characteristics = {}
        self.mode_option_values = [
            "none", "negative", "solarise", "sketch", "denoise", "emboss", "oilpaint", "hatch", "gpen", "pastel", "watercolour", "film", "blur", "saturation", "colourswap", "washedout", "posterise", "colourpoint", "colourbalance", "cartoon"
        ]
        self.rotation_option_values = ["0", "90", "180", "270", "360"]
        self.camera_rotation_deg = str(DEFAULT_CAMERA_ANGLE_DEGREES)
        self.sharpness = str(DEFAULT_SHARPNESS)
        self.contrast = str(DEFAULT_CONTRAST)
        self.brightness = str(DEFAULT_BRIGHTNESS)
        self.saturation = str(DEFAULT_SATURATION)
        self.capture_path = self.make_path(os.path.abspath(os.path.expandvars(os.path.expanduser(IMAGE_SAVE_DIRECTORY))))+"/"
        self.default_image = os.path.abspath(os.path.dirname(__file__))+"/"+DEFAULT_IMAGE
        self.reset_capture_characteristics()
        self.monitor_width, self.monitor_height = self.winfo_screenwidth(), self.winfo_screenheight()
        print(self.monitor_width, self.monitor_height)

        # set location of the main window
        self.geometry(str(int(self.monitor_width*0.3))+"x"+str(self.monitor_height))
        self.title("Raspberry PI Camera")

        # create the main frame on which other elements will be rendered
        self.frame = customtkinter.CTkFrame(master=self)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)


        '''self.canvas = tkinter.Canvas(self.frame, bg = "black", confine=False, borderwidth= 0, height=self.monitor_height, width=int(self.monitor_width*0.3))
        self.canvas.pack()'''


        # set camera angle rotation options
        self.rotation_options = customtkinter.CTkOptionMenu(self.frame, values=self.rotation_option_values, command=self.set_rotation)
        self.rotation_options.pack(pady=10, padx=10)
        self.rotation_options.set("Rotation Degree")

        # set image modes
        self.mode_options = customtkinter.CTkOptionMenu(self.frame, values=self.mode_option_values, command=self.set_mode)
        self.mode_options.pack(pady=10, padx=10)
        self.mode_options.set("Modes")

        # set image sharpness levels
        self.sharpness_label = customtkinter.CTkLabel(master=self.frame, justify=tkinter.LEFT, text="Sharpness: "+self.sharpness)
        self.sharpness_label.pack(pady=0, padx=10)

        self.sharpness_slider = customtkinter.CTkSlider(master=self.frame, command=self.set_sharpness, from_=-100, to=100, number_of_steps=200, hover=True)
        self.sharpness_slider.pack(pady=0, padx=10)
        self.sharpness_slider.set(int(self.sharpness))

        # set image contrast levels
        self.contrast_label = customtkinter.CTkLabel(master=self.frame, justify=tkinter.LEFT, text="Contrast: "+self.contrast)
        self.contrast_label.pack(pady=0, padx=10)

        self.contrast_slider = customtkinter.CTkSlider(master=self.frame, command=self.set_contrast, from_=-100, to=100, number_of_steps=200, hover=True)
        self.contrast_slider.pack(pady=0, padx=10)
        self.contrast_slider.set(int(self.contrast))

        # set image brightness levels
        self.brightness_label = customtkinter.CTkLabel(master=self.frame, justify=tkinter.LEFT, text="Brightness: "+self.brightness)
        self.brightness_label.pack(pady=0, padx=10)

        self.brightness_slider = customtkinter.CTkSlider(master=self.frame, command=self.set_brightness, from_=-100, to=100, number_of_steps=200, hover=True)
        self.brightness_slider.pack(pady=0, padx=10)
        self.brightness_slider.set(int(self.brightness))

        # set image saturation levels
        self.saturation_label = customtkinter.CTkLabel(master=self.frame, justify=tkinter.LEFT, text="Saturation: "+self.saturation)
        self.saturation_label.pack(pady=0, padx=10)

        self.saturation_slider = customtkinter.CTkSlider(master=self.frame, command=self.set_saturation, from_=-100, to=100, number_of_steps=200, hover=True)
        self.saturation_slider.pack(pady=0, padx=10)
        self.saturation_slider.set(int(self.saturation))

        # create image capture button
        self.capture_button = customtkinter.CTkButton(master=self.frame, command=self.capture_image, text="Capture Image", corner_radius=90, width=5)
        self.capture_button.pack(pady=10, padx=0)

        # create image save location button
        self.file_save_location_button = customtkinter.CTkButton(master=self.frame, command=self.file_save_browse_button, text="Save Location", corner_radius=90, width=5)
        self.file_save_location_button.pack(pady=10, padx=0)

        # create status textbox
        self.status_text = customtkinter.CTkTextbox(master=self.frame, width=int(self.monitor_width*0.3), height=50)
        self.status_text.pack(pady=0, padx=10)
        self.status_text.insert("0.0", "Click Capture to capture an image")
        self.status_text.configure(state="disabled")

        # create label which displays the current captured image
        self.status_label_image = customtkinter.CTkLabel(master=self.frame, justify=tkinter.LEFT, text="", image="")
        self.status_label_image.pack(pady=0, padx=10)

        self.start_preview()

    def handle_window_closure(self):
        self.kill_preview()
        self.destroy()

    def kill_preview(self):
        try:
            pid = check_output(["pidof", "raspistill"])
            pid = pid.decode("utf-8").split("\n")[0]
            process_instance = subprocess.run("kill -9 "+pid, check=True, shell=True)
        except Exception as ex:
            print("Preview Kill Exception: "+str(ex))

    def start_preview(self):
        self.thread = Thread(target=self.__start_preview_thread)
        self.thread.start()

    def __start_preview_thread(self):
        try:
            preview_width = int(self.monitor_width*0.65)
            preview_start_x = self.monitor_width - preview_width
            command = "raspistill --preview '"+str(preview_start_x)+",0,"+str(preview_width)+","+str(self.monitor_height)+"' --keypress "
            for k,v in self.capture_characteristics.items():
                command += str(k)+" "+str(v)+" "
            print("Camera command: "+command)
            process_instance = subprocess.run(command, check=True, shell=True)
        except Exception as ex:
            print("Preview Exception: "+str(ex))      

    def make_path(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def reset_capture_characteristics(self):
        self.capture_characteristics = {
            "--timeout": DEFAULT_TIMER_MS,
            "--rotation": self.camera_rotation_deg,
            "--sharpness": int(self.sharpness),
            "--contrast": int(self.contrast),
            "--brightness": int(self.brightness),
            "--saturation": int(self.saturation)
        }

    def set_rotation(self, value):
        self.capture_characteristics["--rotation"] = value
        self.kill_preview()
        self.start_preview()

    def set_mode(self, value):
        self.capture_characteristics["--imxfx"] = value
        self.kill_preview()
        self.start_preview()

    def set_sharpness(self, value):
        self.capture_characteristics["--sharpness"] = str(int(value))
        self.sharpness_label.configure(text="Sharpness: "+str(int(value)))
        self.kill_preview()
        self.start_preview()

    def set_contrast(self, value):
        self.capture_characteristics["--contrast"] = str(int(value))
        self.contrast_label.configure(text="Contrast: "+str(int(value)))
        self.kill_preview()
        self.start_preview()

    def set_brightness(self, value):
        self.capture_characteristics["--brightness"] = str(int(value))
        self.brightness_label.configure(text="Brightness: "+str(int(value)))
        self.kill_preview()
        self.start_preview()

    def set_saturation(self, value):
        self.capture_characteristics["--saturation"] = str(int(value))
        self.saturation_label.configure(text="Saturation: "+str(int(value)))
        self.kill_preview()
        self.start_preview()

    def file_save_browse_button(self):
        from tkinter import filedialog
        dirname = filedialog.askdirectory()
        print(dirname)
        self.capture_path = os.path.abspath(os.path.expandvars(os.path.expanduser(dirname)))+"/"
        self.change_textbox_text(self.status_text, "Image save path: "+self.capture_path)

    def change_textbox_text(self, textbox: customtkinter.CTkTextbox, new_text: str):
        textbox.configure(state="normal")
        textbox.delete("0.0", "end")
        textbox.insert("0.0", new_text)
        textbox.configure(state="disabled")

    def capture_image(self):
        print(self.capture_characteristics)
        milliseconds = int(time.time() * 1000)
        image_name = str("image_"+str(milliseconds)+".jpg")
        try:
            command = "raspistill --output "+self.capture_path + image_name+" "
            for k,v in self.capture_characteristics.items():
                command += str(k)+" "+str(v)+" "
            print("Camera command: "+command)
            self.kill_preview()
            process_instance = subprocess.run(command, check=True, shell=True)

            disk_image = Image.open(self.capture_path + image_name).resize((int(self.monitor_width*0.3), int(self.monitor_width*0.3)))
            img = customtkinter.CTkImage(disk_image, size=(int(self.monitor_width*0.3), int(self.monitor_width*0.3)))

            self.change_textbox_text(self.status_text, self.capture_path + image_name)
            self.status_label_image.configure(image=img)

            self.start_preview()
        except Exception as ex:
            print("Exception: "+str(ex))



if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.handle_window_closure)
    app.mainloop()
