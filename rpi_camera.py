#!/usr/bin/python3
import os
import sys
from threading import Thread
from multiprocessing import Process
import copy
import tkinter
from tkinter import messagebox
import customtkinter
from PIL import Image
from camera_modules import CameraModuleFactory

TEST_FLAG = False
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

        # set location of the main window
        self.geometry(str(int(self.monitor_width*0.3))+"x"+str(self.monitor_height)+"+0+0")
        self.title("Raspberry PI Camera")

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, height=self.monitor_height, width=int(self.monitor_width*0.3))
        self.tabview.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.tabview.add("Controls")
        self.tabview.add("Captured Image")
        self.tabview.tab("Controls").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Captured Image").grid_columnconfigure(0, weight=1)


        # set camera angle rotation options
        self.rotation_options = customtkinter.CTkOptionMenu(self.tabview.tab("Controls"), values=self.rotation_option_values, command=self.set_rotation, width=int(self.monitor_width*0.25))
        self.rotation_options.grid(row=0, column=0,pady=10, padx=10)
        self.rotation_options.set("Rotation Degree")

        # set image modes
        self.mode_options = customtkinter.CTkOptionMenu(self.tabview.tab("Controls"), values=self.mode_option_values, command=self.set_mode, width=int(self.monitor_width*0.25))
        self.mode_options.grid(row=1, column=0,pady=10, padx=10)
        self.mode_options.set("Modes")

        # set image sharpness levels
        self.sharpness_label = customtkinter.CTkLabel(master=self.tabview.tab("Controls"), justify=tkinter.LEFT, text="Sharpness: "+self.sharpness, width=int(self.monitor_width*0.25))
        self.sharpness_label.grid(row=2, column=0,pady=0, padx=10)

        self.sharpness_slider = customtkinter.CTkSlider(master=self.tabview.tab("Controls"), command=self.set_sharpness, from_=-100, to=100, number_of_steps=200, hover=True, width=int(self.monitor_width*0.25))
        self.sharpness_slider.grid(row=3, column=0,pady=0, padx=10)
        self.sharpness_slider.set(int(self.sharpness))

        # set image contrast levels
        self.contrast_label = customtkinter.CTkLabel(master=self.tabview.tab("Controls"), justify=tkinter.LEFT, text="Contrast: "+self.contrast, width=int(self.monitor_width*0.25))
        self.contrast_label.grid(row=4, column=0,pady=0, padx=10)

        self.contrast_slider = customtkinter.CTkSlider(master=self.tabview.tab("Controls"), command=self.set_contrast, from_=-100, to=100, number_of_steps=200, hover=True, width=int(self.monitor_width*0.25))
        self.contrast_slider.grid(row=5, column=0,pady=0, padx=10)
        self.contrast_slider.set(int(self.contrast))

        # set image brightness levels
        self.brightness_label = customtkinter.CTkLabel(master=self.tabview.tab("Controls"), justify=tkinter.LEFT, text="Brightness: "+self.brightness, width=int(self.monitor_width*0.25))
        self.brightness_label.grid(row=6, column=0,pady=0, padx=10)

        self.brightness_slider = customtkinter.CTkSlider(master=self.tabview.tab("Controls"), command=self.set_brightness, from_=-100, to=100, number_of_steps=200, hover=True, width=int(self.monitor_width*0.25))
        self.brightness_slider.grid(row=7, column=0,pady=0, padx=10)
        self.brightness_slider.set(int(self.brightness))

        # set image saturation levels
        self.saturation_label = customtkinter.CTkLabel(master=self.tabview.tab("Controls"), justify=tkinter.LEFT, text="Saturation: "+self.saturation, width=int(self.monitor_width*0.25))
        self.saturation_label.grid(row=8, column=0,pady=0, padx=10)

        self.saturation_slider = customtkinter.CTkSlider(master=self.tabview.tab("Controls"), command=self.set_saturation, from_=-100, to=100, number_of_steps=200, hover=True, width=int(self.monitor_width*0.25))
        self.saturation_slider.grid(row=9, column=0,pady=0, padx=10)
        self.saturation_slider.set(int(self.saturation))

        # create image capture button
        self.capture_button = customtkinter.CTkButton(master=self.tabview.tab("Controls"), command=self.capture_image, text="Capture Image", corner_radius=90, width=int(self.monitor_width*0.25))
        self.capture_button.grid(row=10, column=0,pady=10, padx=0)

        # create image save location button
        self.file_save_location_button = customtkinter.CTkButton(master=self.tabview.tab("Controls"), command=self.file_save_browse_button, text="Save Location", corner_radius=90, width=int(self.monitor_width*0.25))
        self.file_save_location_button.grid(row=11, column=0,pady=10, padx=0)

        # create status textbox
        self.status_text = customtkinter.CTkTextbox(master=self.tabview.tab("Captured Image"), width=int(self.monitor_width*0.25), height=50)
        self.status_text.grid(row=0, column=0,pady=0, padx=10)
        self.status_text.insert("0.0", "Click Capture to capture an image")
        self.status_text.configure(state="disabled")

        # create label which displays the current captured image
        self.status_label_image = customtkinter.CTkLabel(master=self.tabview.tab("Captured Image"), justify=tkinter.LEFT, text="", image="", width=int(self.monitor_width*0.25))
        self.status_label_image.grid(row=1, column=0,pady=0, padx=10)

        self.update()
        self.app_width, self.app_height = self.winfo_width(), self.winfo_height()
        self.app_x, self.app_y = self.winfo_x(), self.winfo_y()
        print("Monitor width x height", self.monitor_width, self.monitor_height)
        print("Widget width x height", self.app_width, self.app_height)
        print("Widget X x Y", self.app_x, self.app_y)
        self.camera_module = CameraModuleFactory.get_camera_module(TEST_FLAG)

        # start camera preview
        self.start_preview()

    def handle_window_closure(self):
        self.camera_module.kill_preview()
        self.destroy()

    def kill_preview(self):
        self.camera_module.kill_preview()

    def start_preview(self):
        self.thread = Thread(target=self.__start_preview_thread)
        self.thread.start()

    def __start_preview_thread(self):
        config = copy.deepcopy(self.capture_characteristics)
        preview_width = int(self.monitor_width - self.app_width)
        preview_start_x = self.app_x + self.app_width
        config["--preview"] = "'"+str(preview_start_x)+",0,"+str(preview_width)+","+str(self.monitor_height)+"'"
        self.camera_module.start_preview(config) 

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
        self.provide_confirmation("Success", "Images will be saved at: "+self.capture_path)

    def change_textbox_text(self, textbox: customtkinter.CTkTextbox, new_text: str):
        textbox.configure(state="normal")
        textbox.delete("0.0", "end")
        textbox.insert("0.0", new_text)
        textbox.configure(state="disabled")

    def capture_image(self):
        config = copy.deepcopy(self.capture_characteristics)
        self.kill_preview()
        image_path = self.camera_module.capture_image(self.capture_path, config)
        disk_image = Image.open(image_path).resize((int(self.monitor_width*0.25), int(self.monitor_width*0.25)))
        img = customtkinter.CTkImage(disk_image, size=(int(self.monitor_width*0.25), int(self.monitor_width*0.25)))
        self.change_textbox_text(self.status_text, image_path)
        self.status_label_image.configure(image=img)
        self.provide_confirmation("Success", "Image Captured. Check Captured Image tab")
        self.start_preview()

    def provide_confirmation(self, title: str, message: str):
        confirmation_dialog = messagebox.showinfo(title=title, message=message)


if __name__ == "__main__":
    if len(sys.argv) > 1 and "test" in sys.argv[1].lower():
        TEST_FLAG = True
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.handle_window_closure)
    app.mainloop()

