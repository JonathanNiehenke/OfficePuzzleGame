from collections import namedtuple
from itertools import chain, cycle
from tkinter import messagebox
import tkinter as tk

class MapFrame(tk.Frame):

    def __init__(self, Parent, Tiles, Handlers, *args, **kwargs):
        tk.Frame.__init__(self, Parent, *args, **kwargs)
        self.parent = Parent

        self.tile, self.handlers = Tiles, Handlers
        self.controls = dict(zip(
            chain(
                ['Up', 'Down', 'Left', 'Right'],
                ['w', 's', 'a', 'd'],
                ['i', 'k', 'j', 'l'],
                ['KP_Up', 'KP_Begin', 'KP_Left', 'KP_Right']),
            cycle([(-1 , 0), (1, 0), (0, -1), (0, 1)])
            ))
        self.player_i, self.player_j = None, None

    def build(self, Title, Structure):
        self.parent.title(Title)
        self.map_grid, self.locations = dict(), dict()

        for Index, Cell in self.iterate_2d(Structure):
            imgCell = tk.Label(self, image=self.tile[Cell])
            imgCell.grid(**Index._asdict())
            self.map_grid[Index] = (Cell, imgCell)
            try:
                self.locations[Cell].append(Index)
            except KeyError:
                self.locations[Cell] = [Index]

    def iterate_2d(self, Structure):
        gridIndex = namedtuple('gridIndex', ['row', 'column'])
        for Row, rowCells in enumerate(Structure):
            for Col, Cell in enumerate(rowCells):
                Index = gridIndex(Row, Col)
                yield Index, Cell

    def comunicate(self, Message):
        self.parent.title(Title)
        tk.Label(self, text=Message).place(relx=0.5, rely=0.5, anchor='center')

    def remove(self):
        for Children in list(self.children.values()):
            Children.destroy()

    def handle_key(self, Event):
        Keyed = Event.keysym
        try:
            I, J = self.controls[Keyed]
        except KeyError:
            if Keyed == 'Escape' and messagebox.askyesno('Quit?', 'You want to quit?'):
                self.parent.destroy()
            elif Keyed == 'F1':
                messagebox.showinfo('Help', 'This is the help.')
        else:
            moveTo = self.player_i + I, self.player_j + J
            cellType, _ = self.map_grid[moveTo]
            self.cell_action(moveTo, cellType)

    def cell_action(self, moveTo, cellType):
        try:
            self.handlers[cellType](moveTo, cellType)
        except KeyError:
            pass

    def move_player(self, indexTo, tileTo):
        replaceFrom, self.on_tile = self.on_tile, tileTo
        indexFrom = (self.player_i, self.player_j)
        self.change_cells((indexFrom, replaceFrom), (indexTo, '$'))
        self.player_i, self.player_j = indexTo

    def change_cells(self, *Pairs):
        for Index, Replace in Pairs:
            _, cellImg = self.map_grid[Index]
            cellImg.configure(image=self.tile[Replace])
            self.map_grid[Index] = (Replace, cellImg)

    def change_cell_image(self, *Pairs):
        for Index, Replace in Pairs:
            _, cellImg = self.map_grid[Index]
            cellImg.configure(image=self.tile[Replace])

"""
The inventory is used in two ways.
    A game mechanic - Calls for Value of Item.
    A information source- Displays certian items.

Argument for Inventory Object

Inventory is a container of items that are displayed to the player.
    Items are unique, stackable, and conditional.
A set would natually support the unique items.
A dictionary would naturally support the stackable (Name, Amount).
Currently the game wants a quick search so a dictionary is used.
But it needs to be organized for displaying.

It contains consistant variables with consistant functions.
    An organized dictionary of item types.
    Adding, removing, searching, and displaying.

The action of when to display should relay on the Inheritor Class.

Attributes of a displayed inventory.
    The groups of items.
    The amount of simutanius items displayed.
    The image of the items displayed.
    The location of the items displayed.
    The Label object of each item.
"""

class InventoryFrame(tk.Frame):

    def __init__(self, Parent, Tile, masterInventory, Fill=' '):
        tk.Frame.__init__(self, Parent)
        self.parent = Parent
        self.tile, self.fill = Tile, Tile[Fill]

        tk.Label(self, text='Inventory', font='-size 14 -weight bold').pack()
        self.items = dict()
        for Group, itemLst in masterInventory.items():
            groupFrame = tk.Frame(self)
            groupHead = tk.Label(groupFrame, text=Group, font='-weight bold')
            groupHead.pack(side='top')

            for Item in itemLst:
                itemLabel = tk.Label(groupFrame, image=self.fill)
                itemLabel.pack(side='left')
                self.items[Item] = itemLabel
            
            groupFrame.pack(fill='x')

    def display(self, *args):
        for Item in args:
            try:
                self.items[Item].config(image=self.tile[Item])
            except KeyError:
                pass


    def mask(self, *args):
        for Item in args:
            try:
                self.items[Item].config(image=self.fill)
            except KeyError:
                pass

class PinEntry(tk.Toplevel):

    def __init__(self, Parent, Answer, actionFunc, *funcArgs):
        tk.Toplevel.__init__(self, Parent, padx=5, pady=5)
        self.parent, self.answer = Parent, Answer
        self.action_func, self.func_args = actionFunc, funcArgs
        self.bind('<Return>', self.handle_field)
        self.bind('<KP_Enter>', self.handle_field)
        self.bind('<Escape>', lambda x: self.destroy())

        tk.Label(self, text='Input Security Pin').pack()
        self.entry= tk.Entry(self, width=len(Answer))
        self.entry.pack()
        self.entry.focus_set()
        self.status = tk.Label(self, text='')
        self.status.pack()

    def handle_field(self, _):
        if self.entry.get() == self.answer:
            self.action_func(*self.func_args)
            self.destroy()
        else:
            self.status.config(text='Incorrect Pin!')

def understand_legend(Legend, legendPath):
    Tile, Handler = dict(), dict()
    for Cell, (Name, Function) in mapLegend.items():
        imagePath = legendPath(Name)
        Tile[Cell] = tk.PhotoImage(file=imagePath)
        if handlingFunction is not None:
            Handler[Cell] = handlingFunction
    return Tile, Handler
