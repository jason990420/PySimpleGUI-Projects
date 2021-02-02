import ctypes
from pathlib import Path
import PySimpleGUI as sg

def byte_layout(rows, cols):
    result = []
    for row in range(rows):
        line = []
        for col in range(cols):
            if col:
                line.append(sg.Text(' ', size=(1, 1), pad=(0, 0)))
            line.append(sg.Text('00', size=(2, 1), pad=(0, 0), key=(row, col)))
        result.append(line)
    return result

def byte_offset(rows, cols):
    return [[sg.Text(f'{row*cols:0>8x}', size=(8, 1), pad=(0, 0), key=row)]
        for row in range(rows)]

def update_data(window, data, position, rows, cols):
    if data is None:
        return
    for row in range(rows):
        for col in range(cols):
            try:
                value = data[(position+row)*cols+col]
                window[(row, col)].update(f'{value:0>2x}')
            except:
                window[(row, col)].update('  ')

        window[row].update(f'{(position+row)*cols:0>8x}')

rows, cols, limit = 16, 16, 0

ctypes.windll.user32.SetProcessDPIAware()   # Set unit of GUI to pixels
sg.theme("DarkBlue")
sg.set_options(font=("Courier New", 16, 'bold'))

frame_layout = [
    [sg.Column(byte_offset(rows, cols)), sg.Column(byte_layout(rows, cols))]
]
option = {
    'range':(0, limit), 'size':(22, 24), 'orientation':'v',
    'resolution':1, 'pad':(0, 0), 'disable_number_display':True,
    'enable_events':True}
layout = [
    [sg.InputText("", visible=False, enable_events=True, key="FILE"),
     sg.FileBrowse(key='BROWSE'),
     sg.Text("Goto Offset"),
     sg.Input("", size=(14, 1), key='OFFSET'),
     sg.Radio("Decimal", 'Unit', default=True, key='DEC'),
     sg.Radio("Hexadecimal", 'Unit', key='HEX'),
     ],
    [sg.Text("Filename: None", size=(66, 1), background_color='blue', key='FILENAME')],
    [sg.Frame("", frame_layout),
     sg.Slider(**option, key='V_Scrollbar'),],
    [sg.StatusBar("", size=(30, 1), key="Status")],
]

window = sg.Window("Binary Viewer 1.0", layout, finalize=True)
window['OFFSET'].bind('<Return>', "")
for key in ['BROWSE', 'OFFSET']:
    window[key].Widget.configure(takefocus=0)
data = None
while True:

    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    elif event == 'FILE':
        filename = values[event]
        path = Path(filename)
        if path.is_file():
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                file_size = len(data)
                upper = file_size//cols+1
                if file_size//cols*cols == file_size:
                    upper = file_size//cols
                limit = 0 if upper-rows<0 else upper-rows
                window['V_Scrollbar'].update(value=1, range=(0, limit))
                window['Status'].update(f"File size: 0x{file_size:x}")
                position = 0
                update_data(window, data, position, rows, cols)
                file = filename if len(filename)<=66 else filename[:30]+"..."+filename[-33:]
                window['FILENAME'].update(file)
            except:
                window['Status'].update("File open error !")

    elif event == 'V_Scrollbar':
        position = int(values[event])
        position = min(max(0, position), limit)
        update_data(window, data, position, rows, cols)

    elif event == 'OFFSET':
        text = values[event]
        if not text:
            window['Status'].update("No offset set !")
            continue
        base = 10 if window['DEC'].get() else 16
        try:
            value = int(text, base=base)
        except:
            window['Status'].update("Wrong number !")
            continue
        position = min(max(0, value//cols), limit)
        update_data(window, data, position, rows, cols)
        window['V_Scrollbar'].update(value=position)
        window['Status'].update(f'Offset:0x{value:0>8x}')

    print(event, values)

window.close()