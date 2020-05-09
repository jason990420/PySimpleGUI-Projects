import os
from urllib.parse import quote
from pathlib import Path

from bs4 import BeautifulSoup
import PySimpleGUI as sg

from Tool import read_URL, read_file, save_file
from PySimpleGUI_Tool import Tree

class Song():

    def __init__(self):
        self.base = 'http://mpge.5nd.com/'
        self.url = 'http://so.5nd.com/s_'
        self.song_file = 'song.json'
        self.song_directory = 'MP3'
        if not Path(self.song_directory).is_dir():
            Path(self.song_directory).mkdir()

    def load(self, name, url):
        signal('Loading song ...')
        try:
            response, html = read_URL(url, encoding='gb18030')
        except:
            signal('Web site link path load failed !')
            return
        if not response:
            signal('Web site link path load failed !')
            return
        soup = BeautifulSoup(html, 'html.parser')
        sub_url = soup.find('div', {"id":"kuPlayer"})["data-play"]
        song_url = self.base + sub_url
        try:
            response, data = read_URL(song_url, byte=True)
        except:
            signal('Web site song load failed !')
            return
        if not response:
            signal('Web site song load failed !')
            return
        file = f'{self.song_directory}/{name}.mp3'
        i = 1
        while Path(file).is_file():
            i += 1
            file = f'{self.song_directory}/{name}_{i}.mp3'
        with open(file, 'wb') as f:
            f.write(data)
        tree1.insert_node('', name, file)
        signal('Song loaded, double click item on left list to play.')

    def search(self, text):
        if text:
            signal('Searching ...')
            url = self.url + quote(text)
            try:
                response, html = read_URL(url, encoding='gb18030')
            except:
                signal('Web site load failed !')
                return
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                tags = soup.find_all('p', {"class":"f14"})
                titles = [tag.text for tag in tags]
                urls = [tag.a['href'] for tag in tags]
                if len(urls)==0:
                    signal('No result found !')
                    return
                for title, url in zip(titles, urls):
                    tree2.insert_node('', title, url, update=True)
            else:
                signal('Web site load failed !')
                return
            signal('Search Done, double click item on right list to load.')

def popup(text):
    text = sg.popup_get_text(message=text, font=font, size=(40,1),
        default_text='', no_titlebar=True, keep_on_top=True)
    return None if text == None or text.strip()=='' else text.strip()

def signal(message):
    status.update(value=message)
    window.refresh()

font = ('Courier New', 12, 'bold')
tree1 = Tree(column_width=50, font=font, row_height=23, key='TREE1')
tree2 = Tree(column_width=73, font=font, row_height=23, key='TREE2')
layout = [[sg.Button('Sort'), sg.Button('Move Up'), sg.Button('Move Down'),
           sg.Button('Search New'), sg.Button('Search Next'),
           sg.Button('Search Previous'), sg.Button('Delete'),
           sg.Button('Rename'), sg.Button('Quit'),
           sg.Text("Search Song", font=font),
           sg.Input('', font=font, size=(38, 1), focus=True, key='Input'),
           sg.Button('Search Song')],
          [tree1, tree2], [sg.Text('', size=(126, 1), font=font, key='Status')]]

window = sg.Window('MP3 Downloader', layout=layout, finalize=True)
tree1.hide_header(window)
tree2.hide_header(window)
window['TREE1'].bind('<Double-Button-1>', '_DOUBLE')
window['TREE2'].bind('<Double-Button-1>', '_DOUBLE')
status = window['Status']
song = Song()
dictionary = read_file(song.song_file)
if dictionary:
    tree1.load_tree(dictionary)

while True:

    event, values = window.read()

    if event in [None, 'Quit']:
        break
    elif event == 'Sort':
        tree1.sort_tree()
    elif event == 'Move Up':
        tree1.move_node_up(tree1.where())
    elif event == 'Move Down':
        tree1.move_node_down(tree1.where())
    elif event == 'Search New':
        text = popup('Name of song to search')
        if text:
            key = tree1.search(text, mode='New')
            if key:
                tree1.select(key)
    elif event == 'Search Next':
        key = tree1.search('', mode='Next')
        if key != None:
            tree1.select(key)
    elif event == 'Search Previous':
        key = tree1.search('', mode='Previous')
        if key != None:
            tree1.select(key)
    elif event == 'Delete':
        key = tree1.where()
        if key:
            path = Path(tree1.treedata.tree_dict[key].values[0])
            if path.is_file():
                path.unlink()
            tree1.delete_node(key)
    elif event == 'Rename':
        key = tree1.where()
        if key:
            text = popup('New song name, same name allowed and as different.')
            if text:
                tree1.rename(key, text)
    elif event == 'Search Song':
        text = values['Input'].strip()
        if text:
            tree2.delete_all_nodes()
            song.search(text)
    elif event == 'TREE1_DOUBLE':
        key = values['TREE1'][0]
        node = tree1.treedata.tree_dict[key]
        filename = node.values[0].replace('/', '\\')
        os.startfile(filename)
    elif event == 'TREE2_DOUBLE':
        key = values['TREE2'][0]
        node = tree2.treedata.tree_dict[key]
        song.load(node.text, node.values[0])

dictionary = tree1.dump_tree()
save_file(song.song_file, dictionary)
window.close()