import os
import tkinter as tk
from PIL import Image, ImageTk

start_x, start_y, end_x, end_y = 0, 0, 0, 0
rect, canvas, img, temp_img_path, window, img_path = None, None, None, None, None, None

def get_mouse_pos(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y


def update_rect(event):
    global rect
    global start_x, start_y, end_x, end_y
    end_x, end_y = event.x, event.y
    canvas.coords(rect, start_x, start_y, end_x, end_y)


def save_rect(event):
    global temp_img_path, img_path
    image_coords = tuple(canvas.coords(rect))
    img = Image.open(temp_img_path)
    cropped_img = img.crop(image_coords)
    cropped_img.save(img_path)
    os.remove(temp_img_path)
    window.destroy()


def main(temp_path, path):
    global rect, canvas, img, temp_img_path, window, img_path
    temp_img_path = temp_path
    img_path = path

    window = tk.Tk()
    window.attributes('-fullscreen', True)
    window.attributes('-topmost', True)

    img = ImageTk.PhotoImage(Image.open(temp_path))
    canvas = tk.Canvas(window, width=img.width(), height=img.height(), borderwidth=0, highlightthickness=0)
    canvas.pack(expand=True)
    canvas.create_image(0, 0, image=img, anchor=tk.NW)

    rect = canvas.create_rectangle(0, 0, 0, 0, dash=(2,2), fill='', outline='red')

    canvas.bind('<Button-1>', get_mouse_pos)
    canvas.bind('<B1-Motion>', update_rect)
    canvas.bind('<ButtonRelease-1>', save_rect)

    window.mainloop()