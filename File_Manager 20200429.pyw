"""
Python Help File - Jason Yang 2020/05/06

Create Book to store major information from source code of Python packages.
It can help to view class or method quickly after you load the sourc codes.

Functions

    1. Load File - Load .py
    2. Load Path - Load all .py files from directory Path
    3. Sort - Sorting all items in each node
    4. Quit - Quit from script
    5. Rename - Rename node
    6. Delete - Delete node
    7. Move Up - Move node up
    8. Move Down - Move node down

Information shown
    1. Left frame
       Tree structure of class and function/method defined
    2. Right Frame
       Docstring for node selected in left frame

Note: All source codes should be with correct syntax and
      exactly 4 spaces as as indentation
"""

import os
import sys
import json
import PySimpleGUI as sg
from token import *
from tokenize import tokenize
from pathlib import Path


class GUI():

    def __init__(self):
        self.font1 = ('Courier', 12, 'bold')
        self.font2 = ('Courier', 12, 'bold')
        self.button_size = 10
        self.line_width = 100
        self.book = 'Book.json'
        self.treedata = sg.TreeData()

    def Layout(self):
        return [[self.Input('Load File'), self.Browse_File('Load File'),
                 self.Input('Load Path'), self.Browse_Path('Load Path'),
                 self.Button('Sort'),           self.Button('Rename'),
                 self.Button('Delete'),         self.Button('Move Up'),
                 self.Button('Move Down'),      self.Button('Quit')],
                [self.Tree('TREE'), self.Multiline('MULTILINE')]]

    def Window(self, layout):
        self.window = sg.Window('Docstring for Python Files', layout=layout,
            margins=(0, 0), use_default_focus=False, finalize=True)
        self.tree = self.window.FindElement('TREE')
        self.multiline = self.window.FindElement('MULTILINE')
        self.tree.Widget.configure(show='tree')    # Invisiable Header
        # self.tree.bind('<Button-1>', 'Down')       # add Button-1 event to Tree

    def Button(self, key):
        return sg.Button(key, enable_events=True, size=(self.button_size, 1),
            font=self.font1)

    def Tree(self, key):
        return sg.Tree(data=self.treedata, headings=['Notes',], pad=(0, 0),
        show_expanded=False, col0_width=30, auto_size_columns=False,
        visible_column_map=[False,], select_mode=sg.TABLE_SELECT_MODE_BROWSE,
        enable_events=True, background_color='white', font=self.font2,
        num_rows=28, row_height=20, key=key)

    def Input(self, key):
        return sg.Input('', font=self.font1, key=key, visible=False,
            enable_events=True, do_not_clear=False)

    def Multiline(self, key):
        return sg.Multiline(default_text='', enable_events=True, pad=(0, 0),
            size=(self.line_width, 31), do_not_clear=True,
            key=key, border_width=0, focus=False, font=self.font1,
            text_color='white', background_color='blue')

    def Browse_File(self, key):
        return sg.FileBrowse(button_text=key, target=key, font=self.font1,
            size=(self.button_size, 1), enable_events=True,
            file_types=(("ALL Python Files", "*.py"),))

    def Browse_Path(self, key):
        return sg.FolderBrowse(button_text=key, target=key, font=self.font1,
                size=(self.button_size, 1), pad=(0, 0), enable_events=True)

    def New_Key(self):
        """
        Find a unique Key for new node, Key start from '1' and not in node list
        """
        i = 0
        while True:
            i += 1
            if str(i) not in self.treedata.tree_dict:
                return str(i)

    def Load_Book(self):
        """
        Read Book.json into treedata
        """
        if not Path(self.book).is_file():
            return
        with open(self.book, 'rt') as f:
            d = json.load(f)
        children = d[''][1]
        while children != []:
            temp = []
            for child in children:
                node = d[child]
                self.treedata.Insert(node[0], child, node[2], node[3])
                temp += node[1]
            children = temp
        self.tree.Update(values=self.treedata)

    def Save_Book(self):
        """
        Save treedata to Book.json
        Dictionary pairs in key: [parent, children, text, values]
        """
        d = {}
        for key, node in self.treedata.tree_dict.items():
            children = [n.key for n in node.children]
            d[key]   = [node.parent, children, node.text, node.values]
        with open(self.book, 'wt') as f:
            json.dump(d, f)

    def Load_File(self, values):
        """
        Load Python file and parsing tokens.
        Two kinds of statements captured into treedata
          1. Name of class or function as Node name
          2. Definition of class or function with docstring as value
        """
        filename = values['Load File']
        if filename == '': return
        self.Parse(filename)

    def Parse(self, filename, parent=''):
        with open(filename, 'rb') as f:
            tokens = list(tokenize(f.readline))
        name = Path(filename).stem
        key = self.New_Key()
        self.treedata.Insert(parent, key, name, values=[''])
        key_list = [key]
        i = 0
        while i < len(tokens):
            word = tokens[i].string
            # Name of 'class' or 'def' for statment
            if tok_name[tokens[i].type]=='NAME' and word in ['class', 'def']:
                level = tokens[i].start[1]//4           # indent for level
                if level > len(key_list)-1:             # if indent too much
                    level = len(key_list)-1             # set to just one indent
                name = word+' '+tokens[i+1].string      # name for tree structure
                i += 2
                string = name
                while i < len(tokens):                  # find end of class or def
                    char = tokens[i].string
                    string += char
                    if char == ',':                     # extra space for ','
                        string += ' '
                    elif tok_name[tokens[i].exact_type]=='COLON':
                        key_list = key_list[:level+1]   # End of statement ':'
                        key = self.New_Key()
                        key_list += [key, ]
                        self.treedata.Insert(
                            key_list[level], key, name, values=[string])
                        break
                    i += 1

            elif tok_name[tokens[i].type]=='STRING' and word.startswith('"""'):
                level = tokens[i].start[1]//4           # Document string
                if level > len(key_list)-1:
                    level = len(key_list)-1
                t = self.treedata.tree_dict[key_list[level]].values[0]
                t += '\n' + word[3:-3]
                t = t.replace('\r\n', '\n').replace('\n\n', '\n').strip()
                self.treedata.tree_dict[key_list[level]].values[0] = t
            i += 1
        self.tree.Update(values=self.treedata)

    def Load_Path(self, values):
        path = values['Load Path']
        if path == '': return
        self.Parse_Path(path, '')

    def Parse_Path(self, path, parent=''):
        files = os.listdir(path)
        if files == []:
            return
        key = self.New_Key()
        name = Path(path.lower()).stem
        self.treedata.Insert(parent, key, name, values=[''])
        for p in files:
            pathname = Path(path, p)
            full_path = os.path.join(path, p)
            if pathname.is_file() and p.endswith('.py'):
                self.Parse(full_path, parent=key)
            elif pathname.is_dir():
                self.Parse_Path(full_path, parent=key)

    def Convert(self, text):
        temp = text.replace('__init__', ' ')    # Set __init__ lowest
        temp = temp.replace('_', '|')           # Set '_' to highest
        return temp

    def Sort(self, values):
        """
        Sort children list of all nodes by name.
        The order is __init__, uppercase letter, lowercase letter, then '_'
        """
        pre_select_key = self.Where()
        for key, node in self.treedata.tree_dict.items():
            children = node.children
            node.children = sorted(                 # sort children by text
                children, key=lambda child: self.Convert(child.text))
        self.tree.Update(values=self.treedata)
        self.Select(pre_select_key)

    def Read_New_name(self):
        return sg.popup_get_text(message='New Name:', font=self.font1,
            default_text='', size=(40,1), no_titlebar=True, keep_on_top=True)

    def Rename(self, values):
        key = self.Where()
        if key:
            name = self.Read_New_name()
            if name:
                self.treedata.tree_dict[key].text = name
                self.tree.Update(key=key, text=name)

    def Delete(self, values):
        key = self.Where()
        if key:
            pre_key = self.Previous_Key(key)
            node = self.treedata.tree_dict[key]
            self.treedata.tree_dict[node.parent].children.remove(node)
            node_list = [node]
            while node_list != []:
                temp = []
                for item in node_list:
                    temp += item.children
                    del self.treedata.tree_dict[item.key]
                    del item
                node_list = temp
            self.tree.Update(values=self.treedata)
            self.Select(pre_key)

    def All_Tags(self, parent='', new=True):
        if new: self.search = []
        children = self.treedata.tree_dict[parent].children
        for child in children:
            self.search.append(child.key)
            self.All_Tags(parent=child.key, new=False)

    def Previous_Key(self, key):
        self.All_Tags('')
        index = self.search.index(key)
        result = '' if index==0 else self.search[index-1]
        return result

    def Key_To_ID(self, key):
        return [k for k in self.tree.IdToKey if (self.tree.IdToKey[k] == key)][0]

    def Select(self, key=''):
        iid = self.Key_To_ID(key)
        self.tree.Widget.see(iid)
        self.tree.Widget.selection_set(iid)

    def Move_Up(self, values):
        key = self.Where()
        if key == '':
            return
        node = self.treedata.tree_dict[key]
        if key == '': return
        pre = self.Previous_Key(key)
        pre_node = self.treedata.tree_dict[pre]
        if pre == '': return
        if pre == node.parent:
            pre_parent_node = self.treedata.tree_dict[pre_node.parent]
            index = pre_parent_node.children.index(pre_node)
            pre_parent_node.children = (pre_parent_node.children[:index] +
                [node] + pre_parent_node.children[index:])
            self.treedata.tree_dict[node.parent].children.remove(node)
            node.parent = pre_parent_node.key
        else:
            if node.parent == pre_node.parent:
                parent_node = self.treedata.tree_dict[node.parent]
                index = parent_node.children.index(pre_node)
                parent_node.children.remove(node)
                parent_node.children = (parent_node.children[:index] +
                    [node] + parent_node.children[index:])
            else:
                pre_parent_node = self.treedata.tree_dict[pre_node.parent]
                pre_parent_node.children.append(node)
                self.treedata.tree_dict[node.parent].children.remove(node)
                node.parent = pre_parent_node.key
        self.tree.Update(values=self.treedata)
        self.Select(key)

    def Next_Not_Children(self, key):
        self.All_Tags('')
        index = self.search.index(key) + 1
        while index < len(self.search):
            parent = []
            p = self.treedata.tree_dict[self.search[index]].parent
            while True:
                parent.append(p)
                p = self.treedata.tree_dict[p].parent
                if p == '': break
            if key in parent:
                index += 1
            else:
                return self.search[index]
        return None

    def Move_Down(self, values):
        key = self.Where()
        if key == '': return
        nxt = self.Next_Not_Children(key)
        if nxt == None: return
        node = self.treedata.tree_dict[key]
        nxt_node = self.treedata.tree_dict[nxt]
        if nxt_node.children == []:
            self.treedata.tree_dict[node.parent].children.remove(node)
            parent_node = self.treedata.tree_dict[nxt_node.parent]
            index = parent_node.children.index(nxt_node)
            parent_node.children = (parent_node.children[:index+1] +
                [node] + parent_node.children[index+1:])
            node.parent = nxt_node.parent
        else:
            self.treedata.tree_dict[node.parent].children.remove(node)
            nxt_node.children = [node] + nxt_node.children
            node.parent = nxt_node.key
        self.tree.Update(values=self.treedata)
        self.Select(key)

    def Where(self):
        item = self.tree.Widget.selection()
        return '' if len(item) == 0 else self.tree.IdToKey[item[0]]

G = GUI()
G.Window(G.Layout())
G.Load_Book()
func = {'Load File':G.Load_File, 'Load Path':G.Load_Path, 'Sort'   :G.Sort,
        'Rename'   :G.Rename,    'Delete'   :G.Delete,    'Move Up':G.Move_Up,
        'Move Down':G.Move_Down}
while True:

    event, values = G.window.Read()

    if event in [None, 'Quit']:
        break

    elif event in func:
        func[event](values)

    key = G.Where()
    txt = G.treedata.tree_dict[key].values[0] if key else ''
    G.multiline.Update(value=txt)

G.Save_Book()
G.window.close()
