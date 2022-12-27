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
DEFAULT_CAMERA_ANGLE_DEGREES = 90

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.capture_characteristics = {}
        self.mode_options = [
            "none", "negative", "solarise", "sketch", "denoise", "emboss", "oilpaint", "hatch", "gpen", "pastel", "watercolour", "film", "blur", "saturation", "colourswap", "washedout", "posterise", "colourpoint", "colourbalance", "cartoon"
        ]
        self.default_camera_rotation_deg = str(DEFAULT_CAMERA_ANGLE_DEGREES)
        self.capture_path = self.make_path(os.path.abspath(os.path.expandvars(os.path.expanduser(IMAGE_SAVE_DIRECTORY))))+"/"
        self.default_image = os.path.abspath(os.path.dirname(__file__))+"/"+DEFAULT_IMAGE
        self.reset_capture_characteristics()
        self.monitor_width, self.monitor_height = self.winfo_screenwidth(), self.winfo_screenheight()
        print(self.monitor_width, self.monitor_height)

        self.geometry(str(int(self.monitor_width*0.3))+"x"+str(self.monitor_height))
        self.title("Raspberry PI Camera")

        self.frame = customtkinter.CTkFrame(master=self)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.rotate_label = customtkinter.CTkLabel(master=self.frame, justify=tkinter.LEFT, text="Rotate "+self.default_camera_rotation_deg+" deg")
        self.rotate_label.pack(pady=0, padx=10)

        self.rotate_slider = customtkinter.CTkSlider(master=self.frame, command=self.set_rotation, from_=0, to=359, number_of_steps=4, hover=True)
        self.rotate_slider.pack(pady=0, padx=10)
        self.rotate_slider.set(int(self.default_camera_rotation_deg))

        self.mode_options = customtkinter.CTkOptionMenu(self.frame, values=self.mode_options, command=self.set_mode)
        self.mode_options.pack(pady=10, padx=10)
        self.mode_options.set("Modes")

        self.capture_button = customtkinter.CTkButton(master=self.frame, command=self.capture_image, text="Capture Image", corner_radius=90, width=5)
        self.capture_button.pack(pady=10, padx=0)

        self.file_save_location_button = customtkinter.CTkButton(master=self.frame, command=self.file_save_browse_button, text="Save Location", corner_radius=90, width=5)
        self.file_save_location_button.pack(pady=10, padx=0)

        self.status_text = customtkinter.CTkTextbox(master=self.frame, width=int(self.monitor_width*0.3), height=50)
        self.status_text.pack(pady=0, padx=10)
        self.status_text.insert("0.0", "Click Capture to capture an image")
        self.status_text.configure(state="disabled")

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
            "--rotation": self.default_camera_rotation_deg
        }

    def set_rotation(self, value):
        int_value = int(value)
        if int_value >= 0 and int_value < 90:
            int_value = 0
        elif int_value >= 90 and int_value < 180:
            int_value = 90
        elif int_value >= 180 and int_value < 270:
            int_value = 180
        elif int_value >= 270 and int_value < 360:
            int_value = 359
        padded_value = str(int_value).rjust(3, "0")
        self.rotate_label.configure(text="Rotate "+str(int_value)+" deg")
        self.capture_characteristics["--rotation"] = int_value
        self.kill_preview()
        self.start_preview()

    def set_mode(self, value):
        self.capture_characteristics["--imxfx"] = value
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
        textbox.delete("0.0", "100000.0")
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
        self.reset_capture_characteristics()



if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.handle_window_closure)
    app.mainloop()
