import os
import shutil
from pathlib import Path
import PySimpleGUI as sg
import sqlite3
import ctypes


class FILE():

    def __init__(self):
        self.file_directory = Path('D:/ALL')
        self.no_extension = 'No_Extension'
        if not self.file_directory.is_dir():
            self.file_directory.mkdir()

    def Create_Directory_By_File_Extension(self, path_object):
        suffix = path_object.suffix
        relative_path = self.no_extension if suffix=='' else suffix[1:].upper()
        directory = self.file_directory.joinpath(relative_path)
        if not directory.is_dir():
            directory.mkdir()
        return directory

    def Get_Path(self, text):
        path = Path(text)
        suffix = path.suffix
        sub_dir = self.no_extension if suffix == '' else suffix[1:].upper()
        result = self.file_directory.joinpath(sub_dir, path.name)
        return result

    def Move_File(self, file_object_from, file_object_to):
        if not file_object_from.is_file() or file_object_to.is_file():
            return False
        shutil.move(file_object_from, file_object_to)
        return True


class GUI():

    def __init__(self):
        self.title       = 'File Management System'
        self.font        = ('Courier New', 12, 'bold')
        self.button_size = (16, 1)
        self.select      = ['', '', '', '', '']
        self.index       = 0
        button00         = [['NEW TAG',  'New    Tag'],
                            ['ROOT TAG', 'Root   Tag'],
                            ['DELETE',   'Delete Tag']]
        button01         = [['RENAME',   'Rename Tag'],
                            ['SEARCH',   'Search Tag'],
                            ['NEXT ONE', 'Next   Tag']]
        button02         = [['SORTING' , 'Sort   Tag'],
                            ['MOVE UP',  'MoveUp Tag'],
                            ['MOVE DN',  'MoveDn Tag']]
        button10         = [['INSERT',   'Import Files'],
                            ['REMOVE',   'Remove Selection']]
        self.text0       = ['S1', 'S2', 'S3', 'S4', 'S5']
        self.text1       = ['T1', 'T2', 'T3', 'T4', 'T5']
        self.binds       = [['TREE0', '<Button-1>',        '_CLICK'],
                            ['TREE0', '<Double-Button-1>', '_DOUBLE'],
                            ['TREE1', '<Button-1>',        '_CLICK'],
                            ['TREE1', '<Double-Button-1>', '_DOUBLE']]
        layout0          = self.Frame([self.Buttons(button00),
                           self.Buttons(button01), self.Buttons(button02),
                           [T0]])
        layout1          = self.Frame([self.Buttons(button10),
                           self.Texts(self.text0, p=(7, 7)), [T1],
                           self.Texts(self.text1, p=(7, 7))])
        ctypes.windll.user32.SetProcessDPIAware()
        self.window      = sg.Window(self.title, layout=[[layout0, layout1]],
                                margins=(2, 2), finalize=True)
        self.Hide_Header()
        T0.Load_Tree(S.Load_Tag_Table())
        self.Binds()
        self.Disable_Insert()

    def _clear_frame1(self):
        self.index = 0
        self.select = ['', '', '', '', '']
        self._frame1_update()

    def _frame1_update(self):
        self._text0_update()
        self._tree1_update()
        self._text1_update()
        self.Disable_Insert()

    def _is_select_not_ok(self):
        return True if T0.Where() in ['']+self.select else False

    def _text0_append(self):
        if self.index == 5:
            self.select =  self.select[1:5]+['']
        self.index = self.index + 1 if self.index < 5 else 5
        self.select[self.index-1]=T0.Where()
        return

    def _text0_clear(self):
        self.index = 0
        self.select = ['', '', '', '', '']

    def _text0_update(self):
        for i in range(5):
            self.window[self.text0[i]].Update(
                value='' if self.select[i]=='' else
                    T0.treedata.tree_dict[self.select[i]].text)

    def _text1_update(self):
        value = T1.treedata.tree_dict[T1.Where()].values
        if value == []: value = ['', '', '', '', '']
        for i in range(5):
            text = '' if value[i]=='' else T0.treedata.tree_dict[value[i]].text
            self.window[self.text1[i]].Update(value=text)

    def _tree1_update(self):
        T1.Tree_Update(S.Load_File_Table())

    def Binds(self):
        for bind in self.binds: self.window[bind[0]].bind(bind[1], bind[2])

    def Disable_Insert(self):
        disabled = True if self.index == 0 else False
        self.window['INSERT'].Update(disabled=disabled)

    def Buttons(self, buttons):
        result = []
        for i, button in enumerate(buttons):
            pad = (0, (2, 0)) if i == 0 else ((3, 0), (2, 0))
            if button[0] == 'INSERT':
                result.append(sg.FilesBrowse(button[1], target=button[0],
                size=self.button_size, key=button[0], font=self.font, pad=pad,
                file_types=(('All files', '*.*'),), enable_events=True))
            else:
                result.append(sg.Button(button[1], auto_size_button=False,
                font=self.font, enable_events=True, size=self.button_size,
                key=button[0], pad=pad))
        return result

    def Frame(self, layout):
        return sg.Frame('', layout=layout, pad=(0, 0))

    def Hide_Header(self):
        T0.Widget.configure(show='tree')
        T1.Widget.configure(show='tree')

    def Insert(self):
        if self._is_select_not_ok(): return
        self._text0_append()
        self._frame1_update()

    def Pop(self, text):
        sg.PopupOK(text, font=self.font, no_titlebar=True)

    def Popup(self, text):
        text = sg.popup_get_text(message=text, font=self.font, size=(40,1),
            default_text='', no_titlebar=True, keep_on_top=True)
        return None if text == None or text.strip()=='' else text.strip()

    def Remove(self):
        if self.index == 0:
            return
        self.select[self.index-1] = ''
        self.index -= 1
        self._frame1_update()
        self.Disable_Insert()

    def Texts(self, texts, p, size=(20, 1)):
        result = []
        for i, text in enumerate(texts):
            pad = (0, p) if i == 0 else ((9, 0), p)
            result.append(sg.Text('', size=size, font=self.font,
            justification='center', auto_size_text=False, key=text,
            text_color='white', background_color='green', pad=pad))
        return result

