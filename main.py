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

def popup_message(message: str):
    tkinter.messagebox.showinfo("",message) 

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
    
    def add_row_user(self, username: str, password: str):
        self.__cur.execute('''INSERT INTO users (username, password) VALUES (%s, %s)''', (username, password))
        self.__conn.commit()
        
    def check_user_exists(self, username: str, password: str) -> bool:
        self.__cur.execute('''SELECT username, password
            FROM users
            WHERE username = (%s) AND password = (%s)
            ''', (username, password))
        if self.__cur.fetchall() == []:
            return False
        else:
            return True
    
    def __create_image(self):
        self.__cur.execute('''CREATE TABLE IF NOT EXISTS image (
            id SERIAL PRIMARY KEY,
            data BYTEA,
            name VARCHAR(255),
            date DATE
            );
            ''')
        self.__conn.commit()
        
        
    def __create_user(self):
        self.__cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255),
            password VARCHAR(255)
            );
            ''')
        self.__conn.commit()

class DrawRectangle:
    id: int = None
    def __init__(self, window: tk.Tk, canvas:tk.Canvas, image: Image):
        self.window = window
        self.image: Image = image
        self.canvas = canvas
        self.x1: int = 0
        self.y1: int = 0
        self.x2: int = 0
        self.y2: int = 0
        
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
    def __init__(self):
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
    logged_in: bool = False
    username: str = None
    __password: str = None
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
        popup_message("Account created!")
        
    def login(self, username: tk.StringVar, password: tk.StringVar):
        if not self.__username_rules(username.get()):
            return None
        self.username = username.get()
        self.__hash_password(password.get())
        if self.db.check_user_exists(self.username, self.__password):
            self.logged_in = True
            popup_message("Login successful!")
        else:
            popup_message("Incorrect username or password!")
    
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
        
class EditableImageWindow:
    def __init__(self, image: Image, image_path: str):
        self.image: Image = image
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
        
        self.rect = DrawRectangle(self.window, canvas, self.image)
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
    __password: tk.StringVar
    user: User = User()
    def __init__(self):
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
        self.__password= tk.StringVar()
        login_label = tk.Label(canvas, text='Login', font=('Arial', 25)).place(x=220, y=50)
        login_username_label = tk.Label(canvas, text='Username', font=('Arial', 15)).place(x=220, y=100)
        login_username_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=self.username).place(x=150, y=130)
        login_password_label = tk.Label(canvas, text='Password', font=('Arial', 15)).place(x=220, y=170)
        login_password_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=self.__password, show='*').place(x=150, y=200)
        login_button = tk.Button(canvas, text='Login', command=self.__login_button, width=31).place(x=150, y=240)
        register_button = tk.Button(canvas, text='Register', command=self.__register_button, width=31).place(x=150, y=270)
        self.window.mainloop()    
    
    def __register_button(self):
        self.window.destroy()
        RegisterWindow()
    
    def __login_button(self):
        self.user.login(self.username, self.__password)
        if self.user.logged_in:
            self.window.destroy()
    
class RegisterWindow:
    username: tk.StringVar
    password: tk.StringVar
    confirm_password: tk.StringVar
    user: User = User()
    def __init__(self):
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
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.confirm_password = tk.StringVar()
        label = tk.Label(canvas, text='Register', font=('Arial', 25)).place(x=325, y=20)
        username_label = tk.Label(canvas, text='Username', font=('Arial', 15)).place(x=345, y=70)
        username_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=self.username).place(x=275, y=100)
        password_label = tk.Label(canvas, text='Password', font=('Arial', 15)).place(x=345, y=140)
        password_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=self.password, show='*').place(x=275, y=170)
        confirm_password_label = tk.Label(canvas, text='Confirm Password', font=('Arial', 15)).place(x=305, y=210)
        confirm_password_entry = tk.Entry(canvas, font=('Arial', 15), textvariable=self.confirm_password, show='*').place(x=275, y=240)
        register_button = tk.Button(canvas, text='Register', command=self.__register_button, width=31).place(x=275, y=280)
        login_button = tk.Button(canvas, text='Login', command=self.__login_button, width=31).place(x=275, y=310)
        self.window.mainloop()
    
    def __login_button(self):
        self.window.destroy()
        LoginWindow()

    def __register_button(self):
        self.user.register(self.username, self.password, self.confirm_password)
    
def main():
    login_window = LoginWindow()
    while True:
        if login_window.user.logged_in:
            app_dirs = AppDirs()
            if keyboard.is_pressed('1'): # Full screen shot
                screen = ImageGrab.grab()
                image_name = f'\\{int(time.time())}.jpg'
                image_path = app_dirs.images_dir + image_name 
                screen.save(image_path)
            if keyboard.is_pressed('2'): # Select a rectangle inside screen shot
                screen = ImageGrab.grab()
                image_name = f'\\{int(time.time())}.jpg'
                image_path = app_dirs.images_dir + image_name
                EditableImageWindow(screen, image_path)
        else:
            break
    #app_dirs = AppDirs()
    #db = DB()
    #with open("C:\\Users\\Aironas\\Documents\\Imager\\Images\\1713174697.jpg", "rb") as image:
    #    f = image.read()
    #    b = bytearray(f)
    #db.add_row_image(b, "asd", date.today())
    #del db22
    

if __name__ == "__main__":
    main()