import numpy as np
import PySimpleGUI as sg
import random

class Game():

    def __init__(self):
        self.pixel  = np.array(
        [[[[0,0], [0,1], [0,2], [0,3]], [[0,0], [1,0], [2,0], [3,0]],  # ____
          [[0,0], [0,1], [0,2], [0,3]], [[0,0], [1,0], [2,0], [3,0]]],
         [[[0,0], [0,1], [1,0], [1,1]], [[0,0], [0,1], [1,0], [1,1]],  # 田
          [[0,0], [0,1], [1,0], [1,1]], [[0,0], [0,1], [1,0], [1,1]]],
         [[[0,1], [1,1], [2,1], [2,0]], [[0,0], [1,0], [1,1], [1,2]],  # ▁▁│
          [[0,1], [0,0], [1,0], [2,0]], [[0,0], [0,1], [0,2], [1,2]]],
         [[[0,0], [0,1], [1,1], [2,1]], [[1,0], [0,0], [0,1], [0,2]],  # │▁▁
          [[0,0], [1,0], [2,0], [2,1]], [[1,0], [1,1], [1,2], [0,2]]],
         [[[0,1], [1,1], [2,1], [1,0]], [[0,0], [0,1], [0,2], [1,1]],  # ▁│▁
          [[0,0], [1,0], [2,0], [1,1]], [[1,0], [1,1], [1,2], [0,1]]],
         [[[0,0], [1,0], [1,1], [2,1]], [[1,0], [1,1], [0,1], [0,2]], # ▔│▁
          [[0,0], [1,0], [1,1], [2,1]], [[1,0], [1,1], [0,1], [0,2]]],
         [[[0,1], [1,1], [1,0], [2,0]], [[0,0], [0,1], [1,1], [1,2]],  # ▁│▔
          [[0,1], [1,1], [1,0], [2,0]], [[0,0], [0,1], [1,1], [1,2]]]])

        self.width, self.height = 10, 20
        self.start_x, self.start_y = 4, 0
        self.kind,self.axis, self.timer = 7, 0, 100

        self.font, self.background = ('Courier New', 16), 'gray'
        self.pause, self.stop, self.no_blcok = False, True, True

        self.block = []

        self.lines, self.score, self.level, self.count = 0, 0, 0, 0
        self.plus = [0, 100, 200, 400, 800]

        self.area = np.zeros((self.height, self.width))
        self.cont = np.full((self.height, self.width), 7)
        self.rate = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 6, 6, 6]
        self.colors = ['gold', 'blue', 'tomato', 'red', 'green', 'purple',
                       'brown', self.background]
        self.func = {'New'      :self.new,   'Pause'  :self.wait,
                     'Left:37'  :self.left,  'Up:38'  :self.rotate,
                     'Right:39' :self.right, 'Down:40':self.down,
                     'Escape:27':self.wait,  ' '      :self.space}

    def blocks(self):
        self.count += 1
        if self.count == 50:
            self.count = 0
            old_axis = self.axis-1 if self.axis>0 else 3
            for kind in range(self.kind):
                self.block = [kind, old_axis, (kind%2)*5+1, (kind//2)*5+1]
                self.draw(show=False)
                self.block = [kind, self.axis, (kind%2)*5+1, (kind//2)*5+1]
                self.draw()
            self.axis = self.axis+1 if self.axis<3 else 0

    def check(self):
        count = 0
        if not self.no_block: self.draw(show=False)
        for y in range(self.height-1, -1, -1):
            if np.sum(self.area[y]) == self.width:
                count += 1
                self.area[1:y+1], self.area[0] = self.area[0:y], 0
                self.cont[1:y+1], self.cont[0] = self.cont[0:y], 7
                for z in range(0, y+1):
                    for x in range(self.width):
                        window.find_element(str(x+10*z)).Update(
                            background_color=self.colors[self.cont[z, x]])
        if not self.no_block: self.draw()
        self.score += min(self.plus[count], 999999)
        self.lines += count
        self.level = int(self.lines//2)
        self.timer = int(100-self.level) if self.level<100 else 1
        window.find_element('Score').Update(value='{:0>6d}'.format(self.score))
        window.find_element('Level').Update(value='{:0>2d}'.format(self.level))

    def clear(self):
        self.area = np.zeros((self.height, self.width))
        for i in range(self.width*self.height):
            window.find_element(str(i)).Update(
                background_color=self.background)

    def down(self):
        kind, axis, x, y = self.block
        new_block = [kind, axis, x, y+1]
        if self.ok(new_block):
            self.block = new_block
            return True
        else:
            self.no_block = True
            data = self.get_font(self.block)+self.block[2:]
            xi, yi = data[:,0], data[:,1]
            self.area[yi, xi] = 1
            return False

    def draw(self, show=True):
        color = self.colors[self.block[0]] if show else self.background
        for x, y in self.get_font(self.block)+self.block[2:]:
            window.find_element(str(x+10*y)).Update(background_color=color)
            self.cont[y, x] = self.colors.index(color)

    def get_font(self, block):
        return self.pixel[block[0], block[1]]

    def left(self):
        kind, axis, x, y = self.block
        new_block = [kind, axis, x-1 if x>0 else x, y]
        if self.ok(new_block):
            self.block = new_block
            return True
        return False

    def new_block(self):
        self.block = [self.random(), 0, int(self.width/2-1), 0]
        self.draw(self.block)
        if self.ok(self.block):
            self.no_block = False
            self.count = 0
        else:
            self.stop = True
            sg.popup("Game Over", no_titlebar=True, font=self.font)

    def new(self):
        self.pause = False
        self.no_block = True
        self.stop = False
        self.clear()

    def offset(self, x_limit, x_max, x_min):
        return x_max-x_limit+1 if x_max>x_limit-1 else x_min if x_min<0 else 0

    def ok(self, block):
        if block[3] >= self.height:
            return False
        data = self.get_font(block)+block[2:]
        if not(np.max(data[:,0])<self.width  and np.min(data[:,0])>-1 and
               np.max(data[:,1])<self.height and np.min(data[:,1])>-1):
            return False
        x, y = data[:,0], data[:,1]
        if np.sum(self.area[y, x]) != 0:
            return False
        return True

    def random(self):
        return random.choice(self.rate)

    def right(self):
        kind, axis, x, y = self.block
        new_block = [kind, axis, x+1 if x<self.width-1 else x, y]
        if self.ok(new_block):
            self.block = new_block
            return True
        return False

    def rotate(self):
        kind, axis, x, y = self.block
        new_block = [kind, (axis+1)%4, x, y]
        data=self.get_font(new_block)+[x, y]
        x_max, x_min = np.max(data[:,0]), np.min(data[:,0])
        y_max, y_min = np.max(data[:,1]), np.min(data[:,1])
        x_offset = self.offset(self.width, x_max, x_min)
        y_offset = self.offset(self.height, y_max, y_min)
        new_block[2:]= [x-x_offset, y-y_offset]
        if self.ok(new_block):
            self.block = new_block
            return True
        return False

    def space(self):
        while True:
            self.draw(show=False)
            stop = not self.down()
            self.draw()
            if stop:
                break

    def update(self, func):
        self.draw(show=False)
        func()
        self.draw()

    def wait(self):
        self.pause = not self.pause

def T(key, text=None, color='white', size=(None, None)):
    if text == None:
        text = ' '*2
    return sg.Text(text, key=key, pad=(1,1), size=size, justification='center',
        font=G.font, background_color=G.background, text_color=color)

def M(text, bg='green'):
    return sg.Text(text, font=G.font, size=(16, 1), justification='center',
        background_color=bg, text_color='white')

def B(text, key):
    return sg.Button(text, font=G.font, size=(16, 1), key=key,
        bind_return_key=False, focus=False)


G = Game()

layout1 = [[T(str(i+j*G.width), color=G.background) for i in range(G.width)]
              for j in range(G.height)]
layout2 = [[M('Score')], [T('Score', text='000000', size=(16, 1))],
           [M('', bg=G.background)],
           [M('Level')], [T('Level', text='00', size=(16, 1))],
           [M('', bg=G.background)],
           [M('Left:Move Left')], [M('Right:Move Right')], [M('Down:Move Down')],
           [M('Up:Rotate')], [M('Space:Drop')], [M('ESC:Pause')],
           [M('', bg=G.background)], [M(' ', bg=G.background)],
           [B('New Game', 'New')], [B('Game Pause', 'Pause')],
           [B('Game Over', 'Over')]]

frame1 = sg.Frame('', layout=layout1, background_color=G.background,
                  border_width=5)
frame2 = sg.Frame('', layout=layout2, background_color=G.background,
                 border_width=5, size=(None, G.height*32))
layout = [[frame1, frame2]]
window = sg.Window('Tetris Game', layout=layout, finalize=True,
                   use_default_focus=False, return_keyboard_events=True,
                   background_color=G.background)

blocks = True
while True:

    event, values = window.read(timeout=10)

    if event in [None, 'Over']:
        break
    elif event in ['New', 'Pause', 'Escape:27']:
        blocks = False
        G.func[event]()
        continue
    if blocks:
        G.blocks()
        continue
    if G.pause or G.stop:
        continue
    if G.no_block:
        G.new_block()
    else:
        if event in G.func:
            G.update(G.func[event])
        G.count += 1
        if G.count == G.timer:
            G.count = 0
            G.update(G.down)
    G.check()

window.close()
