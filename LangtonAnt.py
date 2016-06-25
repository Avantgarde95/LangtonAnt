#!usr/bin/env python

# import sys
import os

__author__ = 'Hun Min Park'
__version__ = '1.0'
__license__ = 'MIT'

# ---------------------------------------------------

try:
    import Tkinter as tk
    import tkMessageBox
except ImportError:
    print 'Error : Failed to import Tkinter module'
    raw_input('Press Enter to exit')
    os._exit(2)

try:
    from PIL import Image, ImageDraw, ImageTk
except ImportError:
    print 'Error : PIL (Pillow) is not installed'\
            ' or not properly installed'
    raw_input('Press Enter to exit')
    os._exit(2)

# ---------------------------------------------------

path_curr = os.path.dirname(os.path.abspath(__file__))

try:
    image_icon = Image.open(os.path.join(
        path_curr, 'icon.ico'))
    image_ant = Image.open(os.path.join(
        path_curr, 'ant.png'))
except IOError:
    print 'Error : Can\'t find the resource'
    raw_input('Press Enter to exit')
    os._exit(3)

turntable = {
    ('U', 'R') : 'R',
    ('U', 'L') : 'L',
    ('D', 'R') : 'L',
    ('D', 'L') : 'R',
    ('R', 'R') : 'D',
    ('R', 'L') : 'U',
    ('L', 'R') : 'U',
    ('L', 'L') : 'D'
}

text_about = '''Langton\'s ant

About : Simple simulation of (multi-color version of) Langton\'s ant
Author : Hun Min Park
Written in : python 2.7
Source : https://github.com/Avantgarde95/LangtonAnt
References : https://en.wikipedia.org/wiki/Langton%27s_ant'''

text_help = '''To open the control panel, press [File] - [Open
control panel].
In the control panel, input the values in the entries and press
\'load\' to reset the board.
And then, press \'run\'/\'stop\' to let the ant move/stop.

For detailed information about Langton\'s ant, see the following
link : https://en.wikipedia.org/wiki/Langton%27s_ant'''

# ---------------------------------------------------

def generate_colors(period):
    colortable = [(255, 255, 255, 255)]
    dc = 255/(period-1)

    for i in xrange(period):
        r = 255 - dc*(i+1)
        g, b = r, r
        a = 255

        colortable.append((r, g, b, a))

    return colortable

# ---------------------------------------------------

