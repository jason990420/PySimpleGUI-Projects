import pickle
from pathlib import Path
from tokenize import tokenize

import PySimpleGUI as sg

class GUI():

    def __init__(self):
        self.font1 = ('Courier New', 10)
        self.font2 = ('Courier New', 12, 'bold')
        self.button_size = 10
        self.line_width = 120
        self.book = 'Book.pkl'
        self.treedata = sg.TreeData()

    def layout(self):
        return [[self.Input('Load File'), self.Browse_File('Load File'),
                 self.Input('Load Path'), self.Browse_Path('Load Path'),
                 self.Button('Sort'),     self.Button('Rename'),
                 self.Button('Delete'),   self.Button('Quit')],
                [self.Tree('TREE'),       self.Multiline('MULTILINE')]]

    def Window(self, layout):
        self.window = sg.Window('Docstring for Python Files', layout=layout,
            margins=(0, 0), use_default_focus=False, finalize=True)
        self.tree = self.window['TREE']
        self.multiline = self.window['MULTILINE']
        self.tree.Widget.configure(show='tree')    # Invisiable Header
        for key, element in self.window.AllKeysDict.items():  # Remove dash box
            element.Widget.configure(takefocus=0)

    def Button(self, key):
        return sg.Button(key, enable_events=True, size=(self.button_size, 1),
            font=self.font2, pad=(5, 5))

    def Tree(self, key):
        return sg.Tree(data=self.treedata, headings=['Notes',], pad=(0, 0),
        show_expanded=False, col0_width=30, auto_size_columns=False,
        visible_column_map=[False,], select_mode=sg.TABLE_SELECT_MODE_BROWSE,
        enable_events=True, text_color='black', background_color='white',
        font=self.font2, num_rows=27, row_height=26, key=key)

    def Input(self, key):
        return sg.Input('', font=self.font2, key=key, visible=False,
            enable_events=True, do_not_clear=False, pad=((0, 5), 5))

    def Multiline(self, key):
        return sg.Multiline(default_text='', size=(self.line_width, 35),
            enable_events=False, pad=((0, 5), 0), focus=False, key=key,
            do_not_clear=True, disabled=True, border_width=0, font=self.font1,
            text_color='white', background_color='blue')

    def Browse_File(self, key):
        return sg.FileBrowse(button_text=key, target=key, font=self.font2,
            size=(self.button_size, 1), enable_events=True, pad=((10, 5), 5),
            file_types=(("ALL Python Files", "*.py"),))

    def Browse_Path(self, key):
        return sg.FolderBrowse(button_text=key, target=key, font=self.font2,
            size=(self.button_size, 1), pad=(5, 5), enable_events=True)

    def parsing(self, path, root=''):
        # token.tok_name
        NAME, STRING, NEWLINE, INDENT, DEDENT, OP, COMMENT, NL = (
            1, 3, 4, 5, 6, 54, 60, 61)
        IDLE, CALL, PROCEDURE, ARGS, COLON, DOCSTRING = 0, 1, 2, 3, 4, 5
        forward = True
        with open(path, 'rb') as f:
            parent_key = self.new_key()
            self.treedata.insert(root, parent_key, path.stem, values=[''])
            parents = [parent_key]
            indents = [-1]
            tokens = list(tokenize(f.readline))
            mode, indent, args, doc_string, parentheses = IDLE, 0, '', '', 0
            i = 0
            while i < len(tokens):
                token = tokens[i]
                token_type, token_string = token.type, token.string
                if token_type in (INDENT, DEDENT):
                    if token_type == DEDENT:
                        indent -= 1
                        if indent == indents[-1]:
                            del parents[-1]
                            del indents[-1]
                    elif token_type == INDENT:
                        indent += 1
                elif (mode == IDLE and token_type == NAME and
                        token_string in ('def', 'class')):
                    mode = CALL
                    call = token_string + ' '
                elif mode==CALL and token_type == NAME:
                    mode = PROCEDURE
                    procedure = token_string
                    indent0 = indent
                elif mode==PROCEDURE and token_type == OP:
                    if token_string == ':':
                        mode = DOCSTRING
                        new_line = False
                        args = ':'
                    elif token_string == '(':
                        mode = ARGS
                        parentheses = 1
                        args = '('
                elif mode == ARGS:
                    if  token_type == OP:
                        if token_string == ')':
                            parentheses -= 1
                            if parentheses == 0:
                                mode = COLON
                        elif token_string == '(':
                            parentheses += 1
                        elif token_string == ',':
                            token_string += ' '
                    args += token_string
                elif mode == COLON:
                    if token_type == OP and token_string == ':':
                        mode = DOCSTRING
                        new_line = False
                    args += token_string
                elif mode == DOCSTRING:
                    flag = False
                    no_up = True
                    if new_line:
                        if token_type not in (NEWLINE, NL, COMMENT):
                            doc_string = token_string if token_type == STRING else ''
                            flag = True
                    else:
                        if token_type == STRING:
                            doc_string = token_string
                            flag = True
                        else:
                            if token_type in (NEWLINE, NL, COMMENT):
                                new_line = True
                            else:
                                doc_string = token_string if token_type == STRING else ''
                                flag = True
                                no_up = False
                    if flag:
                        args = args.replace('\r', ' ').replace('\n', ' ')
                        if doc_string:
                            doc_string = eval(doc_string).strip()
                            doc_string = '\n'.join(
                                map(str.strip, doc_string.split('\n')))
                        key = self.new_key()
                        self.treedata.insert(parents[-1], key, call+procedure, values=[call+procedure+args+'\n\n'+doc_string])
                        if no_up:
                            parents.append(key)
                            indents.append(indent0)
                        mode, args, doc_string, parentheses = IDLE, '', '', 0
                        i -= 1
                i += 1
        return

    def new_key(self):
        """
        Find a unique Key for new node, Key start from '0' and not in node list
        """
        i = 0
        while str(i) in self.treedata.tree_dict:
            i += 1
        return str(i)

    def load_book(self):
        """
        Read Book.json into treedata
        """
        if not Path(self.book).is_file():
            return
        with open(self.book, 'rb') as f:
            self.treedata = pickle.load(f)
        self.tree.update(values=self.treedata)

    def save_book(self):
        """
        Save treedata to Book.json
        Dictionary pairs in key: [parent, children, text, values]
        """
        with open(self.book, 'wb') as f:
            pickle.dump(self.treedata, f)

    def load_children(self, parent, children):
        for node in children:
            key = self.new_key()
            self.treedata.insert(parent, key, node.text, values=[node.value])
            self.load_children(key, node.child)

    def load_file(self, values):
        """
        Load Python file and parsing tokens.
        Two kinds of statements captured into treedata
          1. Name of class or function as Node name
          2. Definition of class or function with docstring as value
        """
        if values['Load File'] == '':
            return
        path = Path(values['Load File'])
        if not path.is_file():
            return
        self.parsing(path)
        self.tree.update(values=self.treedata)

    def load_path(self, values):
        if values['Load Path'] == '':
            return
        path = Path(values['Load Path'])
        if not path.is_dir():
            return
        key = self.new_key()
        self.treedata.insert('', key, path.stem, values=[''])
        for file in path.glob("*.py"):
            p = Path(file)
            if not p.is_file():
                continue
            self.parsing(p, key)
        self.tree.update(values=self.treedata)

    def convert(self, text):
        temp = text.replace('__init__', ' ')    # Set __init__ lowest
        temp = temp.replace('_', '|')           # Set '_' to highest
        return temp

    def sort(self, values):
        """
        Sort children list of all nodes by name.
        The order is __init__, uppercase letter, lowercase letter, then '_'
        """
        pre_select_key = self.where()
        for key, node in self.treedata.tree_dict.items():
            children = node.children
            node.children = sorted(                 # sort children by text
                children, key=lambda child: self.convert(child.text))
        self.tree.update(values=self.treedata)
        self.select(pre_select_key)

    def read_new_name(self):
        return sg.popup_get_text(message='New Name:', font=self.font1,
            default_text='', size=(40,1), no_titlebar=True, keep_on_top=True)

    def rename(self, values):
        key = self.where()
        if key:
            name = self.read_new_name()
            if name:
                self.treedata.tree_dict[key].text = name
                self.tree.update(key=key, text=name)

    def delete(self, values):
        key = self.where()
        if key:
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
            self.tree.update(values=self.treedata)
            self.select('')

    def all_tags(self, parent='', new=True):
        if new:
            self.search = []
        children = self.treedata.tree_dict[parent].children
        for child in children:
            self.search.append(child.key)
            self.all_tags(parent=child.key, new=False)

    def key_to_ID(self, key):
        return [k for k in self.tree.IdToKey if (self.tree.IdToKey[k] == key)][0]

    def select(self, key=''):
        iid = self.key_to_ID(key)
        self.tree.Widget.see(iid)
        self.tree.Widget.selection_set(iid)

    def where(self):
        item = self.tree.Widget.selection()
        return '' if len(item) == 0 else self.tree.IdToKey[item[0]]

sg.theme('DarkGreen')
g = GUI()
g.Window(g.layout())
g.load_book()
func = {'Load File':g.load_file, 'Load Path':g.load_path, 'Sort'   :g.sort,
        'Rename'   :g.rename,    'Delete'   :g.delete}

while True:
    event, values = g.window.Read()
    if event in [None, 'Quit']:
        break
    elif event in func:
        func[event](values)
    key = g.where()
    txt = g.treedata.tree_dict[key].values[0] if key else ''
    g.multiline.Update(value=txt)

g.save_book()
g.window.close()