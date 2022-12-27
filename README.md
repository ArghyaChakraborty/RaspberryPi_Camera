# Raspberry Pi Camera App
## Description
This Python `tkinter` app provides some of the camera options provided by Raspberry Pi camera module `raspistill`. So far this app only captures still images. Video capabilities may be supported in future.

## raspistill command help
Please check file [raspistill-help](raspistill-help)

## customtkinter repository
https://github.com/TomSchimansky/CustomTkinter

## Dependencies
- The Raspberry Pi camera should be installed and enabled
- The Raspberry Pi should be connected to a monitor
- Python 3.7+
- Python modules: customtkinter, Pillow

## Starting Raspberry Pi Camera App
- Open a command prompt in Raspberry PI and execute:
`python3 rpi_camera.py`

## Features
- After the app opens, it starts camera preview
- You can adjust camera rotation and also select different modes
- Furthermore, you can adjust brightness, sharpness, contrast and saturation of the image from the app
- When you change any of the settings, the preview gets automatically refreshed
- When satisfied, click on `(Capture Image)` button and the image will be captured
- The image path will be displayed in the status box in `[Captured Images]` tab (default path: ~/Images). You can adjust this path in code OR browse for the image save location via `(Save Location)` button in the app
- The captured image will be displayed in `[Captured Images]` tab. Note: in order to view the actual image, maximize/minimize/format it, you need to visit the image save location and open the image from there. The `[Captured Images]` tab only shows a quick preview of the captured image

## Screenshots
* Note: The screenshots may not be up to date. The latest app may look different from the images captured below  
* Raspberry Pi camera app controls  
  ![Raspberry Pi Camera App](./images/rpi_image0.jpg)  
* Captured image by the app   
  ![Raspberry Pi Camera App](./images/rpi_image1.jpg)  

## Releases
|Release|Date|Features|
|-------|----|--------|
|0.0.1|Dec 26, 2022|Initial Release|
|0.0.2|Dec 27, 2022|Added current image view inside the app; rounded buttons; allowed ability to select image save location; removed padding from rotation text; changed rotation element UI type; added new elements for brightness, sharpness, contrast, saturation; divided elements into two tabs|