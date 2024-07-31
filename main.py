import keyboard
import os
import time
import configparser
from os import path
from datetime import date
import tkinter.messagebox
import tkinter as tk
import psycopg2 as pg
from PIL import Image, ImageTk, ImageGrab
import requests
from win32gui import GetWindowText, GetForegroundWindow
import time
import webbrowser

def popup_message(message: str):
    tkinter.messagebox.showinfo("",message) 

class API:
    validate_user_url: str
    upload_img_url: str
    api_key: str
    def __init__(self):
        self.validate_user_url = 'https://imager.site/imager/api/validate_user/'
        self.upload_img_url = 'https://imager.site/imager/api/upload_img/'
        
    def login(self, username: str, password: str) -> int:
        data = {'username': username, 'password': password}
        response = requests.post(url = self.validate_user_url, data=data)
        return response
    
    def upload_img(self, username: str, password: str, is_private: bool, description: str, image) -> int:
        data = {'username': username, 'password': password, 'is_private': is_private, 'description': description}
        response = requests.post(url = self.upload_img_url, data=data, files={'image': image})
        return response
        
class DrawRectangle:
    id: int
    image: Image
    canvas: tk.Canvas
    x1: int
    y1: int
    x2: int
    y2: int
    def __init__(self, canvas:tk.Canvas, image: Image):
        self.image = image
        self.canvas = canvas
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.id = None
        
    def update_start_point(self, mouse: tk.Event):
        self.x1 = mouse.x
        self.y1 = mouse.y
        
    def update_end_point(self, mouse: tk.Event):
        self.x2 = mouse.x
        self.y2 = mouse.y
        self.__update_rect()

    def get_rect(self) -> Image:
        cropped_img = self.image.crop(self.canvas.coords(self.id))
        return cropped_img
    
    def __update_rect(self):
        self.canvas.coords(self.id, self.x1, self.y1, self.x2, self.y2)
      
class AppDirs:
    user_docs_dir: str
    app_dir: str
    images_dir: str
    settings_dir: str
    def __init__(self):
        self.user_docs_dir = os.path.expanduser('~/Documents')
        self.app_dir = self.user_docs_dir + "/Imager"
        self.images_dir = self.app_dir + "/Images"
        self.settings_dir = self.app_dir + "/Settings"
        self.__check_dirs()
    
    def __check_dirs(self):
        self.__check_dir(self.app_dir)
        self.__check_dir(self.images_dir)
        self.__check_dir(self.settings_dir)
        
    def __check_dir(self, dir):
        if not os.path.exists(dir):
            os.mkdir(dir)
            
class User:
    logged_in: bool
    username: str
    _password: str
    def __init__(self):
        self.logged_in = False
        self.username = None
        self._password = None
        
    def login(self, username: tk.StringVar, password: tk.StringVar):
        api = API()
        self.username = username.get()
        self._password = password.get()
        response: requests.Response = api.login(self.username, self._password)
        match response.status_code:
            case 200:
                self.logged_in = True
                popup_message("Login successful!")
            case 401:
                popup_message("Incorrect username or password!")
            case _:
                popup_message("Something is wrong")
        
class EditableImageWindow:
    image: Image
    image_path: str
    def __init__(self, image: Image, image_path: str):
        self.image = image
        self.image_path = image_path
        self.__init_ui()
    
    def __init_ui(self):
        self.window = tk.Tk()
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)

        canvas = tk.Canvas(self.window, width=self.image.size[0], height=self.image.size[1], borderwidth=0, highlightthickness=0)
        canvas.pack(expand=True)
        image = ImageTk.PhotoImage(self.image)
        canvas.create_image(0, 0, image=image, anchor=tk.NW)
        
        self.rect = DrawRectangle(canvas, self.image)
        self.rect.id = canvas.create_rectangle(self.rect.x1, self.rect.y1, self.rect.x2, self.rect.y2, dash=(2,2), fill='', outline='red')

        canvas.bind('<Button-1>', lambda event: self.__button1(event))
        canvas.bind('<B1-Motion>', lambda event: self.__button1_motion(event))
        canvas.bind('<ButtonRelease-1>', lambda event: self.__button1_release())

        self.window.mainloop()
    
    def __button1(self, event: tk.Event):
        self.rect.update_start_point(event)
    
    def __button1_motion(self, event: tk.Event):
        self.rect.update_end_point(event)
    
    def __button1_release(self):
        rect_image = self.rect.get_rect()
        rect_image.save(self.image_path)
        self.window.destroy()