class SQL():

    def __init__(self):
        self.database   = 'D:/ALL/file.db'
        self.file_table = 'file_table'
        self.file_cols  = ('filename', 'key1', 'key2', 'key3', 'key4', 'key5')
        self.tag_table  = 'tag_table'
        self.tag_cols   = ('key',)
        self.conn       = sqlite3.connect(self.database)
        self.c          = self.conn.cursor()
        self.Create_File_Table()
        self.Create_Tag_Table()

    def Commit(self, command):
        self.c.execute(command)
        self.conn.commit()

    def Create_File_Table(self):
        command = ('CREATE TABLE IF NOT EXISTS file_table '
                   '(filename TEXT, key1 TEXT, key2 TEXT, key3 TEXT, '
                   'key4 TEXT, key5 TEXT)')
        self.Commit(command)

    def Create_Tag_Table(self):
        command = 'CREATE TABLE IF NOT EXISTS tag_table (key TEXT)'
        self.Commit(command)

    def Insert_File_Table(self, values):
        command = ('INSERT INTO file_table ' +
                   '(filename, key1, key2, key3, key4, key5) VALUES ' +
                   repr(tuple(values)))
        self.Commit(command)

    def Load_File_Table(self):
        if G.index == 0: return []
        t1 = "'), ('".join(G.select[:G.index])
        command = """
            with list(col) as (VALUES ('""" +t1+"""')), cte as ( select rowid,
            ',' || key1 || ',' || key2 || ',' || key3 || ',' || key4 || ',' ||
            key5 || ',' col from file_table ) select * from file_table where
            rowid in ( select c.rowid from cte c inner join list l on c.col
            like '%,' || l.col || ',%' group by c.rowid having count(*) =
            (select count(*) from list) )"""
        self.Commit(command)
        return self.c.fetchall()

    def Load_Tag_Table(self):
        command = ' '.join(('SELECT * from', self.tag_table))
        self.Commit(command)
        data = self.c.fetchone()
        return None if data == None else eval(data[0])

    def Records_In_File_Table(self, key):
        command = ("SELECT * FROM file_table WHERE '" + key +
                   "' IN (key1, key2, key3, key4, key5)")
        self.Commit(command)
        result = self.c.fetchall()
        return result

    def Save_To_Tag_Table(self, dictionary):
        self.Commit(' '.join(('DELETE FROM', self.tag_table, 'WHERE ROWID=1')))
        command = ' '.join(('INSERT INTO', self.tag_table, '(',
            self.tag_cols[0], ')', 'VALUES', '(', repr(str(dictionary)), ')'))
        self.Commit(command)


