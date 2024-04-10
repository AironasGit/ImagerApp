import os
import tkinter as tk
from PIL import Image, ImageTk

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
        

def main(temp_path, path):
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