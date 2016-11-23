from collections import defaultdict
import tkinter as tk
from tkinter import messagebox

import tile_game_engine

db = print

# Objectives
#   Source: Position, printing.
#   Preceding: Computer, Power, Password, USB.
#   Return items: Mop, flashlight.
#   Reset state: Light, motion.
# Obstructions
#   Removable: Key locks, wet floor.
#   Togglable: Lights, Motion detectors.
#   Portable: Cart, Plant, Papers, Garbage.
#   Preceding: Power, Pin, replace bulb, new batteries, soap and water.
# Reroute
#   Emergency: Bathroom, dying phone battery, get boss call, wifi crash,
#       improper temperature.
#   Other: reminder, correcting mistake, replace air filter (Allergies).
# Synergistic Mechanics
#   Once way: Flashlight-Darkness-Light, Hands-Narrow.
# Resource:
#   Coffee/Hunger bar.

# Documented improvements
#   light/darkness replacement excludes player.
#   better indicate computer before printer.
#   better indicate changes/restrictions when holding objects.
#   ? add restriction explanations: Darkness, WetFloor, and Plug.

class OfficeGame(object):
    """
    An office themed tile puzzle game, where dark hallways, slippery
    floors and objects prevent you from finishing your job.
    """

    def __init__(self, Parent, levelFilename):
        self.parent = Parent
        self.parent.title("Office Game")
        self.parent.minsize(252, 258)
        self.level_title = tk.StringVar()
        tk.Label(self.parent, textvar=self.level_title).pack()
        self.game_frame = tk.Frame(Parent)
        GameTile = tile_game_engine.GameTile
        imagePath = 'Images\\{}.png'.format
        self.tiles = {
            '$': GameTile('$', imagePath('Player'), None),
            ' ': GameTile(' ', imagePath('Empty'), self.move_player),
            '#': GameTile('#', imagePath('Wall'), None),
            ':': GameTile(':', imagePath('OpenNarrow'), self.move_player),
            ';': GameTile(';', imagePath('ClosedNarrow'), None),
            '@': GameTile('@', imagePath('DropZone'), self.swap_items),
            'a': GameTile('a', imagePath('RedKey'), self.pickup_key),
            'b': GameTile('b', imagePath('BlueKey'), self.pickup_key),
            'c': GameTile('c', imagePath('GreenKey'), self.pickup_key),
            'd': GameTile('d', imagePath('YellowKey'), self.pickup_key),
            'A': GameTile('A', imagePath('RedLock'), self.open_cell),
            'B': GameTile('B', imagePath('BlueLock'), self.open_cell),
            'C': GameTile('C', imagePath('GreenLock'), self.open_cell),
            'D': GameTile('D', imagePath('YellowLock'), self.open_cell),
            'e': GameTile('e', imagePath('Source'), self.grab_source),
            'E': GameTile('E', imagePath('Elevator'), self.finish),
            'g': GameTile('g', imagePath('Cart'), self.pickup_item),
            'G': GameTile('G', imagePath('Plant'), self.pickup_item),
            'h': GameTile('h', imagePath('Desk'), self.drop_item),
            'H': GameTile('H', imagePath('Papers'), self.pickup_item),
            'i': GameTile('i', imagePath('TrashCan'), self.drop_item),
            'I': GameTile('I', imagePath('Trash'), self.pickup_item),
            'j': GameTile('j', imagePath('Mop'), self.swap_items),
            'J': GameTile('J', imagePath('WetFloor'), self.remove_slip),
            'k': GameTile('k', imagePath('Flashlight'), self.swap_items),
            'K': GameTile('K', imagePath('Darkness'), self.enter_cell),
            'l': GameTile('l', imagePath('LightOff'), self.turn_light_on),
            'L': GameTile('L', imagePath('LightOn'), self.turn_light_off),
            'q': GameTile('q', imagePath('LightPlug'), self.swap_plug),
            'Q': GameTile('Q', imagePath('Empty'), self.limit_plug),
            'r': GameTile('r', imagePath('ComputerPlug'), self.swap_plug),
            'R': GameTile('R', imagePath('PrinterPlug'), self.swap_plug),
            's': GameTile('s', imagePath('Socket'), self.plug_in),
            'S': GameTile('S', imagePath('PluggedSocket'), self.remove_plug),
            'p': GameTile('p', imagePath('Computer'), self.print_source),
            'P': GameTile('P', imagePath('Printer'), self.grab_print),
        }
        self.fill_tile, self.end_tile = self.tiles[' '], self.tiles['E']
        self.keys, self.hands, self.map = self.__build_inventories()
        self.environment = tile_game_engine.NavigationalFrame(
            self.game_frame, self.tiles, playerTileType='$')
        self.generated_levels = iter(self.__prep_levels(levelFilename))
        self.level_requirements, self.end_cell = next(self.generated_levels)
        self.environment.grid(row=0, column=0, columnspan=2)
        tk.Label(self.game_frame, text="Keys").grid(row=1, column=0)
        tk.Label(self.game_frame, text="Object").grid(row=1, column=1)
        self.keys.grid(row=2, column=0)
        self.hands.grid(row=2, column=1)
        self.game_frame.pack()
        self.parent.bind("<Key>", self.__handle_key)

    def __build_inventories(self):
        """Builds the key, hands and map inventory groups."""
        keyTiles = [self.tiles[tileType] for tileType in ("abcd")]
        Keys = tile_game_engine.InventorySlots(
            self.game_frame, keyTiles, "left", self.fill_tile, Shared=False)
        handTiles = [self.tiles[tileType] for tileType in ("@jgGHIkqrR")]
        Hands = tile_game_engine.InventorySlots(
            self.game_frame, handTiles, "left", self.tiles['@'], Shared=True)
        Map = tile_game_engine.InventorySlots(
            None, [], None, self.tiles['@'], Shared=False)
        return Keys, Hands, Map

    def __fileParser(self, fileName):
        """Iterable of parsed levels from fileName."""
        with open(fileName, "r") as File:
            Messages, Level = [], []
            for Line in File:
                Begins = Line[0]  # Empty lines contain a newline.
                if Begins == '"':
                    Messages.append(Line.strip())
                elif Begins == '\n' and Level:
                    yield Messages, Level
                    Messages.clear()
                    Level.clear()
                elif Begins == '\\' or Begins == '\n':
                    continue
                else:
                    Level.append(Line.strip())  # removes newline.

    def __display_messages(self, Messages):
        """Display pre-level messages in the place of game_frame."""
        Title, *Information = Messages
        self.level_title.set(Title)
        self.game_frame.pack_forget()
        for Info in Information:
            Temp = tile_game_engine.InscribedMessage(self.parent, Info, 250)
            self.parent.wait_window(Temp)
        self.game_frame.pack()

    def __prep_levels(self, levelFilename):
        """Load level, their messages and their requirements."""
        for Messages, Structure in self.__fileParser(levelFilename):
            self.__display_messages(Messages)
            self.environment.build(Structure)
            End = self.environment.cell_locations.get('E', [None])[-1]
            sourceCount = self.environment.count_tile_types('e')
            printerCount = self.environment.count_tile_types('p')
            uPrinterCount = self.environment.count_tile_types('R')
            Requirements = sourceCount + printerCount + uPrinterCount
            if End is None and Requirements:
                End = self.environment.cell_locations['$'][-1]
            yield Requirements, self.environment.cells[End]

    def __change_requirements(self, value):
        """Change requirements and reveal or hide the elevator."""
        self.level_requirements += value
        if self.level_requirements:
            self.end_cell.replace_tile(self.fill_tile)
        else:
            self.end_cell.replace_tile(self.end_tile)

    def __accept_object(self, tileType, Tile):
        """Replaces the inventory and adjusts the environment."""
        self.hands.replace(Tile.type, Tile)
        self.__change_requirements(1)
        self.environment.replace_tiles(':', self.tiles[';'])

    def __drop_object(self, tileType):
        """Removes the inventory and adjusts the environment."""
        self.hands.remove(tileType)
        self.__change_requirements(-1)
        self.environment.replace_tiles(':', self.tiles[':'])

    def __handle_key(self, Event):
        """Handles keyboard input to quit or move in direction."""
        keyPressed = Event.keysym
        if (keyPressed == "Escape" and
                messagebox.askyesno("Quit?", "You want to quit?")):
            self.parent.destroy()
        else:
             self.environment.handle_key(keyPressed)

    def move_player(self, moveTo, cellTo):
        self.environment.move_player(moveTo, cellTo)

    def pickup_key(self, moveTo, cellTo):
        """Replaces cell to Empty and place key in inventory."""
        Tile = cellTo.tile
        self.keys.replace(Tile.type, Tile)
        cellTo.replace_tile(self.fill_tile)
        self.move_player(moveTo, cellTo)

    def open_cell(self, moveTo, cellTo):
        """Replaces cell and inventory if carrying the required key."""
        requiredKey = self.tiles[cellTo.type.lower()]
        if self.keys.is_carrying(requiredKey.type):
            self.keys.remove(requiredKey.type)
            cellTo.replace_tile(self.fill_tile)
            self.move_player(moveTo, cellTo)

    def enter_cell(self, moveTo, cellTo):
        """Move player if carrying the required key."""
        if self.hands.is_carrying(cellTo.type.lower()):
            self.move_player(moveTo, cellTo)

    def grab_source(self, moveTo, cellTo):
        """Replaces cell, moves player and adjusts the environment."""
        cellTo.replace_tile(self.fill_tile)
        self.__change_requirements(-1)
        self.move_player(moveTo, cellTo)
        # self.message.set('Source information obtained.')

    def finish(self, moveTo, cellTo):
        """Loads the next level or congratulates then closes."""
        self.move_player(moveTo, cellTo)
        self.map.clear()
        self.environment.reset()
        try:
            self.level_requirements, self.end_cell = next(
                self.generated_levels)
        except StopIteration:
            tk.messagebox.showinfo("Complete", "You finished!")
            self.parent.destroy()

    def swap_items(self, moveTo, cellTo):
        """Swaps, drops or accepts objects and other adjustments."""
        handItem = self.hands.item(cellTo.tile.type)
        dropItem = self.map.item(moveTo, cellTo.tile.type)
        self.hands.replace(handItem, self.tiles[dropItem])
        self.map.replace(moveTo, self.tiles[handItem])
        cellTo.replace_tile_image(self.tiles[handItem].image)
        # Level requirements +1 while holding a handItem.
        if (handItem != '@'):  # Returning Item
            self.__change_requirements(-1)
            self.environment.replace_tiles(':', self.tiles[':'])
        if (dropItem != '@'):  # Accepting Item
            self.__change_requirements(1)
            self.environment.replace_tiles(':', self.tiles[';'])

    def pickup_item(self, moveTo, cellTo):
        """Replaces cell and moves player if hands have nothing."""
        if self.hands.is_carrying('@'):
            Tile = cellTo.tile
            self.__accept_object(Tile.type, Tile)
            cellTo.replace_tile(self.fill_tile)
            self.move_player(moveTo, cellTo)

    def drop_item(self, moveTo, cellTo):
        """Remove object from hands if carrying the intended object."""
        item = cellTo.type.upper()
        if self.hands.is_carrying(item):
            self.__drop_object(item)

    def remove_slip(self, moveTo, cellTo):
        """Replaces and moves player if carrying the required key."""
        requiredKey = self.tiles[cellTo.type.lower()]
        if self.hands.is_carrying(requiredKey.type):
            cellTo.replace_tile(self.fill_tile)
            self.move_player(moveTo, cellTo)

    def limit_plug(self, moveTo, cellTo):
        """Moves player if not carrying a plug."""
        if not self.hands.item('@') in "qRr":
            self.move_player(moveTo, cellTo)

    def swap_plug(self, moveTo, cellTo):
        """Accepts or drops plug type."""
        if self.hands.is_carrying('@'):
            Tile = cellTo.tile
            self.__accept_object(Tile.type, Tile)
        elif self.hands.is_carrying(cellTo.type):
            self.__drop_object(cellTo.type)

    def plug_in(self, moveTo, cellTo):
        """Drops plug type and adjusts the environment."""
        Plug = self.hands.item('@')
        if Plug in "qRr":
            self.__drop_object(Plug)
            self.map.replace(moveTo, self.tiles[Plug])
            cellTo.replace_tile(self.tiles['S'])
            Off = self.tiles[{'q': 'l', 'r': 'p', 'R': 'P'}[Plug]]
            for cellIndex in self.environment.cell_locations[Plug]:
                self.environment.cells[cellIndex].replace_tile(Off)

    def remove_plug(self, moveTo, cellTo):
        """Accepts plug type and adjusts environment."""
        Plug = self.map.item(moveTo)
        On = {'q': 'L', 'r': 'p', 'R': 'P'}[Plug]
        Unpowered = all(
            cellTypes != On for cellTypes in self.environment.iter_types(Plug))
        if self.hands.is_carrying('@') and Unpowered:
            plugTile = self.tiles[Plug]
            self.__accept_object(Plug, plugTile)
            self.map.remove(moveTo)
            cellTo.replace_tile(self.tiles['s'])
            self.environment.replace_tiles(Plug, plugTile)

    def print_source(self, moveTo, cellTo):
        """Replaces cell and adds print to map inventory."""
        self.map.replace(cellTo.type, cellTo.tile)
        cellTo.replace_tile(self.tiles['#'])

    def grab_print(self, moveTo, cellTo):
        """Replaces and changes requirements if map carries print."""
        if self.map.is_carrying('p'):
            self.map.remove('p')
            cellTo.replace_tile(self.tiles['#'])
            self.__change_requirements(-1)
            # self.message.set('Source information obtained.')

    def turn_light_on(self, moveTo, cellTo):
        """Turns light on and adjusts environment and requirements."""
        cellTo.replace_tile(self.tiles['L'])
        self.environment.replace_tiles('K', self.fill_tile,)
        self.__change_requirements(1)

    def turn_light_off(self, moveTo, cellTo):
        """Turns light off and adjusts environment and requirements."""
        cellTo.replace_tile(self.tiles['l'])
        self.environment.replace_tiles('K', self.tiles['K'])
        self.__change_requirements(-1)

gameWindow = tk.Tk()
OfficeGame(gameWindow, "office_levels.txt")
gameWindow.focus_set()
gameWindow.mainloop()
