from collections import defaultdict, namedtuple, OrderedDict
from itertools import chain, cycle

import tkinter as tk
from tkinter import messagebox


class MapTile(object):
    """A object consisting of an action, image and type."""

    def __init__(self, tileType, imagePathname, actionFunction):
        self.actionFunction = actionFunction
        self.image = tk.PhotoImage(file=imagePathname)
        self.type = tileType

    def action(self, moveTo, cellTo):
        try:
            self.actionFunction(moveTo, cellTo)
        except TypeError:  # Circumstancually None.
            pass


class MapCell(object):
    """
    An object consisting of a MapTile object and a tk.Label of an image.
    """

    def __init__(self, Tile, tkImg):
        self.tile = Tile
        self.tkImg = tkImg

    @property
    def type():
        return self.tile.type

    def action(self, moveTo, cellTo):
        return self.tile.action(moveTo, cellTo)

    def replace_tile_image(self, tileImage):
        self.tkImg.configure(image=tileImage)

    def reset_tile_image(self):
        self.tkImg.configure(image=self.tile.image)

    def replace_tile(self, Tile):
        self.tile = Tile
        self.tkImg.configure(Tile.image)


class MapFrame(tk.Frame):
    """
    A continuous tk.Frame that displays and manages the graphical
    representation of the environments above view. Handles level loads,
    and keyboard input.
    """

    gridIndex = namedtuple('gridIndex', ['row', 'column'])
    directional_controls = dict(zip(
        chain(
            ['Up', 'Down', 'Left', 'Right'],
            ['w', 's', 'a', 'd'],
            ['i', 'k', 'j', 'l'],
            ['KP_Up', 'KP_Begin', 'KP_Left', 'KP_Right']),
        cycle([(-1 , 0), (1, 0), (0, -1), (0, 1)])
        ))

    def __init__(self, Parent, Tiles, playerTileType, *args, **kwargs):
        tk.Frame.__init__(self, Parent, *args, **kwargs)
        self.pack()
        self.parent, self.tiles = Parent, Tiles
        self.player_tile = Tiles[playerTileType]
        self.cells, self.cell_locations = {}, defaultdict(list)
        self.player_i, self.player_j = None, None

    def build(self, Structure):
        for Index, tileType in self.iter_2d(Structure):
            self.cells[Index] = self.initiate_cell(Index, tileType)
            self.cell_locations[tileType].append(Index)
        startIndex = self.cell_locations[self.player_tile.type][0]
        self.cells[startIndex] = self.initiate_cell(
            self.gridIndex(*startIndex), ' ')
        self.cells[startIndex].replace_tile_image(self.player_tile.image)
        self.player_i, self.player_j = startIndex

    def initiate_cell(self, Index, tileType):
        Tile = self.tiles[tileType]
        tkImg = tk.Label(self, image=Tile.image)
        tkImg.grid(**Index._asdict())
        return MapCell(Tile, tkImg)

    def iter_2d(self, Structure):
        for Row, rowCells in enumerate(Structure):
            for Col, tileType in enumerate(rowCells):
                yield self.gridIndex(Row, Col), tileType

    def handle_input(self, Event):
        """Handle directoinal keypress or escape."""
        keyPressed = Event.keysym
        try:
            I, J = self.directional_controls[keyPressed]
        except KeyError:
            if (keyPressed == "Escape" and
                    messagebox.askyesno("Quit?", "You want to quit?")):
                self.parent.destroy()
        else:
            moveTo = self.player_i + I, self.player_j + J
            self.cells[moveTo].action(moveTo, self.cells[moveTo])

    def move_player(self, moveTo, cellTo):
        cellFrom = self.cells[(self.player_i, self.player_j)]
        cellFrom.reset_tile_image()
        cellTo.replace_tile_image(self.player_tile.image)
        self.player_i, self.player_j = moveTo

"""
class InventoryFrame(tk.Frame):

    def __init__(self, Parent, *args, **kwargs):
        tk.Frame.__init__(self, Parent, *args, **kwargs)
        self.parent = Parent

    def include_inventory_group(self, groupName, )
        self.inventory[groupName]
"""
