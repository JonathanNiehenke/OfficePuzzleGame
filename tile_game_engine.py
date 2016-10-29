from collections import defaultdict, namedtuple
from itertools import chain, cycle

import tkinter as tk
from tkinter import messagebox


class GameTile(object):
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
        return '<GameTile: {}>'.format(self.type)


class GameCell(object):
    """
    An object joinng a GameTile object and a tk.Label of an image. Used
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
        return GameCell(Tile, tkImg)

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


class InventoryItem(object):

    def __init__(self, Count, Share, tkImage, fillTile):
        self.count, self.share, self.fill_tile = Count, Share, fillTile
        # A inventory item may not need to be displayed.
        self._cell = (GameCell(fillTile, tkImage)
                      if fillTile is not None or tkImage is not None else None)

    def add(self, Tile, Times=1):
        self.count += Times
        self.__change_image(Tile.image)

    def deduct(self, Times=1):
        self.count -= Times
        if not self.count:
            self.__change_image(self.fill_tile.image)

    def __change_image(self, Image):
        try:
            self.__cell.replace_tile_image(Image)
        except AttributeError:  # Expecting NoneType.
            pass  # Explicitly supressed.


class InventoryFrame(tk.Frame):

    def __init__(self, Parent, Arranged='Vertically', *args, **kwargs):
        tk.Frame.__init__(self, Parent, *args, **kwargs)
        self.parent, self.itemInventory = Parent, {}
        self.group_pack = ('left' if Arranged == 'Horizontally' else 'top')

    def init_uniquely_displayed_group(self, Tiles, fillTile,
                                      Arranged="Horizontally"):
        groupFrame = tk.Frame(self)
        groupFrame.pack(side=self.group_pack)
        Share = []
        for Tile in Tiles:
            tkImage = tk.Label(groupFrame, image=fillTile.image)
            tkImage.pack(side=('top' if Arranged == 'Vertically' else 'left'))
            self.itemInventory[Tile.type]  = InventoryItem(
                0, Share, tkImage, fillTile)

    def init_shared_displayed_group(self, Tiles, fillTile):
        Share = [Tile.type for Tile in Tiles]
        tkImage = tk.Label(self, image=fillTile.image)
        tkImage.pack(side=self.group_pack)
        for Tile in Tiles:
            self.itemInventory[Tile.type]  = InventoryItem(
                0, Share, tkImage, fillTile)

    def include(self, Tile):
        inventoryItem = self.itemInventory.setdefault(
            Tile.type, InventoryItem(0, [], None, None))
        if not any(self.itemInventory[shareItem].count
                   for shareItem in inventoryItem.share):
            inventoryItem.add(Tile)

    def remove(self, Tile):
        try:  # To accept Tile or Tile.type
            tileType = Tile.type
        except AttributeError:
            tileType = Tile
        self.itemInventory[tileType].deduct()

    def is_carrying(self, Tile):
        inventoryItem = self.itemInventory.setdefault(
            Tile.type, InventoryItem(0, [], None, None))
        return inventoryItem.count

    # def get_shared_item(self, Tile):
        # for sharedItem in self.itemInventory[Tile.type].share:
            # if self.itemInventory[sharedItem].count
                # return 

    # def swap_shared_item(self, Tile):
        # for sharedItem in self.itemInventory[Tile.type].share:
            # sharedInventoryItem = self.itemInventory[sharedItem]
            # if sharedInventoryItem.count
                # self.remove(sharedItem)
                # self.include(Tile)
                # return shareInventoryItem.fillTile
        # else:
            # self.include(Tile)
            # return defaultItem

    def reset(self):
        for inventoryItem in itemInventory.values():
            if itemInventory.count:
                inventoryItem.count = 0
                inventoryItem.tkImage.configure(image=inventoryItem.fillImage)