class LoginWindow:
    username: tk.StringVar
    _password: tk.StringVar
    user: User
    def __init__(self):
        self.user = User()
        self.__init_ui()
    
    def __init_ui(self):
        ratio = 35
        self.window = tk.Tk()
        self.window.resizable(False, False)
        width, height = 16*ratio, 9*ratio
        x = (self.window.winfo_screenwidth()//2)-(width//2)
        y = (self.window.winfo_screenheight()//2)-(height//2)
        self.window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        canvas = tk.Canvas(self.window, width=width, height=height, borderwidth=0, highlightthickness=0)
        canvas.pack(expand=True)
        self.username = tk.StringVar()
        self._password= tk.StringVar()
        login_label = tk.Label(canvas, text='Login', font=('Arial', 25)).place(x=220, y=50)
        login_username_label = tk.Label(canvas, text='Username', font=('Arial', 15)).place(x=220, y=100)
        login_username_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=self.username).place(x=150, y=130)
        login_password_label = tk.Label(canvas, text='Password', font=('Arial', 15)).place(x=220, y=170)
        login_password_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=self._password, show='*').place(x=150, y=200)
        login_button = tk.Button(canvas, text='Login', command=self.__login_button, width=31).place(x=150, y=240)
        register_button = tk.Button(canvas, text='Register', command=self.__register_button, width=31).place(x=150, y=270)
        self.window.mainloop()    
    
    def __register_button(self):
        webbrowser.open('https://imager.site/imager/register/')
    
    def __login_button(self):
        self.user.login(self.username, self._password)
        if self.user.logged_in:
            self.window.destroy()
    
