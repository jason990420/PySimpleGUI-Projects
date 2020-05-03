import PySimpleGUI as sg
import math
from pathlib import Path
from Tool import Read_URL, Map
from PIL import Image
from io import BytesIO

class GUI():

    def __init__(self):
        self.boxes      = 51
        self.box_height = 50
        self.x0, self.y0, self.z0 = 0, 150, -50
        self.z1         = 0
        self.gap_width  = 860
        self.road_width = 800
        self.line_width = 20
        self.offset     = 0.5
        self.road_color = 'grey'
        self.gap_color  = 'black'
        self.line_color = 'white'
        self.figures = []
        self.count = 0
        self.Create_Window()

    def Create_Canvas(self):
        self.width = 1080
        self.height = 400
        return sg.Graph((self.width, self.height), (-self.width//2, 0),
            (self.width//2, self.height), key='Graph')

    def Create_Window(self):
        self.window = sg.Window('3D Road', layout=[[self.Create_Canvas()]],
            return_keyboard_events=True, finalize=True)
        self.draw = self.window.FindElement('Graph')
        self.Load_Background()
        self.Load_Tree()
        self.Draw_Background()

    def Download_Picture(self, url, file, size):
        if not Path(file).is_file():
            sg.popup(f'First time to load {file} from web ...', no_titlebar=True,
                auto_close=True, auto_close_duration=2)
            response, data = Read_URL(url, byte=True)
            if data:
                with open(file, 'wb') as f:
                    f.write(data)
                im = Read_File(file)
                im = im.resize(size)
                im.save(file)
                sg.popup(f'{file} loaded ...', no_titlebar=True,
                    auto_close=True, auto_close_duration=1)
            else:
                sg.popup(f'{file} load failed...', no_titlebar=True,
                    auto_close=True, auto_close_duration=2)
                self.window.close()
                quit()

    def Load_Data(self, file):
        im = Image.open(file)
        with BytesIO() as output:
            im.save(output, format='PNG')
            data = output.getvalue()
        return (data, im.width, im.height)

    def Load_Background(self):
        url = 'https://ae01.alicdn.com/kf/HTB18XRYXBv0gK0jSZKb762K2FXaF.png'
        file = 'background.png'
        size = (self.width, 300)
        self.Download_Picture(url, file, size)
        self.background, self.background_width, self.background_height = (
            self.Load_Data(file))

    def Load_Tree(self):
        url = 'https://www.vippng.com/png/full/458-4585828_fall-tree-png.png'
        file = 'tree.png'
        size = (250, 250)
        self.Download_Picture(url, file, size)
        self.tree = Image.open(file)
        self.tree_width, self.tree_height = self.tree.size

    def Point_To_2D(self, point):
        x, y, z = point
        s1 = (z-self.z1)/(z-self.z0)
        X = x + (self.x0 - x)*s1 - self.x0
        Y = y + (self.y0 - y)*s1
        return [X, Y]

    def Point_To_Box(self, x, y, z, dx, dy, dz, dx2):
        return [[x, y, z], [x+dx, y, z],
                [x+dx+dx2, y+dy, z+dz], [x+dx2, y+dy, z+dz]]

    def Draw_Background(self):
        self.background_figure = self.draw.DrawImage(data=self.background,
            location=(-self.background_width//2, self.height))

    def Draw_Box(self, x, y, z, dx, dy, dz, dx2, color):
        points = self.Point_To_Box(x, y, z, dx, dy, dz, dx2)
        points = Map(self.Point_To_2D, points)
        self.figures.append(self.draw.DrawPolygon(points, fill_color=color))

    def Draw_Grass(self, x, y, z, dx, dy, dz, dx2, color):
        points = self.Point_To_Box(x, y, z, dx, dy, dz, dx2)
        points = Map(self.Point_To_2D, points)
        points[0][0] = points[3][0] = -self.width//2
        points[1][0] = points[2][0] =  self.width//2
        self.figures.append(self.draw.DrawPolygon(points, fill_color=color))

    def Draw_Tree(self, x, y, z, dx, dy, dz, scale=1):
        w = max(1, int(self.tree_width*scale))
        h = max(1, int(self.tree_height*scale))
        im = self.tree.resize((w, h))
        with BytesIO() as output:
            im.save(output, format='PNG')
            data = output.getvalue()
        X, Y = self.Point_To_2D([x, y, z])
        figure = self.draw.DrawImage(data=data,
            location = (X-self.tree_width*scale/2, Y+self.tree_height*scale))
        self.figures.append(figure)
        X, Y = self.Point_To_2D([x+dx, y+dy, z+dy])
        figure = self.draw.DrawImage(data=data,
            location = (X-self.tree_width*scale/2, Y+self.tree_height*scale))
        self.figures.append(figure)

    def Delete_Figures(self):
        for figure in self.figures:
            self.draw.DeleteFigure(figure)
        self.figures = []

    def Update_All(self):
        self.Delete_Figures()
        self.Draw_Grass(-self.width//2, 0, self.offset,
            self.width, 0, self.boxes*self.box_height, 0, 'green')
        for box in range(self.boxes-1, -1, -1):
            center = -500*math.sin(2*(box+self.count)/self.boxes*math.pi)
            dx = -500*math.sin(2*(box+self.count+1)/self.boxes*math.pi)-center
            dy = center/2-250
            z = box*self.box_height
            if (box+self.count)%3 == 0:
                self.Draw_Box(center-self.gap_width//2, 0, z, self.gap_width,
                    0, self.box_height, dx, self.gap_color)
            self.Draw_Box(center-self.road_width//2, 0, z, self.road_width,
                    0, self.box_height, dx, self.road_color)
            if (box+self.count)%3 == 0:
                self.Draw_Box(center-self.line_width//2, 0, z, self.line_width,
                    0, self.box_height, dx, self.line_color)
            if (box+self.count)%10 == 0:
                scale = 1- (z-self.z1)/(z-self.z0)
                self.Draw_Tree(center-self.gap_width//2-50, 0, z,
                    self.gap_width+100, 0, 0, scale)
        self.count += 1
        if self.count == self.boxes:
            self.count = 0
        self.x0 = center


G = GUI()
while True:

    G.Update_All()
    event, values = G.window.Read(timeout=100)

    if event == None:
        break

    elif event in ['Left:37', 'Right:39', 'Up:38', 'Down:40']:
        pass

G.window.close()