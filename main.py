import pyautogui
import keyboard
import os
import time
import ss_window

def create_dirs():
    docs_folder = os.path.expanduser('~\\Documents') 
    app_folder = docs_folder + "\\Imager"
    images_folder = app_folder + "\\Images"
    temp_folder = app_folder + "\\Temp"
    if not os.path.exists(app_folder):
        os.mkdir(app_folder)
    if not os.path.exists(images_folder):
        os.mkdir(images_folder)
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)
    return app_folder, images_folder, temp_folder

def main():
    _, images_folder, temp_folder = create_dirs()
    
    while True:
        if keyboard.is_pressed('1'): # Full screen shot
            screen = pyautogui.screenshot()
            image_name = f'\\{int(time.time())}.jpg'
            image_path = images_folder + image_name 
            screen.save(image_path)
        if keyboard.is_pressed('2'): # Select a rectangle inside screen shot
            screen = pyautogui.screenshot()
            image_name = f'\\{int(time.time())}.jpg'
            temp_image_path = temp_folder + image_name
            image_path = images_folder + image_name
            screen.save(temp_image_path)
            ss_window.main(temp_image_path, image_path)

if __name__ == "__main__":
    main()