class SettingsWindow:
    settings: configparser.ConfigParser
    settings_path: str
    storage_local: int 
    storage_db: int 
    is_private: int 
    screen_shot: str 
    screen_shot_edit: str 
    settings_window: str 
    def __init__(self):
        self.settings = configparser.ConfigParser()
        self.settings_path = f'{AppDirs().settings_dir}/settings.ini'
        self.__generate_default_settings()
        self.__init_settings()
        self.__init_ui()
        
    def __init_ui(self):
        ratio = 50
        self.window = tk.Tk()
        self.window.resizable(False, False)
        width, height = 16*ratio, 9*ratio
        x = (self.window.winfo_screenwidth()//2)-(width//2)
        y = (self.window.winfo_screenheight()//2)-(height//2)
        self.window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        canvas = tk.Canvas(self.window, width=width, height=height, borderwidth=0, highlightthickness=0)
        canvas.pack(expand=True)
        
        check_button_local_var = tk.IntVar(value=self.storage_local)
        check_button_local = tk.Checkbutton(canvas, text='Store locally',variable=check_button_local_var, onvalue=1, offvalue=0, command= lambda: self.__change_setting('Storage', 'Local', str(check_button_local_var.get()))).place(x=50, y=50)
        
        check_button_db_var = tk.IntVar(value=self.storage_db)
        check_button_db = tk.Checkbutton(canvas, text='Store in Database',variable=check_button_db_var, onvalue=1, offvalue=0, command= lambda: self.__change_setting('Storage', 'Db', str(check_button_db_var.get()))).place(x=50, y=70)
        
        check_button_private_var = tk.IntVar(value=self.is_private)
        check_button_private = tk.Checkbutton(canvas, text='Private',variable=check_button_private_var, onvalue=1, offvalue=0, command= lambda: self.__change_setting('Storage', 'is_private', str(check_button_private_var.get()))).place(x=50, y=90)
        
        self.screen_shot_var = tk.StringVar(value=self.screen_shot)
        screen_shot_label = tk.Label(canvas, text='Keybind to screen shot').place(x=180, y=115)
        screen_shot_entry = tk.Entry(canvas, textvariable=self.screen_shot_var).place(x=55, y=115)
        
        self.screen_shot_edit_var = tk.StringVar(value=self.screen_shot_edit)
        screen_shot_edit_label = tk.Label(canvas, text='Keybind to screen shot and edit').place(x=180, y=140)
        screen_shot_edit_entry = tk.Entry(canvas, textvariable=self.screen_shot_edit_var).place(x=55, y=140)
        
        self.settings_window_var = tk.StringVar(value=self.settings_window)
        settings_window_label = tk.Label(canvas, text='Keybind to open settings window').place(x=180, y=165)
        settings_window_entry = tk.Entry(canvas, textvariable=self.settings_window_var).place(x=55, y=165)
        
        save_button = tk.Button(canvas, text='Save changes', command=self.__save_keybind_changes).place(x=50, y=300)
        
        self.window.mainloop()
        
    def __save_keybind_changes(self):
        keybind_changes = [
            ('KeyBinds', 'settings_window', self.settings_window_var.get()),
            ('KeyBinds', 'screen_shot', self.screen_shot_var.get()),
            ('KeyBinds', 'screen_shot_edit', self.screen_shot_edit_var.get())
        ]
        for keybind_change in keybind_changes:
            self.__change_setting(keybind_change[0], keybind_change[1], keybind_change[2])
    
    def __change_setting(self, section, key, value):
        self.settings.set(section, key, value)
        with open(self.settings_path, 'w') as f:
            self.settings.write(f)
        self.__init_settings()
    
    def __init_settings(self):
        self.storage_local = self.settings.getint('Storage', 'local')
        self.storage_db = self.settings.getint('Storage', 'db')
        self.is_private = self.settings.getint('Storage', 'is_private')
        self.screen_shot = self.settings.get('KeyBinds', 'screen_shot')
        self.screen_shot_edit = self.settings.get('KeyBinds', 'screen_shot_edit')
        self.settings_window = self.settings.get('KeyBinds', 'settings_window')
    
    def __generate_default_settings(self):
        if os.path.exists(self.settings_path):
            self.settings.read(self.settings_path)
            return
        self.settings['Storage'] = {'local': '1',
                                    'db': '0',
                                    'is_private': '1'}
        self.settings['KeyBinds'] = {'screen_shot': 'ctrl+1',
                                    'screen_shot_edit': 'ctrl+2',
                                    'settings_window': 'ctrl+3'}
        with open(self.settings_path, 'w') as settingsfile:
            self.settings.write(settingsfile)
        self.settings.read(self.settings_path)

class HotKey:
    def __init__(self):
        pass
    
    def screen_shot(self, app_dirs: AppDirs, settings: SettingsWindow, username, password): # Full screen shot
        screen = ImageGrab.grab()
        image_name = f'\\{int(time.time())}.jpg'
        image_path = app_dirs.images_dir + image_name
        if settings.storage_local:
            screen.save(image_path)
        if settings.storage_db:
            screen.save(image_path)
            api = API()
            with open(image_path, 'rb') as img:
                response = api.upload_img(username, password, bool(settings.is_private), GetWindowText(GetForegroundWindow()), img)
                img.close()
            if not settings.storage_local:
                os.remove(image_path)
    
    def screen_shot_edit(self, app_dirs: AppDirs, settings: SettingsWindow, username, password): # Select a rectangle inside screen shot
        screen = ImageGrab.grab()
        image_name = f'\\{int(time.time())}.jpg'
        image_path = app_dirs.images_dir + image_name
        EditableImageWindow(screen, image_path)
        api = API()
        with open(image_path, 'rb') as img:
            api.upload_img(username, password, bool(settings.is_private), GetWindowText(GetForegroundWindow()), img)
            img.close()
        if not settings.storage_local:
            os.remove(image_path)
    
def main():
    login_window = LoginWindow()
    if login_window.user.logged_in:
        app_dirs = AppDirs()
        settings = SettingsWindow()
        hot_key = HotKey()
        keyboard.add_hotkey(settings.settings_window, lambda: SettingsWindow())
        keyboard.add_hotkey(settings.screen_shot_edit, lambda: hot_key.screen_shot_edit(app_dirs, settings, login_window.user.username, login_window.user._password))
        keyboard.add_hotkey(settings.screen_shot, lambda: hot_key.screen_shot(app_dirs, settings, login_window.user.username, login_window.user._password))
        keyboard.wait()
    
if __name__ == "__main__":
    main()