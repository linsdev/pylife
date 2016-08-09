#!/usr/bin/env python3

from functools import partial
from threading import Thread
from time import sleep
from tkinter import Tk, messagebox, Canvas
from tkinter.ttk import Style, Frame, Button


class CanvasGrid(Canvas):
    def __init__(self, master=None, data=None, cell_size=10, color='green'):
        self.cell = data if data else [[False]]
        self._grid_width = len(self.cell)
        self._grid_height = len(self.cell[0])
        self._width = self._grid_width * cell_size
        self._height = self._grid_height * cell_size
        Canvas.__init__(self, master, width=self._width, height=self._height)
        self.cell_size = cell_size
        self.color = color
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', partial(self.on_click, motion=True))
        self.draw()

    def on_click(self, e, motion=False):
        if e.x in range(0, self._width) and e.y in range(0, self._height):
            e.x //= self.cell_size
            e.y //= self.cell_size
            #  "<=" is a pythonic implication logical operation
            self.cell[e.x][e.y] = self.cell[e.x][e.y] <= motion
            self.draw()

    def draw(self):
        self.delete('all')
        for y in range(0, self._grid_height):
            for x in range(0, self._grid_width):
                if self.cell[x][y]:
                    self.create_rectangle(
                            x * self.cell_size, y * self.cell_size,
                            (x+1) * self.cell_size, (y+1) * self.cell_size,
                            fill=self.color, width=0)


class World(CanvasGrid):
    def __init__(self, master=None, size=3, fps=10, on_stop=None):
        super().__init__(master, [[False] * size for _ in range(0, size)])
        self.size = size
        self.time_frame = 1 / fps
        self._on_stop = on_stop
        self.simulation = False

    def start(self):
        self.simulation = True
        Thread(target=self._next_loop).start()

    def stop(self):
        self.simulation = False
        self._on_stop and self._on_stop()

    def _next_loop(self):
        while self.simulation:
            sleep(self.time_frame)
            self.next()

    def for_all_cell(self, f):
        new_cell = [[False] * self.size for _ in range(0, self.size)]
        for y in range(0, self.size):
            for x in range(0, self.size):
                new_cell[x][y] = f(x, y)
        if self.simulation and self.cell == new_cell:
            self.stop()
            messagebox.showwarning('The simulation stopped',
                                   'Nothing alive or nothing changed')
            self.clear()
        else:
            self.cell = new_cell
            self.draw()

    def clear(self): self.for_all_cell(lambda x, y: False)

    def next(self):
        def f(x, y):
            neighbors = -self.cell[x][y]    # moore neighborhood
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    neighbors += self.cell[(x+dx) % self.size][(y+dy) % self.size]
            return neighbors == 2 and self.cell[x][y] or neighbors == 3

        self.for_all_cell(f)


class Window(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.resizable(False, False)
        self.master.title('The Game of Life')
        self.pack()

        self.button_start = Button(self, text='Start', command=self.button_start)
        self.button_start.grid(row=1, column=1, padx=8, pady=8)

        Button(self, text='Reset', command=self.button_reset).grid(row=2, column=1)

        self.world = World(self, 60, on_stop=self.button_start_text_reset)
        self.world.grid(row=1, column=2, rowspan=50)

    def button_start_text_reset(self):
        self.button_start['text'] = 'Start'

    def button_start(self):
        if self.world.simulation:
            self.world.stop()
            self.button_start_text_reset()
        else:
            self.world.start()
            self.button_start['text'] = 'Stop'

    def button_reset(self):
        self.world.stop()
        self.world.clear()
        self.button_start_text_reset()


if __name__ == '__main__':
    root = Tk()
    Style().theme_use('clam')
    Window(root)
    root.mainloop()

