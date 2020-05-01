import PySimpleGUI as sg
import math
from pathlib import Path
from Tool import Read_File, Read_URL
from PIL import Image
from io import BytesIO
from PIL import Image, ImageTk

class GUI():

    def __init__(self):
        self.width, self.height = self.size = (1080, 400)
        self.boxes = 51
        self.x0, self.y0, self.z0 = 400, 150, -50
        self.z1 = 0
        self.box_distance = 100
        self.w0 = 20
        self.w1 = 2000
        self.w2 = 2060
        self.c1 = 0
        self.count = 0
        self.offset = 0.5
        self.background_url = 'https://ae01.alicdn.com/kf/HTB18XRYXBv0gK0jSZKb762K2FXaF.png'
        self.background_file = 'background.png'
        self.Get_Image(self.background_url, self.background_file, (self.width, 300))
        self.background_image = Image.open(self.background_file)
        self.tree_url = 'https://www.vippng.com/png/full/458-4585828_fall-tree-png.png'
        self.tree_file = 'tree.png'
        self.Get_Image(self.tree_url, self.tree_file, (50, 50))
        self.tree_data, self.w, self.h = self.Get_Tree()
        self.window = sg.Window('Racing', layout=[[self.Graph()]],
            return_keyboard_events=True, finalize=True)
        self.draw = self.window.FindElement('Graph')
        self.figures = []
        self.Draw_Background()

    def Convert_To_Screen(self, x, y, z):
        scale = (z-self.z1)/(z-self.z0)
        X = x + (self.x0 - x)*scale - self.x0
        Y = y + (self.y0 - y)*scale
        return [X, Y]

    def Convert_points(self, points):
        return [self.Convert_To_Screen(*point) for point in points]

    def point_to_points(self, x, y, z, dx, dz):
        return [[self.c1+x, y+self.y1 ,z], [self.c1+x+dx, y+self.y1, z], [self.c2+x+dx, y+self.y2, z+dz], [self.c2+x, y+self.y2, z+dz]]

    def Draw_Background(self):
        with BytesIO() as output:
            self.background_image.save(output, format='PNG')
            data = output.getvalue()
        self.background_figure = self.draw.DrawImage(data=data, location=(-self.width/2, self.height))

    def Draw_Box(self, points, color):
        self.figures.append(self.draw.DrawPolygon(points, fill_color=color))

    def Draw_Road(self, i):
        points = self.point_to_points(-self.w1/2, 0, self.offset+i*self.box_distance, self.w1, self.box_distance)
        points = self.Convert_points(points)
        self.Draw_Box(points, color='grey')

    def Draw_Horse(self, i):
        color = ['grey', 'white']
        points = self.point_to_points(-self.w0/2, 0, self.offset+i*self.box_distance, self.w0, self.box_distance)
        points = self.Convert_points(points)
        self.Draw_Box(points, color=color[(self.count+i)%2])

    def Draw_Gap(self, i):
        color = ['black', 'darkgrey']
        points = self.point_to_points(-self.w2/2, 0, self.offset+i*self.box_distance, self.w2, self.box_distance)
        points = self.Convert_points(points)
        self.Draw_Box(points, color=color[(self.count+i)%2])

    def Draw_Ground(self, i):
        points = self.point_to_points(-self.w2-50, 0, self.offset+i*self.box_distance, 50, self.box_distance)
        points = self.Convert_points(points)
        points[0][0] = points[3][0] = -self.width/2
        points[1][0] = points[2][0] =  self.width/2
        self.Draw_Box(points, color='green')

    def Get_Tree(self):
        im = Image.open(self.tree_file)
        with BytesIO() as output:
            im.save(output, format='PNG')
            data = output.getvalue()
        return data, im.width//2, im.height

    def Draw_Tree(self, i):
        if (i+self.count)%3 == 0:
            x, y = self.Convert_To_Screen(self.c1-self.w2//2-200, self.y1, self.offset+i*self.box_distance)
            figure = self.draw.DrawImage(data=self.tree_data, location = (x-self.w, y+self.h))
            self.figures.append(figure)
            x, y = self.Convert_To_Screen(self.c1+self.w2//2+200, self.y1, self.offset+i*self.box_distance)
            figure = self.draw.DrawImage(data=self.tree_data, location = (x-self.w, y+self.h))
            self.figures.append(figure)

    def Get_Image(self, url, file, size):
        if not Path(file).is_file():
            response, data = Read_URL(url, byte=True)
            if data:
                with open(file, 'wb') as f:
                    f.write(data)
                im = Read_File(file)
                im = im.resize(size)
                im.save(file)

    def Graph(self):
        return sg.Graph(self.size, (-self.width//2, 0), (self.width//2, self.height), key='Graph')

    def Update(self):
        for figure in self.figures:
            self.draw.DeleteFigure(figure)
        self.figures = []
        for i in range(self.boxes-1, -1, -1):
            self.c1 = -2000*math.sin((i+G.count)*2/self.boxes*math.pi)
            self.c2 = -2000*math.sin((i+G.count+1)*2/self.boxes*math.pi)
            self.y1, self.y2 = self.c1//5-400, self.c2//5-400
            self.Draw_Ground(i)
            self.Draw_Gap(i)
            self.Draw_Road(i)
            self.Draw_Horse(i)
            self.Draw_Tree(i)
        self.x0 = G.c1  # + self.w1//4
        self.count += 1
        if self.count == self.boxes*10:
            self.count = 0

G = GUI()
while True:

    G.Update()
    event, values = G.window.Read(timeout=100)

    if event == None:
        break
    elif event == 'Left:37':
        G.x0 -= G.box_distance
    elif event == 'Right:39':
        G.x0 += G.box_distance
    elif event == 'Up:38':
        pass
    elif event == 'Down:40':
        pass

G.window.close()