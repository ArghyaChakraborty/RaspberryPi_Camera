from abc import ABC, abstractmethod
from PIL import Image, ImageGrab
import subprocess
import time
import os
import sys
import shutil
from threading import Thread

class BaseCameraModule(ABC):
    @abstractmethod
    def kill_preview(self) -> None:
        pass
    
    @abstractmethod
    def start_preview(self, configuration: dict) -> None:
        pass
    
    @abstractmethod
    def capture_image(self, capture_path: str, configuration: dict) -> str:
        pass

class RaspiCameraModule(BaseCameraModule):
    def kill_preview(self) -> None:
        print("RaspiCameraModule.kill_preview")
        try:
            pid = subprocess.check_output(["pidof", "raspistill"])
            pid = pid.decode("utf-8").split("\n")[0]
            subprocess.run("kill -9 "+pid, check=True, shell=True)
        except Exception as ex:
            print("Preview Kill Exception: "+str(ex))

    def start_preview(self, configuration: dict) -> None:
        print("RaspiCameraModule.start_preview")
        try:
            command = "raspistill --keypress "
            for k,v in configuration.items():
                command += str(k)+" "+str(v)+" "
            print("Start Preview Command: "+command)
            subprocess.run(command, check=True, shell=True)
        except Exception as ex:
            print("Preview Exception: "+str(ex))  

    def capture_image(self, capture_path: str, configuration: dict) -> str:
        print("RaspiCameraModule.capture_image")
        image_name = ""
        try:
            milliseconds = int(time.time() * 1000)
            image_name = capture_path + str("image_"+str(milliseconds)+".jpg")
            command = "raspistill --output "+ image_name + " "
            for k,v in configuration.items():
                command += str(k)+" "+str(v)+" "
            print("Capture Command: "+command)
            subprocess.run(command, check=True, shell=True)
        except Exception as ex:
            print("Capture Exception: "+str(ex))
        return image_name

class DummyCameraModule(BaseCameraModule):
    def __init__(self) -> None:
        super().__init__()
        curr_dir = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")
        self.communication_file = curr_dir+"/dummy_camera_module_communication"
        self.default_image_file = curr_dir+"/images/rpi_logo.jpg"
        self.dummy_camera_module_executable = curr_dir+"/mock_raspistill.py"
        self.write_communication_message("start")
        self.python_cmd = "python3" if os.system("python3 --version") == 0 else "python"
        print(str(sys.version_info), self.python_cmd)

    def write_communication_message(self, message: str):
        print("Writing communication message => ", message)
        with open(self.communication_file, "w") as fp:
            fp.write(message)

    def kill_preview(self) -> None:
        print("DummyCameraModule.kill_preview")
        try:
            self.write_communication_message("stop")
            time.sleep(1)
        except Exception as ex:
            print("Kill Preview Exception: "+str(ex))
    
    def start_preview(self, configuration: dict) -> None:
        print("DummyCameraModule.start_preview")
        try:
            self.write_communication_message("start")
            existing_processes = os.system("ps -ef | grep -v grep | grep "+self.dummy_camera_module_executable+" | grep -v grep")
            if existing_processes > 0:
                print("No processes exist, launching new process")
                subprocess.run(
                    self.python_cmd+" "+self.dummy_camera_module_executable+" "+self.default_image_file+" "+self.communication_file+" "+configuration["--preview"], 
                    check=True, shell=True)
            else:
                print("Processes' already running, not launching new ", existing_processes)
        except Exception as ex:
            print("Start Preview Exception: "+str(ex))
    
    def capture_image(self, capture_path: str, configuration: dict) -> str:
        print("DummyCameraModule.capture_image")
        image_name = ""
        try:
            milliseconds = int(time.time() * 1000)
            image_name = capture_path + str("image_"+str(milliseconds)+".jpg")
            shutil.copy(self.default_image_file, image_name)
        except Exception as ex:
            print("Capture Image Exception: "+str(ex))
        return image_name

class CameraModuleFactory:
    @staticmethod
    def get_camera_module(test_flag: bool) -> BaseCameraModule:
        if test_flag:
            return DummyCameraModule()
        else:
            return RaspiCameraModule()