class MainApp(tk.Frame, object):
    def __init__(self, parent = None):
        self.parent = parent
        super(MainApp, self).__init__(self.parent)

        #self.parent.resizable(0, 0)
        self.parent.protocol('WM_DELETE_WINDOW', self.quit)
        self.icon = ImageTk.PhotoImage(image_icon)
        self.parent.tk.call(
            'wm', 'iconphoto', self.parent._w, self.icon)

        self.initialize()
        self.init_frames()
        self.init_menubar()
        self.init_board()

    def initialize(self):
        self.flag_control = False
        self.flag_about = False
        self.flag_help = False

        self.cell_width, self.cell_height = 20, 20
        self.dim_x, self.dim_y = 15, 15
        self.start_x, self.start_y = 7, 7
        self.dt = 500

        self.ant_x, self.ant_y = self.start_x, self.start_y 
        self.ant_direction = 'R'

        self.pattern = 'RL'
        self.period = len(self.pattern)
        self.state = [[0 for j in xrange(self.dim_x)] 
                      for i in xrange(self.dim_y)]
        self.colortable = [
            (255, 255, 255, 255),
            (0, 0, 0, 255)]

        self.id_step = None

    def init_frames(self):
        pass

    def init_menubar(self):
        self.menu_main = tk.Menu(self.parent)
        
        self.menu_file = tk.Menu(
            self.menu_main, tearoff = 0)
        self.menu_file.add_command(
            label = 'Open control panel',
            command = self.open_control)
        self.menu_file.add_command(
            label = 'Quit',
            command = self.quit)

        self.menu_help = tk.Menu(
            self.menu_main, tearoff = 0)
        self.menu_help.add_command(
            label = 'About',
            command = self.open_about)
        self.menu_help.add_command(
            label = 'Help',
            command = self.open_help)

        self.menu_main.add_cascade(
            label = 'File',
            menu = self.menu_file)
        self.menu_main.add_cascade(
            label = 'Help',
            menu = self.menu_help)

        self.parent.config(menu = self.menu_main)

    def init_board(self):
        self.board = tk.Canvas(self)
        self.board.pack()
        self.open_control()
        self.update_board()
    
    def update_board(self):
        self.board.delete('all')

        self.board_width = self.cell_width * self.dim_x
        self.board_height = self.cell_height * self.dim_y

        self.board.configure(
            width = self.board_width,
            height = self.board_height)

        self.draw_bg()
        self.draw_grid()
        self.draw_cells()
        self.draw_ant()

    def draw_bg(self):
        self.image_bg = Image.new(
            'RGBA', (self.board_width, self.board_height),
            (255, 255, 255, 255))
        
        self.imagetk_bg = ImageTk.PhotoImage(self.image_bg)

        coor_x, coor_y\
                = self.board_width/2, self.board_height/2
        
        self.board.create_image(
            (coor_x, coor_y), image = self.imagetk_bg,
            tags = 'bg')

    def draw_grid(self):
        self.image_grid = Image.new(
            'RGB', (self.board_width, self.board_height),
            (255, 255, 255))
        self.drawobj_grid = ImageDraw.Draw(self.image_grid)

        x0, x1 = self.cell_width, self.board_width
        y0, y1 = self.cell_height, self.board_height
        dx, dy = self.cell_width, self.cell_height

        _draw_line = self.drawobj_grid.line

        for x in xrange(x0, x1, dx):
            _draw_line((x, 0, x, y1), fill = 0)
        
        for y in xrange(y0, y1, dy):
            _draw_line((0, y, x1, y), fill = 0)
       
        coor_x, coor_y\
                = self.board_width/2, self.board_height/2

        self.imagetk_grid = ImageTk.PhotoImage(self.image_grid)
        
        self.id_grid = self.board.create_image(
            (coor_x, coor_y), image = self.imagetk_grid,
            tags = 'grid')

    def draw_cells(self):
        self.image_cells = Image.new(
            'RGBA', (self.board_width, self.board_height),
            (255, 255, 255, 0))
        
        self.drawobj_cells = ImageDraw.Draw(self.image_cells)

        coor_x, coor_y\
                = self.board_width/2, self.board_height/2
        
        self.imagetk_cells = ImageTk.PhotoImage(
            self.image_cells)
        
        self.id_cells = self.board.create_image(
            (coor_x, coor_y), image = self.imagetk_cells,
            tags = 'grid')

    def draw_ant(self):
        coor_x = self.cell_width * (self.ant_x+1)\
                - self.cell_width/2
        coor_y = self.cell_height * (self.ant_y+1)\
                - self.cell_height/2

        self.imagetk_ant = ImageTk.PhotoImage(
            image_ant.resize(
                (self.cell_width, self.cell_height),
                Image.ANTIALIAS))
         
        self.id_ant = self.board.create_image(
            (coor_x, coor_y), image = self.imagetk_ant,
            tags = 'ant')

    def open_control(self):
        if self.flag_control:
            return

        self.root_control = tk.Toplevel(self.parent)
        self.root_control.wm_title('Control panel')
        self.root_control.protocol(
            'WM_DELETE_WINDOW', self.close_control)
        self.control = ControlApp(self.root_control)

        self.control.button_reset.configure(
            command = self.reset)
        self.control.button_run.configure(
            command = self.run)
        self.control.button_stop.configure(
            command = self.stop)

        self.set_control()
        self.control.pack()
        self.control.focus_set()
        self.flag_control = True

    def close_control(self):
        self.root_control.destroy()
        self.control = None
        self.flag_control = False
    
    def set_control(self):
        self.control.entry_cell_width.insert(0, self.cell_width)
        self.control.entry_cell_height.insert(
            0, self.cell_height)
        self.control.entry_dim_x.insert(0, self.dim_x)
        self.control.entry_dim_y.insert(0, self.dim_y)
        self.control.entry_start_x.insert(0, self.start_x)
        self.control.entry_start_y.insert(0, self.start_y)
        self.control.entry_pattern.insert(0, self.pattern)
        self.control.entry_dt.insert(0, self.dt)
    
    def open_about(self):
        if self.flag_about:
            return
        
        self.root_about = tk.Toplevel(self.parent)
        self.root_about.wm_title('About')
        self.root_about.protocol(
            'WM_DELETE_WINDOW', self.close_about)
        self.about = TextApp(
            self.root_about, contents = text_about)
        self.about.pack()

        self.flag_about = True

    def close_about(self):
        self.root_about.destroy()
        self.about = None
        self.flag_about = False
    
    def open_help(self):
        if self.flag_help:
            return
        
        self.root_help = tk.Toplevel(self.parent)
        self.root_help.wm_title('Help')
        self.root_help.protocol(
            'WM_DELETE_WINDOW', self.close_help)
        self.help_ = TextApp(
            self.root_help, contents = text_help)
        self.help_.pack()

        self.flag_help = True

    def close_help(self):
        self.root_help.destroy()
        self.help_ = None
        self.flag_help = False

    def update_cell(self, x = 0, y = 0):
        x0, x1 = self.cell_width*x, self.cell_width*(x+1)
        y0, y1 = self.cell_height*y, self.cell_height*(y+1)
        
        self.state[y][x] = (self.state[y][x]+1) % self.period
        
        self.drawobj_cells.rectangle(
            (x0, y0, x1, y1),
            fill = self.colortable[self.state[y][x]],
            outline = (0, 0, 0, 255))

        coor_x, coor_y\
                = self.board_width/2, self.board_height/2
        
        self.imagetk_cells = ImageTk.PhotoImage(
            self.image_cells)
        
        self.board.itemconfig(
            self.id_cells, image = self.imagetk_cells)

    def move_ant(self, dx, dy):
        self.ant_x += dx
        self.ant_y += dy

        self.board.move(
            self.id_ant,
            self.cell_width * dx, self.cell_height * dy)

    def step(self):
        if self.ant_x <= 0 or self.ant_x >= self.dim_x-1\
           or self.ant_y <= 0 or self.ant_y >= self.dim_y-1:
            self.stop()
            return

        pattern_curr = self.pattern[
            self.state[self.ant_y][self.ant_x]]

        self.ant_direction = turntable[
            (self.ant_direction, pattern_curr)]

        self.update_cell(self.ant_x, self.ant_y)

        d = self.ant_direction

        if d == 'U':
            self.move_ant(0, -1)
        elif d == 'D':
            self.move_ant(0, 1)
        elif d == 'R':
            self.move_ant(1, 0)
        elif d == 'L':
            self.move_ant(-1, 0)
        else:
            pass

        self.id_step = self.board.after(self.dt, self.step)

    def reset(self):
        data = self.control.read_inputs()
        
        if data == -1:
            return

        self.stop()
        
        self.cell_width = data['cell_width']
        self.cell_height = data['cell_height']
        self.dim_x = data['dim_x']
        self.dim_y = data['dim_y']
        self.start_x = data['start_x']
        self.start_y = data['start_y']
        self.pattern = data['pattern']
        self.dt = data['dt']

        self.ant_x, self.ant_y = self.start_x, self.start_y
        self.ant_direction = 'R'
        self.period = len(self.pattern)
        self.state = [[0 for j in xrange(self.dim_x)] 
                      for i in xrange(self.dim_y)]
        self.colortable = generate_colors(self.period)

        self.update_board()

    def run(self):
        if self.id_step == None:
            self.step()

    def stop(self):
        if self.id_step != None:
            self.board.after_cancel(self.id_step)
            self.id_step = None

    def quit(self):
        if self.flag_control:
            self.close_control()

        self.parent.destroy()

