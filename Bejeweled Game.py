import numpy as np
import PySimpleGUI as sg
import random
import math
import winsound
from time import sleep
from io import BytesIO
from pathlib import Path
from PIL import Image
from Tool import read_URL, read_file, save_file


class Bejewel():

    def __init__(self):

        self.title = 'Bejeweled Game'
        self.url1 = 'http://pngimg.com/uploads/diamond/diamond_PNG6698.png'
        self.file1 = 'Jewelry.png'
        self.url2 = ('http://b.zol-img.com.cn/sjbizhi/images/4/320x510/'
                     '1366614187468.jpg')
        self.file2 = 'background.png'
        self.font = ('Courier New', 16, 'bold')
        self.w = self.h = 80
        self.columns = 12
        self.rows = 7
        self.kinds = 5  # maximum 7 now
        self.gap = 10
        self.width = self.columns * (self.w + self.gap) + self.gap
        self.height = self.rows * (self.h + self.gap) + self.gap
        self.steps = 5
        self.d = [(self.h+self.gap)//self.steps for i in range(self.steps-1)]
        self.dx = self.d + [self.w+self.gap-sum(self.d)]
        self.dy = self.d + [self.h+self.gap-sum(self.d)]
        self.background = 'darkgreen'
        self.x = [i*(self.w+self.gap)+self.gap for i in range(self.columns)]
        self.y = [self.height*2-i*(self.w+self.gap)-2*self.gap
                    for i in range(self.rows*2)]
        self.sound = [int(220*(1+(2**(3/12))**i)) for i in range(12)]
        self.data = []
        self.score = 0
        self.figure = None
        self.kind = None

    def Add_All(self):
        if self.figure is not None and self.kind is not None:
            cells = [[x, y] for x in range(self.columns)
                for y in range(self.rows*2) if self.figure[y, x]!=0]
            self.Delete(cells)
        self.score = 0
        self.Score(0)
        self.figure = np.full((self.rows*2, self.columns), 0)
        self.kind = np.random.randint(0, self.kinds-1, size = (
            self.rows*2, self.columns), dtype=np.int8)
        # self.exist = np.full((self.rows*2, self.columns), 0, dtype=np.int8)
        for y in range(self.rows*2):
            for x in range(self.columns):
                self.Add_New(self.kind[y, x], x, y)

    def Add_New(self, value, x, y):
        self.figure[y, x] = draw.DrawImage(
            data=self.data[value], location=(self.x[x], self.y[y]))

    def Array_To_Data(self, array):
        image = Image.fromarray(array, mode='RGBA')
        with BytesIO() as output:
            image.save(output, format="PNG")
            data = output.getvalue()
        return data

    def Check_Line(self, line, var, direction):
        result, value, count, tmp = [], None, 0, []
        for index, kind in enumerate(line):
            if kind != value:
                if count >= 3:
                    result += tmp
                tmp, value, count = [index], kind, 1
            else:
                count += 1
                tmp.append(index)
        if count >= 3:
            result += tmp
        if direction == 'x':
            result = [[var, y+self.rows] for y in result]
        else:
            result = [[x, var+self.rows] for x in result]
        return result

    def Check_Lines(self):
        result = []
        for x in range(self.columns):
            result += self.Check_Line(self.kind[self.rows:, x], x, 'x')
        for y in range(self.rows):
            result += self.Check_Line(self.kind[y+self.rows, :], y, 'y')
        if result == []:
            return False
        cells = []
        for item in result:
            if item not in cells:
                cells.append(item)
        self.Flash(cells)
        self.Delete(cells)
        self.Score(len(cells))
        return True

    def Delete(self, cells):
        if cells == []:
            return
        for item in cells:
            x, y = item
            draw.Widget.addtag_withtag('Delete', self.figure[y, x])
        draw.Widget.delete('Delete')
        draw.Widget.dtag('Delete', 'Delete')
        for x, y in cells:
            self.kind[y, x], self.figure[y, x] = -1, 0
        window.Refresh()

    def Flash(self, target):
        dxes = [-2] + [4, -4]*3 + [2]
        for x, y in target:
            draw.Widget.addtag_withtag('Remove', self.figure[y, x])
        for dx in dxes:
            draw.Widget.move('Remove', dx, 0)
            window.Refresh()
            sleep(0.05)

    def Load_background(self):
        if not Path(self.file2).is_file():
            response, data = read_URL(self.url2, byte=True)
            if data:
                with open(self.file2, 'wb') as f:
                    f.write(data)
            else:
                Signal(f'Cannot get {filename} from web !')
                quit()
        im = read_file(self.file2)
        im = im.convert(mode='RGBA').resize((self.width, self.height))
        a = np.array(im, dtype=np.uint8)
        data = self.Array_To_Data(a)
        self.picture = draw.DrawImage(data=data, location=(0, self.height))

    def Load_Icon(self):
        if not Path(self.file1).is_file():
            response, data = read_URL(self.url1, byte=True)
            if data:
                with open(self.file1, 'wb') as f:
                    f.write(data)
            else:
                Signal(f'Cannot get {elf.file1} from web !')
                quit()
        im = read_file(self.file1).resize((self.w, self.h))
        a = np.array(im, dtype=np.uint8)
        arrays = []
        for i, j, k in [[0, 1, 2], [0, 0, 0], [2, 2, 2], [2, 0, 2], [0, 2, 0],
                        [2, 2, 1], [1, 1, 0]]:
            t = a.copy()
            t[:,:,0], t[:,:,1], t[:,:,2] = a[:,:,i], a[:,:,j], a[:,:,k]
            arrays.append(t)
        self.data = [self.Array_To_Data(array) for array in arrays]

    def Move_Add(self, line):
        for x in line:
            value = random.randint(0, self.kinds-1)
            self.kind[0, x] = value
            self.Add_New(value, x, 0)

    def Move_All_Down(self):
        while True:
            target_down, line_down = [], []
            for x in range(self.columns):
                for y in range(2*self.rows-1, self.rows-1, -1):
                    if self.kind[y, x] == -1:
                        target_down += [[x, i] for i in range(y-1, -1, -1)]
                        line_down.append(x)
                        break
            if target_down == []:
                return
            self.Move_Down(target_down)
            self.Move_Add(line_down)

    def Move_Down(self, target):
        for x, y in target:
            draw.Widget.addtag_withtag('Move Down', self.figure[y, x])
            self.kind[y+1, x] = self.kind[y, x]
            self.figure[y+1, x] = self.figure[y, x]
        for dy in self.dy:
            draw.Widget.move('Move Down', 0, dy)
            window.Refresh()
            # sleep(0.005)
        draw.Widget.dtag('Move Down', 'Move Down')

    def Position_to_cell(self, x, y):
        x0, offset_x = divmod(x - self.gap, self.w + self.gap)
        y0, offset_y = divmod(self.height*2 - y - self.gap, self.h + self.gap)
        if ((x <= self.gap) or (self.height-y <= self.gap) or
            (offset_x > self.w) or (offset_y > self.h)):
                return None, None
        return x0, y0

    def Score(self, score):
        self.score += int(score**2//3)
        self.score = min(self.score, 999999)
        window.FindElement('Score').Update(
            value='Score {:0>6d}'.format(self.score))

    def Switch(self, x1, y1, x2, y2):
        for i in range(self.steps):
            dx = -self.dx[i] if x1 > x2 else  self.dx[i] if x1 < x2 else 0
            dy =  self.dy[i] if y1 > y2 else -self.dy[i] if y1 < y2 else 0
            draw.MoveFigure(self.figure[y1, x1], dx, dy)
            draw.MoveFigure(self.figure[y2, x2], -dx, -dy)
            window.Refresh()
            sleep(0.05)
        self.kind[y1, x1], self.kind[y2, x2] = (
            self.kind[y2, x2], self.kind[y1, x1])
        self.figure[y1, x1], self.figure[y2, x2] = (self.figure[y2, x2],
            self.figure[y1, x1])

    def Switch_Icon(self, here, there):
        x1, y1 = here
        x2, y2 = there
        x0, y0 = self.Position_to_cell(x1, y1)
        if x0 == None:
            return False
        if abs(x2-x1) > abs(y2-y1):
            x, y = (x0+1, y0) if x2>x1 else (x0-1, y0)
        else:
            x, y = (x0, y0-1) if y2>y1 else (x0, y0+1)
        if not (0<=x0<self.columns and 0<=x<self.columns and
                self.rows<=y0<self.rows*2 and self.rows<=y<self.rows*2):
            return False
        self.Switch(x0, y0, x, y)
        if not self.Update():
            self.Switch(x, y, x0, y0)

    def Update(self):
        flag = False
        sound = -1
        while self.Check_Lines():
            flag = True
            sound = sound + 1 if sound <11 else 11
            winsound.Beep(self.sound[sound], 100)
            self.Move_All_Down()
        return flag

    def Button(self, key):
        return sg.Button(key, font=self.font, size = (10, 1),
            enable_events=True, key=key)

    def Graph(self):
        return sg.Graph((self.width+1, self.height+1), (-1, -1),
            (self.width, self.height), background_color=self.background,
            drag_submits=True, enable_events=True, key='Graph')

    def Text(self):
        return sg.Text('Score 000000', font=self.font, size = (29, 1),
                       text_color = 'yellow', justification='left',
                       auto_size_text=False, key='Score')


def Signal(string):
    sg.popup(string)
    window.close()
    exit()

B = Bejewel()
layout = [[B.Text(), B.Button('New Game'), B.Button('Quit')], [B.Graph()]]
window = sg.Window(B.title, layout=layout, finalize=True)
draw = window.find_element('Graph')
B.Load_background()
B.Load_Icon()


mouse_down = False
drag = False
old_position = None
start = False
while True:

    event, values = window.read()

    if event in [None, 'Quit']:
        break

    elif event == 'New Game':
        B.Add_All()
        B.Update()

    elif event == 'Graph':
        new_position = values['Graph']
        if (not drag) and (not mouse_down):
            old_position = new_position
            mouse_down = True
        elif (not drag) and mouse_down:
            if new_position != old_position:
                drag = True
    elif event == 'Graph+UP':
        if drag:
            B.Switch_Icon(old_position, new_position)
        mouse_down = False
        drag = False
        old_position = None

window.close()