class Tree0(sg.Tree):

    def __init__(self, key):

        self.font = ('Courier New', 12, 'bold')
        self.key = key
        self.search = []
        self.index = 0
        self.text = None
        self.treedata = sg.TreeData()
        super().__init__(data=self.treedata, col0_width=48, font=self.font,
            num_rows=20, row_height=30, background_color='white',
            show_expanded=False, justification='left', key=self.key,
            visible_column_map=[False,], auto_size_columns=False,
            headings=['Nothing',], enable_events=True,
            select_mode=sg.TABLE_SELECT_MODE_BROWSE, pad=(0, 0))

    def _delete_tag(self, key):
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

    def _is_root(self):
        return True if self.Where()=='' else False

    def _records(self, key):
        tag_list = [key] + self.All_Tags(key)
        records = 0
        for tag in tag_list:
            records += len(S.Records_In_File_Table(tag))
        return records

    def All_Tags(self, parent='', new=True):
        if new: self.search = []
        children = self.treedata.tree_dict[parent].children
        for child in children:
            self.search.append(child.key)
            self.All_Tags(parent=child.key, new=False)
        return self.search

    def Delete(self):
        key = self.Where()
        if self._is_root(): return
        if self._records(key)!= 0:
            G.Pop('Tag referenced by files, delete not allowed, revise tag first !')
            return
        previous_key = self.Previous_Key(key)
        self._delete_tag(key)
        self.Tree_Update()

        self.Expand(previous_key)
        self.Select(previous_key)
        G._clear_frame1()

    def Expand(self, key='', top=False):
        if top:
            children = self.treedata.tree_dict[key].children
            for child in children:
                kids = self.treedata.tree_dict[child.key].children
                for kid in kids:
                    self.Select(kid.key)
        else:
            children = self.treedata.tree_dict[key].children
            for child in children:
                self.Select(child.key)

    def _get_key(self):
        i = 1
        while True:
            if str(i) in self.treedata.tree_dict:
                i += 1
            else:
                return str(i)

    def Insert(self):
        text = G.Popup('New tag, same name allowed and as different tag.')
        if text == None: return
        parent = self.Where()
        key = self._get_key()
        self.treedata.insert(parent, key, text, [])
        self.Tree_Update()
        self.Select(key)
        self.Select(parent)

    def Key_To_ID(self, key):
        return [k for k in self.IdToKey if (self.IdToKey[k] == key)][0]

    def Load_Tree(self, dictionary):
        if dictionary == None:
            return
        children = dictionary[''][1]
        while children != []:
            temp = []
            for child in children:
                node = dictionary[child]
                self.treedata.insert(node[0], child, node[2], node[3])
                temp += node[1]
            children = temp
        self.Tree_Update()
        for child in self.treedata.tree_dict[''].children:
            self.Expand(child.key)
        self.Select('')

    def Move_Up(self):
        key = self.Where()
        node = self.treedata.tree_dict[key]
        if key == '': return
        pre = self.Previous_Key(key)
        pre_node = self.treedata.tree_dict[pre]
        if pre == '': return
        if pre == node.parent:
            pre_parent_node = self.treedata.tree_dict[pre_node.parent]
            index = pre_parent_node.children.index(pre_node)
            pre_parent_node.children = pre_parent_node.children[:index]+[node]+pre_parent_node.children[index:]
            self.treedata.tree_dict[node.parent].children.remove(node)
            node.parent = pre_parent_node.key
        else:
            if node.parent == pre_node.parent:
                parent_node = self.treedata.tree_dict[node.parent]
                index = parent_node.children.index(pre_node)
                parent_node.children.remove(node)
                parent_node.children = parent_node.children[:index]+[node]+parent_node.children[index:]
            else:
                pre_parent_node = self.treedata.tree_dict[pre_node.parent]
                pre_parent_node.children.append(node)
                self.treedata.tree_dict[node.parent].children.remove(node)
                node.parent = pre_parent_node.key
        self.Tree_Update()
        self.Select(key)

    def Move_Down(self):
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
            parent_node.children = parent_node.children[:index+1]+[node]+parent_node.children[index+1:]
            node.parent = nxt_node.parent
        else:
            self.treedata.tree_dict[node.parent].children.remove(node)
            nxt_node.children = [node] + nxt_node.children
            node.parent = nxt_node.key
        self.Tree_Update()
        self.Select(key)

    def Next_Key(self, key):
        self.All_Tags('')
        index = self.search.index(key)
        if index == len(self.search)-1: return None
        return self.search[index+1]

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

    def Previous_Key(self, key):
        self.All_Tags('')
        index = self.search.index(key)
        result = '' if index==0 else self.search[index-1]
        return result

    def Rename(self):
        key = self.Where()
        if key == '': return
        text = G.Popup('New tag name, same name allowed and as different tag.')
        if text == None: return
        self.treedata.tree_dict[key].text = text
        self.Update(key=key, text=text)
        G._text0_update()
        G._text1_update()

    def _search_text(self, text=None, next=False):
        if len(self.treedata.tree_dict) < 2: return
        if not next:
            self.All_Tags()
            self.text = text
            self.index = 0
        else:
            if self.text == None:
                return
            text = self.text
        length = len(self.search)
        for i in range(self.index, length):
            key = self.search[i]
            if text.upper() in self.treedata.tree_dict[key].text.upper():
                self.Select(key)
                self.index = i + 1 if i + 1 < length else 0
                return
        G.Pop('Tag not found !')
        self.index = 0

    def Search(self):
        text = G.Popup('Tag to search')
        if text != None: self._search_text(text)

    def Search_Next(self):
        self._search_text(next=True)

    def Select(self, key=''):
        iid = self.Key_To_ID(key)
        self.Widget.see(iid)
        self.Widget.selection_set(iid)

    def Sorting(self):
        for key, node in self.treedata.tree_dict.items():
            children = node.children
            node.children = sorted(children, key=lambda x: x.text)
        self.Tree_Update()
        self. Expand(top=True)
        self.Select('')

    def Tree_To_Dictionary(self):
        dictionary = {}
        for key, node in self.treedata.tree_dict.items():
            children = [n.key for n in node.children]
            dictionary[key]=[node.parent, children, node.text, node.values]
        return dictionary

    def Tree_Update(self):
        self.Update(values=self.treedata)

    def Where(self):
        item = self.Widget.selection()
        return '' if len(item) == 0 else self.IdToKey[item[0]]