# ---------------------------------------------------

class ControlApp(tk.Frame, object):
    def __init__(self, parent = None):
        self.parent = parent
        
        self.parent.resizable(0, 0)
        self.icon = ImageTk.PhotoImage(image_icon)
        self.parent.tk.call(
            'wm', 'iconphoto', self.parent._w, self.icon)
        
        super(ControlApp, self).__init__(self.parent)

        self.init_frames()
        self.init_inputs_cell()
        self.init_inputs_dim()
        self.init_inputs_start()
        self.init_inputs_pattern()
        self.init_inputs_dt()
        self.init_buttons()

    def init_frames(self):
        self.frame_whole = tk.Frame(self)
        self.frame_whole.pack(padx = 20, pady = 6)
        
        self.frame_inputs = tk.Frame(self.frame_whole)
        self.frame_buttons = tk.Frame(self.frame_whole)
        self.frame_inputs.pack()
        self.frame_buttons.pack(pady = 2)

    def init_inputs_cell(self):
        self.label_cell_width = tk.Label(
            self.frame_inputs,
            text = 'Cell width')
        self.entry_cell_width = tk.Entry(
            self.frame_inputs,
            width = 20)
        self.label_cell_height = tk.Label(
            self.frame_inputs,
            text = 'Cell height')
        self.entry_cell_height = tk.Entry(
            self.frame_inputs,
            width = 20)

        self.label_cell_width.grid(
            row = 0, column = 0, padx = 5, pady = 2)
        self.entry_cell_width.grid(
            row = 0, column = 1, padx = 5, pady = 2)
        self.label_cell_height.grid(
            row = 1, column = 0, padx = 5, pady = 2)
        self.entry_cell_height.grid(
            row = 1, column = 1, padx = 5, pady = 2)

    def init_inputs_dim(self):
        self.label_dim_x = tk.Label(
            self.frame_inputs,
            text = 'Size of row')
        self.entry_dim_x = tk.Entry(
            self.frame_inputs,
            width = 20)
        self.label_dim_y = tk.Label(
            self.frame_inputs,
            text = 'Size of column')
        self.entry_dim_y = tk.Entry(
            self.frame_inputs,
            width = 20)

        self.label_dim_x.grid(
            row = 2, column = 0, padx = 5, pady = 2)
        self.entry_dim_x.grid(
            row = 2, column = 1, padx = 5, pady = 2)
        self.label_dim_y.grid(
            row = 3, column = 0, padx = 5, pady = 2)
        self.entry_dim_y.grid(
            row = 3, column = 1, padx = 5, pady = 2)

    def init_inputs_start(self):
        self.label_start_x = tk.Label(
            self.frame_inputs,
            text = 'Ant\'s position (x)')
        self.entry_start_x = tk.Entry(
            self.frame_inputs,
            width = 20)
        self.label_start_y = tk.Label(
            self.frame_inputs,
            text = 'Ant\'s position (y)')
        self.entry_start_y = tk.Entry(
            self.frame_inputs,
            width = 20)

        self.label_start_x.grid(
            row = 4, column = 0, padx = 5, pady = 2)
        self.entry_start_x.grid(
            row = 4, column = 1, padx = 5, pady = 2)
        self.label_start_y.grid(
            row = 5, column = 0, padx = 5, pady = 2)
        self.entry_start_y.grid(
            row = 5, column = 1, padx = 5, pady = 2)

    def init_inputs_pattern(self):
        self.label_pattern = tk.Label(
            self.frame_inputs,
            text = 'Pattern')
        self.entry_pattern = tk.Entry(
            self.frame_inputs,
            width = 20)

        self.label_pattern.grid(
            row = 6, column = 0, padx = 5, pady = 2)
        self.entry_pattern.grid(
            row = 6, column = 1, padx = 5, pady = 2)

    def init_inputs_dt(self):
        self.label_dt = tk.Label(
            self.frame_inputs,
            text = 'Time interval (ms)')
        self.entry_dt = tk.Entry(
            self.frame_inputs,
            width = 20)

        self.label_dt.grid(
            row = 7, column = 0, padx = 5, pady = 2)
        self.entry_dt.grid(
            row = 7, column = 1, padx = 5, pady = 2)

    def init_buttons(self):
        self.button_reset = tk.Button(
            self.frame_buttons,
            text = 'load', command = self.read_inputs)
        self.button_run = tk.Button(
            self.frame_buttons,
            text = 'run', command = None)
        self.button_stop = tk.Button(
            self.frame_buttons,
            text = 'stop', command = None)

        self.button_reset.grid(
            row = 0, column = 0, padx = 25, pady = 2)
        self.button_run.grid(
            row = 0, column = 1, padx = 25, pady = 2)
        self.button_stop.grid(
            row = 0, column = 2, padx = 25, pady = 2)

    def raise_error(self, title = 'Error', message = 'Error'):
        tkMessageBox.showerror(title, message)

    def read_inputs(self):
        cell_range = (2, 40+1)
        dim_range = (10, 200+1)
        pattern_range = (2, 20+1)
        
        board_max = 1000

        data = {}

        try:
            data['cell_width'] = int(
                self.entry_cell_width.get())
            data['cell_height'] = int(
                self.entry_cell_height.get())
            data['dim_x'] = int(self.entry_dim_x.get())
            data['dim_y'] = int(self.entry_dim_y.get())
            data['start_x'] = int(self.entry_start_x.get())
            data['start_y'] = int(self.entry_start_y.get())
            data['pattern'] = self.entry_pattern.get()
            data['dt'] = int(self.entry_dt.get())
        except ValueError:
            self.raise_error(message = 'Received non-integer')
            return -1

        if (data['cell_width'] not in xrange(*cell_range))\
           or (data['cell_height'] not in xrange(*cell_range)):
            self.raise_error(
                message = 'Cell size should be in %d - %d'
                % (cell_range[0], cell_range[1]-1))
            return -1

        if (data['dim_x'] not in xrange(*dim_range))\
           or (data['dim_y'] not in xrange(*dim_range)):
            self.raise_error(
                message = 'Row/column size should be in %d - %d'
                % (dim_range[0], dim_range[1]-1))
            return -1
       
        if (data['dim_x'] * data['cell_width'] > board_max)\
           or (data['dim_y'] * data['cell_height'] > board_max):
            self.raise_error(
                message = 'Board size too big!')
            return -1

        if (data['start_x'] not in xrange(0, data['dim_x']))\
           or (data['start_y'] not in xrange(0, data['dim_y'])):
            self.raise_error(
                message = 'Ant should be inside the board.')
            return -1
        
        if len(data['pattern']) not in xrange(*pattern_range):
            self.raise_error(
                message = 'Pattern length should be in %d - %d'
                % (pattern_range[0], pattern_range[1]-1))
            return -1

        for c in data['pattern']:
            if c not in ('R', 'L'):
                self.raise_error(
                    message = 'Pattern should only consists of'\
                    'R and L.')
                return -1

        if data['dt'] <= 0:
            self.raise_error(
                message = 'Time interval should be positive.')
            return -1

        return data

# ---------------------------------------------------

class TextApp(tk.Frame, object):
    def __init__(self, parent = None, contents = ''):
        self.parent = parent
        self.contents = contents

        self.parent.resizable(0, 0)
        self.icon = ImageTk.PhotoImage(image_icon)
        self.parent.tk.call(
            'wm', 'iconphoto', self.parent._w, self.icon)
        
        super(TextApp, self).__init__(self.parent)

        self.init_frames()
        self.init_contents()

    def init_frames(self):
        self.frame_contents = tk.Frame(
            self,
            relief = 'groove',
            borderwidth = 2)
        self.frame_contents.pack(padx = 10, pady = 10)
    
    def init_contents(self):
        self.label_contents = tk.Label(
            self.frame_contents,
            justify = 'left',
            text = self.contents)
        self.label_contents.pack(padx = 7, pady = 7)

if __name__ == '__main__':
    root = tk.Tk()
    root.wm_title('Langton\'s Ant')
    app = MainApp(root)
    app.pack()
    root.mainloop()
