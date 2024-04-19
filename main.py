import pyautogui
import keyboard
import os
import time
import configparser
from os import path
from datetime import date
import tkinter as tk
import psycopg2 as pg
from PIL import Image, ImageTk

def popup_message(message: str):
    window = tk.Tk()
    window.resizable(False, False)
    window.attributes('-topmost', True)
    canvas = tk.Canvas(window, borderwidth=0, highlightthickness=0)
    canvas.pack(expand=True)
    label = tk.Label(canvas, text=message, font=('Arial', 15), wraplength=300).grid()
    window.mainloop()


class DB:
    __config = configparser.ConfigParser()
    __path_to_config = path.abspath(path.join(path.dirname(__file__), 'config.ini'))
    __config.read(__path_to_config)
    def __init__(self) -> None:
        self.__init_values()
        self.__init_connection()
        self.__init_tables()
    
    def __init_tables(self) -> None:
        self.__create_user()
        self.__create_image()
    
    def __init_values(self) -> None:
        self.__host: str = self.__config.get('Default', 'Host')
        self.__dbname: str = self.__config.get('Default', 'DbName')
        self.__user: str = self.__config.get('Default', 'User')
        self.__password: str = self.__config.get('Default', 'Password')
        self.__port: int = int(self.__config.get('Default', 'Port'))
    
    def __init_connection(self) -> None:
        self.__conn = pg.connect(host=self.__host, dbname=self.__dbname, user=self.__user, password=self.__password, port=self.__port)
        self.__cur = self.__conn.cursor()
    
    def __del__(self) -> None:
        self.__cur.close()
        self.__conn.close()
    
    def add_row_image(self, data: bytearray, name: str, date: date) -> None:
        self.__cur.execute('''INSERT INTO image (data, name, date) VALUES (%s, %s, %s)''', (data, name, date))
        self.__conn.commit()
    
    def add_row_user(self, username: str, password: str) -> None:
        self.__cur.execute('''INSERT INTO users (username, password) VALUES (%s, %s)''', (username, password))
        self.__conn.commit()
    
    def __create_image(self) -> None:
        self.__cur.execute('''CREATE TABLE IF NOT EXISTS image (
            id SERIAL PRIMARY KEY,
            data BYTEA,
            name VARCHAR(255),
            date DATE
            );
            ''')
        self.__conn.commit()
        
        
    def __create_user(self) -> None:
        self.__cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255),
            password VARCHAR(255)
            );
            ''')
        self.__conn.commit()


class ImageRectangle:
    id: int = None
    img_path: str = None
    temp_img_path: str = None
    window: tk.Tk = None
    image_canvas: tk.Canvas = None
    
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1: int = x1
        self.y1: int = y1
        self.x2: int = x2
        self.y2: int = y2
        
    def update_start_point(self, mouse):
        self.x1 = mouse.x
        self.y1 = mouse.y
        
    def update_end_point(self, mouse):
        self.x2 = mouse.x
        self.y2 = mouse.y
        self.__update_rect()

    def save_rect(self):
        img = Image.open(self.temp_img_path)
        cropped_img = img.crop(self.image_canvas.coords(self.id))
        cropped_img.save(self.img_path)
        os.remove(self.temp_img_path)
        self.window.destroy()
    
    def __update_rect(self):
        self.image_canvas.coords(self.id, self.x1, self.y1, self.x2, self.y2)
      
        
class AppDirs:
    def __init__(self) -> None:
        self.user_docs_dir: str = os.path.expanduser('~\\Documents')
        self.app_dir = self.user_docs_dir + "\\Imager"
        self.images_dir = self.app_dir + "\\Images"
        self.temp_dir = self.app_dir + "\\Temp"
        self.__check_dirs()
    
    def __check_dirs(self):
        self.__check_dir(self.app_dir)
        self.__check_dir(self.images_dir)
        self.__check_dir(self.temp_dir)
        
    def __check_dir(self, dir):
        if not os.path.exists(dir):
            os.mkdir(dir)
            
   
class User:
    username : str = None
    __password : str = None
    def __init__(self):
        self.db = DB()
        
    def __del__(self):
        del self.db
    
    def register(self, username: tk.StringVar, password: tk.StringVar, confirm_password: tk.StringVar):
        if not self.__username_rules(username.get()):
            return None
        if not self.__password_rules(password.get(), confirm_password.get()):
            return None
        self.username = username.get()
        self.__hash_password(password.get())
        self.db.add_row_user(self.username, self.__password)
    
    def __username_rules(self, username: str) -> bool:
        min_length = 3
        max_length = 10
        illegal_chars = ',/;[]<>()-=+!@#$%^&*'
        if len(username) < min_length:
            popup_message(f'Username is too short. Minimum length is {min_length}')
            return False
        if len(username) > max_length:
            popup_message(f'Username is too long. Maximum length is {max_length}')
            return False
        for char in illegal_chars:
            if char in username:
                popup_message(f'Username contains an illegal character "{char}"')
                return False
        return True
    
    def __password_rules(self, password: str, confirm_password: str) -> bool:
        min_length = 5
        max_length = 15
        if len(password) < min_length:
            popup_message(f'Username is too short. Minimum length is {min_length}')
            return False
        if len(password) > max_length:
            popup_message(f'Username is too long. Maximum length is {max_length}')
            return False
        if password != confirm_password:
            popup_message(f'Passwords do not match')
            return False
        return True
    
    def __hash_password(self, password: str):
        from hashlib import sha256
        self.__password = sha256(password.encode('utf-8')).hexdigest()
        
    
def create_window(temp_path, path):
    rect = ImageRectangle(0, 0, 0, 0)
    rect.temp_img_path = temp_path
    rect.img_path = path

    window = tk.Tk()
    window.attributes('-fullscreen', True)
    window.attributes('-topmost', True)

    img = ImageTk.PhotoImage(Image.open(temp_path))
    canvas = tk.Canvas(window, width=img.width(), height=img.height(), borderwidth=0, highlightthickness=0)
    canvas.pack(expand=True)
    canvas.create_image(0, 0, image=img, anchor=tk.NW)
    
    rect.image_canvas = canvas
    rect.window = window
    rect.id = canvas.create_rectangle(rect.x1, rect.y1, rect.x2, rect.y2, dash=(2,2), fill='', outline='red')
    
    canvas.bind('<Button-1>', lambda event: rect.update_start_point(event))
    canvas.bind('<B1-Motion>', lambda event: rect.update_end_point(event))
    canvas.bind('<ButtonRelease-1>', lambda event: rect.save_rect())

    window.mainloop()


def login_window(window_to_close: tk.Tk = None):
    if window_to_close != None:
        window_to_close.destroy()
    ratio = 35
    window = tk.Tk()
    window.resizable(False, False)
    width, height = 16*ratio, 9*ratio
    
    canvas = tk.Canvas(window, width=width, height=height, borderwidth=0, highlightthickness=0)
    canvas.pack(expand=True)
    
    user = User()
    username = tk.StringVar()
    password = tk.StringVar()
    login_label = tk.Label(canvas, text='Login', font=('Arial', 25)).place(x=220, y=50)
    login_username_label = tk.Label(canvas, text='Username', font=('Arial', 15)).place(x=220, y=100)
    login_username_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=username).place(x=150, y=130)
    login_password_label = tk.Label(canvas, text='Password', font=('Arial', 15)).place(x=220, y=170)
    login_password_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=password, show='*').place(x=150, y=200)
    login_button = tk.Button(canvas, text='Login', command=lambda : User.register(username, password), width=31).place(x=150, y=240)
    register_button = tk.Button(canvas, text='Register', command=lambda : register_window(window), width=31).place(x=150, y=270)
    
    window.mainloop()
    
    
def register_window(window_to_close: tk.Tk = None):
    if window_to_close != None:
        window_to_close.destroy()
    ratio = 50
    window = tk.Tk()
    window.resizable(False, False)
    width, height = 16*ratio, 9*ratio
    
    canvas = tk.Canvas(window, width=width, height=height, borderwidth=0, highlightthickness=0)
    canvas.pack(expand=True)
    
    user = User()
    username = tk.StringVar()
    password = tk.StringVar()
    confirm_password = tk.StringVar()
    label = tk.Label(canvas, text='Register', font=('Arial', 25)).place(x=325, y=20)
    username_label = tk.Label(canvas, text='Username', font=('Arial', 15)).place(x=345, y=70)
    username_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=username).place(x=275, y=100)
    password_label = tk.Label(canvas, text='Password', font=('Arial', 15)).place(x=345, y=140)
    password_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=password, show='*').place(x=275, y=170)
    confirm_password_label = tk.Label(canvas, text='Confirm Password', font=('Arial', 15)).place(x=305, y=210)
    confirm_password_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=confirm_password, show='*').place(x=275, y=240)
    register_button = tk.Button(canvas, text='Register', command=lambda : user.register(username, password, confirm_password), width=31).place(x=275, y=280)
    login_button = tk.Button(canvas, text='Login', command=lambda : login_window(window), width=31).place(x=275, y=310)
    
    window.mainloop()


def main():
    register_window()
    #app_dirs = AppDirs()
    #db = DB()
    #with open("C:\\Users\\Aironas\\Documents\\Imager\\Images\\1713174697.jpg", "rb") as image:
    #    f = image.read()
    #    b = bytearray(f)
    #db.add_row_image(b, "asd", date.today())
    #del db
    
    #while True:
    #    if keyboard.is_pressed('1'): # Full screen shot
    #        screen = pyautogui.screenshot()
    #        image_name = f'\\{int(time.time())}.jpg'
    #        image_path = app_dirs.images_dir + image_name 
    #        screen.save(image_path)
    #    if keyboard.is_pressed('2'): # Select a rectangle inside screen shot
    #        screen = pyautogui.screenshot()
    #        image_name = f'\\{int(time.time())}.jpg'
    #        temp_image_path = app_dirs.temp_dir + image_name
    #        image_path = app_dirs.images_dir + image_name
    #        screen.save(temp_image_path)
    #        create_window(temp_image_path, image_path)

if __name__ == "__main__":
    main()