class Tree1(sg.Tree):

    def __init__(self, key):
        self.font = ('Courier New', 12, 'bold')
        self.key = key
        self.treedata = sg.TreeData()
        super().__init__(data=self.treedata, col0_width=103, font=self.font,
            num_rows=20, row_height=30, background_color='white',
            show_expanded=False, justification='left', key=self.key,
            visible_column_map=[False,], auto_size_columns=False,
            headings=['Nothing',], enable_events=True,
            select_mode=sg.TABLE_SELECT_MODE_BROWSE, pad=(0, 0))

    def _get_key(self):
        i = 1
        while True:
            if str(i) in self.treedata.tree_dict:
                i += 1
            else:
                return str(i)

    def Execute(self):
        filename = F.Get_Path(self.treedata.tree_dict[self.Where()].text)
        if Path(filename).is_file:
            os.startfile(filename)
        else:
            G.Pop('File not exist !!')

    def Insert(self):
        if G.index == 0: return
        paths = values['INSERT'].split(';')
        for file in paths:
            path = Path(file)
            directory= F.Create_Directory_By_File_Extension(path)
            target = directory.joinpath(path.name)
            if F.Move_File(path, target):
                S.Insert_File_Table([target.name]+G.select)
                key = self._get_key()
                self.treedata.insert('', key, target.name, G.select)
        G._frame1_update()

    def Key_To_ID(self, key):
        return [k for k in self.IdToKey if (self.IdToKey[k] == key)][0]

    def Select(self, key=''):
        iid = self.Key_To_ID(key)
        self.Widget.see(iid)
        self.Widget.selection_set(iid)

    def Tree_Update(self, files):
        self.treedata = sg.TreeData()
        for file in files:
            key = self._get_key()
            self.treedata.insert('', key, file[0], file[1:])
        self.Update(values=self.treedata)
        self.Select('')

    def Where(self):
        item = self.Widget.selection()
        return '' if len(item) == 0 else self.IdToKey[item[0]]

F  = FILE()
S  = SQL()
T0 = Tree0('TREE0')
T1 = Tree1('TREE1')
G  = GUI()

function = {'NEW TAG':T0.Insert, 'ROOT TAG':T0.Select, 'DELETE':T0.Delete,
            'RENAME' :T0.Rename, 'SEARCH'  :T0.Search, 'INSERT':T1.Insert,
            'REMOVE' :G.Remove,  'NEXT ONE':T0.Search_Next,
            'TREE0_DOUBLE':G.Insert,   'TREE1_CLICK':G._text1_update,
            'TREE1_DOUBLE':T1.Execute, 'SORTING':T0.Sorting,
            'MOVE UP':T0.Move_Up, 'MOVE DN':T0.Move_Down}

while True:

    event, values = G.window.read()

    if event == None:
        break

    elif event in function:
        function[event]()

S.Save_To_Tag_Table(T0.Tree_To_Dictionary())
S.conn.close()
G.window.close()
del S, T0, T1, G