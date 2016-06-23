from collections import defaultdict, namedtuple
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
        except TypeError:  # Circumstantially None.
            pass

    def __str__(self):
        return '<MapTile: {}>'.format(self.type)


class MapCell(object):
    """
    An object consisting of a MapTile object and a tk.Label of an image.
    Used where an tile and a tkImage are required.
    """

    def __init__(self, Tile, tkImg):
        self.tile = Tile
        self.tk_image = tkImg

    @property
    def type(self):
        return self.tile.type

    def action(self, moveTo, cellTo):
        self.tile.action(moveTo, cellTo)

    def replace_tile_image(self, tileImage):
        self.tk_image.configure(image=tileImage)

    def reset_tile_image(self):
        self.tk_image.configure(image=self.tile.image)

    def replace_tile(self, Tile):
        self.tile = Tile
        self.tk_image.configure(image=Tile.image)

    def __str__(self):
        return "<MapCell: {}>".format(self.type)

    def __repr__(self):
        return self.__str__()


class NavigationalFrame(tk.Frame):
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
        self.parent, self.tiles = Parent, Tiles
        self.player_tile = Tiles[playerTileType]
        self.player_i, self.player_j = None, None
        self.cells, self.cell_locations = {}, defaultdict(list)

    def build(self, Structure):
        for Index, tileType in self.iter_2d(Structure):
            self.cells[Index] = self.initiate_cell(Index, tileType)
            self.cell_locations[tileType].append(Index)
        startIndex = self.cell_locations[self.player_tile.type][-1]
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
        """Handle directional key-press or escape."""
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

    def reset(self):
        for child in self.winfo_children():
            child.destroy()
        self.cells.clear()
        self.cell_locations.clear()


class InventoryFrame(tk.Frame):

    invGroup = namedtuple("inventoryGroup", ["fill", "slots"])

    def __init__(self, Parent, Arranged='Vertically', *args, **kwargs):
        tk.Frame.__init__(self, Parent, *args, **kwargs)
        self.parent, self.inventory = Parent, {}
        self.group_pack = ('left' if Arranged == 'Horizontally' else 'top')

    def initialize_group(self, groupName, fillTile, slotAmount,
                         Arranged='Horizontally', *args, **kwargs):
        Slots, groupFrame = [], tk.Frame(self.parent, *args, **kwargs)
        groupFrame.pack(side=self.group_pack)
        for _ in range(slotAmount):
            tkImg = tk.Label(groupFrame, image=fillTile.image)
            tkImg.pack(side=('top' if Arranged == 'Vertically' else 'left'))
            Slots.append(MapCell(fillTile, tkImg))
        self.inventory[groupName] = self.invGroup(fillTile, Slots)

    def is_carrying(self, groupName, Tile):
        for Cell in self.inventory[groupName].slots:
            if Tile == Cell.tile:
                return True
        else:
            return False

    def include(self, groupName, includedTile):
        self.replace(groupName, self.inventory[groupName].fill, includedTile)

    def remove(self, groupName, replaceTile):
        self.replace(groupName, replaceTile, self.inventory[groupName].fill)

    def replace(self, groupName, removedTile, includedTile):
        removedTileType = removedTile.type
        for Cell in self.inventory[groupName].slots:
            if Cell.type == removedTileType:
                Cell.replace_tile(includedTile)
                break

    def reset(self):
        for fillTile, Slots in self.inventory:
            for Cell in Slots:
                Cell.replace_tile(fillTile)
