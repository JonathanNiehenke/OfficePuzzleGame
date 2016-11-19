from collections import defaultdict, namedtuple
from itertools import chain, cycle

import tkinter as tk
from tkinter import messagebox

db = print


class GameTile(object):
    """An object consisting of a type, an image, and an action."""

    def __init__(self, tileType, imagePathname, actionFunction):
        self.type = tileType
        self.image = tk.PhotoImage(file=imagePathname)
        self.actionFunction = actionFunction

    def action(self, moveTo, cellTo):
        try:
            self.actionFunction(moveTo, cellTo)
        except TypeError:  # Expecting NoneType.
            pass # Explicitly supressed.

    def __str__(self):
        return '<GameTile: {}>'.format(self.type)


class GameCell(object):
    """
    An object joining a GameTile object and a tk.Label of an image. Used
    where the identity or action of the tile and a tkImage are required.
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
        return "<GameCell: {}>".format(self.type)

    def __repr__(self):
        return self.__str__()


class NavigationalFrame(tk.Frame):
    """
    Manages the graphical representation of the environments above view.
    Including level loads and keyboard input.
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
        for Index, tileType in self.__iter_2d(Structure):
            self.cells[Index] = self.__initiate_game_cell(Index, tileType)
            self.cell_locations[tileType].append(Index)
        startIndex = self.cell_locations[self.player_tile.type][-1]
        # Properly placing player allows walkability of the startIndex.
        self.__properly_place_player(startIndex)
        self.player_i, self.player_j = startIndex

    def count_tile_types(self, tileType):
        return len(self.cell_locations.get(tileType, []))

    def __iter_2d(self, Structure):
        for Row, rowCells in enumerate(Structure):
            for Col, tileType in enumerate(rowCells):
                yield self.gridIndex(Row, Col), tileType

    def __initiate_game_cell(self, Index, tileType):
        Tile = self.tiles[tileType]
        tkImg = tk.Label(self, image=Tile.image)
        tkImg.grid(**Index._asdict())
        return GameCell(Tile, tkImg)

    def __properly_place_player(self, startIndex):
        self.cells[startIndex].replace_tile(self.tiles[' '])
        self.cells[startIndex].replace_tile_image(self.player_tile.image)

    def handle_key(self, keyPressed):
        """Handle directional key-press."""
        try:
            I, J = self.directional_controls[keyPressed]
        except KeyError:
            pass  # Explicitly silenced.
        else:
            moveTo = self.player_i + I, self.player_j + J
            self.cells[moveTo].action(moveTo, self.cells[moveTo])

    def move_player(self, moveTo, cellTo):
        cellFrom = self.cells[(self.player_i, self.player_j)]
        cellFrom.reset_tile_image()
        cellTo.replace_tile_image(self.player_tile.image)
        self.player_i, self.player_j = moveTo

    def replace_tiles(self, tileType, Tile):
        for cellIndex in self.cell_locations[tileType]:
            self.cells[cellIndex].replace_tile(Tile)

    def iter_types(self, tileType):
        for cellIndex in self.cell_locations[tileType]:
            yield self.cells[cellIndex].type

    def reset(self):
        for child in self.winfo_children():
            child.destroy()
        self.cells.clear()
        self.cell_locations.clear()


class ItemSlot(object):
    """An object managing the item's quantity and display."""

    def __init__(self, defaultTile, tkParent, Direction):
        self.default_tile = defaultTile
        self.current_type = defaultTile.type
        self.quantity = 1
        # Some items won't be displayed.
        if all((tkParent, Direction, defaultTile)):
            tkImg = tk.Label(tkParent, image=defaultTile.image)
            tkImg.pack(side=Direction)
            self.__game_cell = GameCell(defaultTile, tkImg)
        else:
            self.__game_cell = None;

    def replace(self, Tile):
        self.current_type = Tile.type
        self.quantity = 1
        self.__change_image(Tile.image)

    def remove(self):
        self.current_type = self.default_tile.type
        self.quantity = 1
        self.__reset_image()

    # def add(self, Tile, Times=1):
        # self.quantity += Times
        # self.__change_image(Tile.image)

    # def deduct(self, Times=1):
        # self.quantity -= Times
        # if not self.quantity:
            # self.__reset_image()

    def __change_image(self, Image):
        try:
            self.__game_cell.replace_tile_image(Image)
        except AttributeError:  # Expecting NoneType.
            pass  # Explicitly supressed.

    def __reset_image(self):
        try:
            self.__game_cell.reset_tile_image()
        except AttributeError:  # Expecting NoneType.
            pass  # Explicitly supressed.


class InventorySlots(tk.Frame):
    """An object maintaining groups of ItemSlots."""

    def __init__(self, tkParent, Tiles, Direction, fillTile, Shared):
        tk.Frame.__init__(self, tkParent)
        self.fill_tile, self.direction = fillTile, Direction
        if Shared:
            sharedSlot = ItemSlot(fillTile, self, Direction)
            self.slots = {Tile.type: sharedSlot for Tile in Tiles}
        else:
            self.slots = {Tile.type: ItemSlot(fillTile, self, Direction)
                          for Tile in Tiles}

    def replace(self, Id, Tile):
        self.__get_slot(Id, Tile.type).replace(Tile)

    def remove(self, Id):
        self.slots[Id].remove()

    def quantitiy(self, Id):
        return self.slots[Id].quantity

    def is_carrying(self, Id, current=None):
        itemSlot = self.__get_slot(Id, current)
        return itemSlot.current_type == Id and itemSlot.quantity

    def item(self, Id, current=None):
        return self.__get_slot(Id, current).current_type

    def __get_slot(self, Id, current):
        try:
            Slot = self.slots[Id]
        except KeyError:
            Slot = ItemSlot(self.fill_tile, self, self.direction)
            current = self.fill_tile.type if current is None else current
            Slot.current_type = current
            Slot.quantity = 1
            self.slots[Id] = Slot
        return Slot

    def clear(self):
        self.slots.clear()

class InscribedMessage(tk.Frame):

    def __init__(self, tkParent, Message, Wrap=0):
        tk.Frame.__init__(self, tkParent)
        self.pack()
        tk.Label(self, text=Message, wraplength=Wrap).pack()
        self.bind("<Key>", self.__destroy)
        self.focus_set()

    def __destroy(self, Event):
        self.destroy()
