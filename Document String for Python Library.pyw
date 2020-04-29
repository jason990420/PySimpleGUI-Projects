"""
Python Help File - Jason Yang 2019/01/17

Create Book to store major information from source code of Python packages.
It can help to view class or method quickly after you load the sourc codes.

Function Key:
    1. Buttons to load source code and sort all items
       (Should find the source code with major content of package)
    2. Right mouse button to rename or delete node.

Information will be shown:
    1. Class definition (class)
    2. Method definition (def)
    3. Document string (if soure code is well documented)

Note: All source codes should be with correct syntax.
"""
import os
import sys
from token import *
from tokenize import tokenize
from pathlib import Path
import PySimpleGUI as sg
import ctypes

def load(path, treedata, Parent=''):
    """
    Load Python file and parsing tokens.
    Capture two statements into treedata
    1. class name and text (definition, append document string)
    2. def name and text (definition, append document string)
    """
    try:
        with open(path, 'rb') as f:
            tokens = list(tokenize(f.readline))     # Covert .py into tokens
    except:
        sg.Popup('File Error or bad Python file!')  # Failed for open/read or
        return False                                # sytax error.
    filename = Path(path).stem                      # Get filename
    key = find_key(treedata)                        # Create a unique key
    treedata.Insert(Parent, key, filename, values=['']) # filename for root node
    key_list = [key]
    i = 0
    while i < len(tokens):                          # Search all tokens
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
                    key = find_key(treedata)        # New key
                    key_list += [key, ]
                    treedata.Insert(                # Insert one node of tree
                        key_list[level], key, name, values=[string])
                    break
                i += 1

        elif tok_name[tokens[i].type]=='STRING' and word.startswith('"""'):
            level = tokens[i].start[1]//4           # Document string
            if level > len(key_list)-1:
                level = len(key_list)-1
            t = treedata.tree_dict[key_list[level]].values[0]   # append text
            t += '\n' + word[3:-3]
            t = t.replace('\r\n', '\n').replace('\n\n', '\n').strip()
            treedata.tree_dict[key_list[level]].values[0] = t   # update text
        i += 1
    return True

def load_path(Parent, path, treedata):

    files = os.listdir(path)
    if files == []:
        return
    key = find_key(treedata)
    name = Path(path.lower()).stem
    treedata.Insert(Parent, key, name, values=[''])
    for p in files:
        pathname = Path(path, p)
        full_path = os.path.join(path, p)
        if pathname.is_file() and p.endswith('.py'):
            load(full_path, treedata, Parent=key)
        elif pathname.is_dir():
            load_path(key, full_path, treedata)
    return

class TreeRtClick(sg.Tree):
    '''
    GregSal commented on 24 Nov 2019
    https://github.com/PySimpleGUI/PySimpleGUI/issues/2234

    A variation of the Tree class that replaces the right-click callback
    function with one that first selects the tree item at the location of the
    right-click.
    '''
    def _RightClickMenuCallback(self, event):
        '''
        Replace the parent class' right-click callback function with one that
        first selects the tree item at the location of the right-click.
        '''
        tree = self.Widget  # Get the Tkinter Tree widget

        # These two calls are directly to the Tkinter Treeview widget.
        item_to_select = tree.identify_row(event.y) # Identify the tree item
        tree.selection_set(item_to_select)  # Set that item as selected.

        # Continue with normal right-click menu function.
        super()._RightClickMenuCallback(event)

class Tree_Data(sg.TreeData):
    """
    New Class for TreeData to create new methods
    move - Move node to under another node
    delete - Delete any node from tree
    save - Save treedata to 'Book.txt' file for using on next time.
    read - Read file 'Book.txt' file when script loading
    sort - Sord all node by name, __init__ first for more detail information
    """
    def __init__(self):

        super().__init__()

    def move(self, key1, key2):
        """
        Move node1/key1 to under node2/key2
        It will be failed if node2 is under node1
        """
        if key1 == '' and not self.is_legal_move(key1, key2):
            return False
        node = self.tree_dict[key1]
        parent1_node = self.tree_dict[node.parent]
        parent1_node.children.remove(node)      # removed from parent node
        parent2_node = self.tree_dict[key2]
        parent2_node.children.append(node)      # added into node2 children
        node.parent = parent2_node.key          # set node1.parent to node2
        return True

    def delete(self, key):
        """
        Delete node/key and all nodes under it
        """
        if key == '':
            return False
        node = self.tree_dict[key]
        node_list = [node, ]
        parent_node = self.tree_dict[node.parent]
        parent_node.children.remove(node)           # Removed node from parent
        while node_list != []:                      # delete all nodes under it
            temp = []
            for item in node_list:
                temp += item.children
                del item
            node_list = temp
        return True

    def is_legal_move(self, key1, key2):
        """
        Check if node2/keys is under node1/key1
        """
        node_list = [self.tree_dict[key1], ]
        node2 = self.tree_dict[key2]

        while node_list != []:
            if node2 in node_list:
                return False
            temp = []
            for node in node_list:
                temp += node.children
            node_list = temp

        return True

    def save(self, filename):
        """
        Save all required data in treedata to file by dictionary
        Dictionary with key: [parent, children, text and values]
        Saved by str(dictionary) method
        """
        dict = {}
        for key, node in self.tree_dict.items():
            children = [n.key for n in node.children]
            dict[key]=[node.parent, children, node.text, node.values]

        with open(filename, 'wt', encoding='utf-8') as f:
            f.write(str(dict))

    def read(self, filename):
        """
        Read treedata from file
        Insert Nodes from parent.children to parent, start from root
        """
        if not Path(filename).is_file():
            return
        with open(filename, 'rt', encoding='utf-8', newline='\n') as f:
            dict = eval(f.read())
        children = dict[''][1]
        while children != []:
            temp = []
            for child in children:
                node = dict[child]
                self.Insert(node[0], child, node[2], node[3])
                temp += node[1]
            children = temp

    def sort(self):
        """
        Sort children list of all nodes by name.

        The order is __init__, uppercase letter, lowercase letter, then '_'
        """
        def convert(text):
            temp = text.replace('__init__', ' ')    # Set __init__ lowest
            temp = temp.replace('_', '|')           # Set '_' to highest
            return temp

        for key, node in self.tree_dict.items():
            children = node.children
            node.children = sorted(                 # sort children by text
                children, key=lambda child: convert(child.text))

