"""
Demo script to change the shape of a PySimple button.
Just defined function for new shape of Button.
Applied to other Element is posiible, just revised a little code.

Date: 2020/06/10
Auther: Jason Yang
Revision: 0.0.1
"""
from io import BytesIO

from PIL import Image, ImageDraw
from tkinter import Tk, Label, font as tkFont
import PySimpleGUI as sg

def get_string_width(text, font):
    """
    get string length
    : Parameter
      text - string to calculate length of text when drawn on screen.
      font - font , (family, size, style) or "family size style"
    : Return
      integer - width of string
    """
    root = Tk()
    root.geometry("+10000+10000")
    label = Label(root, text=text, font=font, padx=0, pady=0)
    label.pack()
    root.update()
    width = label.winfo_width()
    root.destroy()
    return width

def button_image(width, height, color='red', kind='stadium'):
    """
    Get image data of a stadium shape.
    : Parameters
      width, height - positive integer, size of image.
        The height will be adjusted to a multiple of 2.
    : Return
      image data for PySimpleGUI
    """
    width += 10
    kinds = ['stadium', 'round']
    if (not (isinstance(width, int) and isinstance(height, int))) or not (
            width>0 and height>0):
        print('Paramters width and height should be positive integer.')
        raise ValueError
    height = (height+1)//2*2
    if width<height:
        print('Width should be greater than height')
        raise ValueError
    if kind not in kinds:
        print('Paramter kind not in existing shape')
        raise ValueError

    im = Image.new(
        mode='RGBA', size=(width, height), color=(255, 255, 255, 0))
    image = ImageDraw.Draw(im, mode='RGBA')

    if kind == 'stadium':
        width = width
        radius = height//2
        image.ellipse((0, 0, height, height), fill=color)
        image.ellipse((width-height, 0, width, height), fill=color)
        image.rectangle((radius, 0, width-radius, height), fill=color)
    elif kind == 'round':
        bg = sg.theme_background_color()
        r, r2 = height//2, height
        image.rectangle((0, 0, width, height), fill=color)
        image.arc((-r, -r, r2, r2), start=180, end=270, fill=bg, width=r)
        image.arc((width-r2, -r, width+r, r2), start=270, end=360, fill=bg,
            width=r)
        image.arc((-r, 0, r2, r*3), start=90, end=180, fill=180, width=r)
        image.arc((width-r2, 0, width+r, r*3), start=0, end=90, fill=bg,
            width=r)
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data


def button(button_text='', kind='stadium', **kwargs):
    """
    Button with different shape
    : Parameters
      kind - shape of button, 'stadium' only now
    : Return
      instance of sg.Button
    """
    bg = sg.theme_background_color()

    def len_(text):
        length = 0
        for char in text:
            length += 2 if east_asian_width(char) in 'AFW' else 1
        return length

    font = kwargs['font'] if 'font' in kwargs else sg.DEFAULT_FONT
    if isinstance(font, tuple):
        family, fsize = font[0], font[1]
    else:
        font_lst = font.split()
        familiy, fsize = font_lst[0].strip(), eval(font_lst[1].strip())

    height = 3*fsize

    if 'size' in kwargs:
        size = kwargs['size'][0]
        width = get_string_width(' '*size, font)
    else:
        width = get_string_width(button_text, font)

    if 'auto_size_button' in kwargs and kwargs['auto_size_button']:
        width = get_string_width(button_text, font)

    if 'button_color' in kwargs:
        color = kwargs['button_color'][1]
        kwargs['button_color'] = (kwargs['button_color'][0], bg)
    else:
        color = 'blue'
        kwargs['button_color'] = (sg.DEFAULT_BUTTON_COLOR[0], bg)

    image_data = button_image(width, height, color, kind=kind)
    kwargs['image_data'] = image_data
    kwargs['border_width'] = 0

    return sg.Button(button_text=button_text, **kwargs)


font1 = ('Courier New', 12, 'bold')
font2 = ('Arial', 12, 'bold')
color1 = ('white', 'blue')
color2 = ('white', 'green')

layout = [
    [button("START", font=font1, button_color=color1),
     button("STOP",  font=font1, button_color=color1),
     button("EXIT",  font=font1, button_color=color1)],
    [sg.Multiline('\n   Demo for different shape of Button', size=(80, 20))],
    [button("START", font=font1, button_color=color2, kind='round'),
     button("STOP",  font=font1, button_color=color2, kind='round'),
     button("EXIT",  font=font1, button_color=color2, kind='round')]]

window = sg.Window('Image Button', layout, use_default_focus=False)

while True:

    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

window.close()