def Button(Key):
    # Easy method for sg.Button
    return sg.Button(Key, enable_events=True, size=(10, 1), font=Font)

def Load_File():
    # Easy method for sg.FileBrowse
    Key = 'Load File'
    return sg.FileBrowse(button_text=Key, target=Key, key=Key,
                size=(10, 1), font=Font, pad=(0, 0), enable_events=True,
                file_types=(("ALL Python Files", "*.py"),))

def Load_Path():
    Key = 'Load Path'
    return sg.FolderBrowse(button_text=Key, target=Key, key=Key,
                size=(10, 1), font=Font, pad=(0, 0), enable_events=True)

def Text(Key):
    # Easy method for sg.Multiline
    return sg.Multiline(default_text='', size=(120,33), enable_events=True,
                do_not_clear=True, key='Text', border_width=0, focus=False,
                font=Font, pad=(0, 0), text_color='white',
                background_color='blue')

def Tree(treedata):
    # Easy method for sg.Tree, here use class with modified method
    return TreeRtClick(
        data=treedata, headings=['Notes',], show_expanded=False, pad=(0, 0),
        col0_width=30, auto_size_columns=False, visible_column_map=[False,],
        select_mode=sg.TABLE_SELECT_MODE_BROWSE, enable_events=True,
        background_color='white', font=Small_Font, num_rows=33, row_height=23,
        key='Tree', right_click_menu=['Right',['Rename', 'Delete', 'Move']])

def find_key(treedata):
    """
    Find a unique Key for new node, Key start from '1' and not in node list
    """
    i = 0
    while True:
        i += 1
        if str(i) not in treedata.tree_dict:
            return str(i)

ctypes.windll.user32.SetProcessDPIAware()       # Set unit of GUI to pixels
Font = ('Courier New', 12, 'bold')
Small_Font =  ('Courier New', 11, 'bold')

treedata = Tree_Data()                          # Initial root node of Tree
treedata.read('Book.txt')                       # Load all treedata from file

Layout = [[Load_File(), Load_Path(), Button('Sort'), Button('Quit')],
          [Tree(treedata),Text('Text')]]
sg.theme('DarkPurple4')
Window = sg.Window('Python Book', layout=Layout, font=Font, finalize=True)
Window['Tree'].Widget.configure(show='tree')    # Invisiable Header
Window['Tree'].bind('<Button-1>', 'Down')       # add Button-1 event to Tree
Window['Text'].Widget.configure(wrap=None)      # Set Text no wrap

Mode = Key1 = Key2 = None
Note = True

while True:

    Event, Values = Window.read()

    if Event == None or Event == 'Quit':        # End of Script
        break

    elif Event == 'Load File':                  # Load from Python library file
        path = Values['Load File']
        if path in [None, '']:
            continue
        if path.lower().endswith('.py'):
            load(path, treedata)
            Window['Tree'].Update(values=treedata)
            Window.Refresh()

    elif Event == 'Load Path':
        path = Values['Load Path']
        if path in [None, '']:
            continue
        load_path('', path, treedata)
        Window['Tree'].Update(values=treedata)
        Window.Refresh()

    elif Event == 'Tree':                       # Update view on Text
        if Values['Tree']==[]:
            continue
        key = Values['Tree'][0]
        text = treedata.tree_dict[key].values[0]
        Window['Text'].Update(text)
        if Mode == 'Move':
            Key2 = key
            treedata.move(Key1, Key2)
            Window['Tree'].Update(values=treedata)
            Window['Text'].Update('')
            Mode = Key1 = Key2 = None

    elif Event == 'Rename':                     # Rename text name of node
        if Values['Tree']==[]:
            continue
        key = Values['Tree'][0]
        text = treedata.tree_dict[key].text
        t = sg.popup_get_text(message=f'Replace "{text}" with', font=Font,
            default_text=text, size=(40,1), no_titlebar=True, keep_on_top=True)
        if t != None:
            t = t.strip()
            treedata.tree_dict[key].text = t
            Window['Tree'].Update(key=key, text=t)

    elif Event == 'Delete':                     # Delete Node
        if Values['Tree']==[]:
            continue
        key = Values['Tree'][0]
        treedata.delete(key)
        Window['Tree'].Update(values=treedata)
        Window['Text'].Update('')

    elif Event == 'Move':                       # Move Node to
        if Values['Tree']==[]:                  # next clicked node
            continue
        Mode = 'Move'
        Key1 = Values['Tree'][0]
        if Note:
            sg.Popup('Click another label for destination.', font=Font)
            Note = False

    elif Event == 'Sort':                       # Sort all nodes by text
        treedata.sort()
        Window['Tree'].Update(values=treedata)
        Window['Text'].Update('')

treedata.save('Book.txt')                       # Save treedata before quit
del treedata                                    # deltete treedata
Window.close()