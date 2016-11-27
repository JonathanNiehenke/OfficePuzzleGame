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
#   obscure printer till activating computer.
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
        self.parent.bind("<Key>", self.__handle_key)
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
            '@': GameTile('@', imagePath('DropZone'), self.swap_objects),
            'a': GameTile('a', imagePath('RedKey'), self.pickup_key),
            'b': GameTile('b', imagePath('BlueKey'), self.pickup_key),
            'c': GameTile('c', imagePath('GreenKey'), self.pickup_key),
            'd': GameTile('d', imagePath('YellowKey'), self.pickup_key),
            'A': GameTile('A', imagePath('RedLock'), self.open_key_lock),
            'B': GameTile('B', imagePath('BlueLock'), self.open_key_lock),
            'C': GameTile('C', imagePath('GreenLock'), self.open_key_lock),
            'D': GameTile('D', imagePath('YellowLock'), self.open_key_lock),
            'e': GameTile('e', imagePath('Source'), self.grab_source),
            'E': GameTile('E', imagePath('Elevator'), self.finish),
            'g': GameTile('g', imagePath('Cart'), self.pickup_object),
            'G': GameTile('G', imagePath('Plant'), self.pickup_object),
            'h': GameTile('h', imagePath('Papers'), self.pickup_object),
            'H': GameTile('H', imagePath('Desk'), self.drop_object),
            'i': GameTile('i', imagePath('Trash'), self.pickup_object),
            'I': GameTile('I', imagePath('TrashCan'), self.drop_object),
            'j': GameTile('j', imagePath('Mop'), self.swap_objects),
            'J': GameTile('J', imagePath('WetFloor'), self.open_lock),
            'k': GameTile('k', imagePath('Flashlight'), self.swap_objects),
            'K': GameTile('K', imagePath('Darkness'), self.enter_cell),
            'l': GameTile('l', imagePath('LightOff'), self.toggle),
            'L': GameTile('L', imagePath('LightOn'), self.toggle),
            'm': GameTile('m', imagePath('MotionOn'), self.toggle),
            'M': GameTile('M', imagePath('MotionOff'), self.toggle),
            'N': GameTile('N', imagePath('Signal'), None),
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

    def __build_inventories(self):
        """Builds the key, hands and map inventory groups."""
        keyTiles = [self.tiles[tileType] for tileType in ("abcd")]
        Keys = tile_game_engine.InventorySlots(
            self.game_frame, keyTiles, "left", self.fill_tile, Shared=False)
        handTiles = [self.tiles[tileType] for tileType in ("@jgGhikqrR")]
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
                if Begins == '\n' and Level:
                    yield Messages, Level
                    Messages.clear()
                    Level.clear()
                elif Begins == '"':
                    Messages.append(Line.strip())
                elif Begins == '\\' or Begins == '\n':
                    continue
                else:
                    Level.append(Line.strip())  # removes newline.
            if Level:  # In-case no empty line at EOF.
                yield Messages, Level

    def __display_messages(self, Messages):
        """Set level title and display pre-level messages."""
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

    def open_cell(self, moveTo, cellTo):
        """Replaces cellTo so it is walkable and move player."""
        cellTo.replace_tile(self.fill_tile)
        self.move_player(moveTo, cellTo)

    def enter_cell(self, moveTo, cellTo):
        """Move player if carrying the required key."""
        if self.hands.is_carrying(cellTo.type.lower()):
            self.move_player(moveTo, cellTo)

    def pickup_key(self, moveTo, cellTo):
        """Accept key and opens cell if not already carrying it."""
        if not self.keys.is_carrying(cellTo.type):
            cellToTile = cellTo.tile
            self.keys.replace(cellToTile.type, cellToTile)
            self.open_cell(moveTo, cellTo)

    def open_key_lock(self, moveTo, cellTo):
        """Opens cell and removes key if carrying the required key."""
        requiredKey = cellTo.type.lower()
        if self.keys.is_carrying(requiredKey):
            self.keys.remove(requiredKey)
            self.open_cell(moveTo, cellTo)

    def pickup_object(self, moveTo, cellTo):
        """Accept object and opens cell if carrying nothing."""
        if self.hands.is_carrying('@'):
            cellToTile = cellTo.tile
            self.__accept_object(cellToTile.type, cellToTile)
            self.open_cell(moveTo, cellTo)

    def open_lock(self, moveTo, cellTo):
        """Opens cell if carrying the required key."""
        if self.hands.is_carrying(cellTo.type.lower()):
            self.open_cell(moveTo, cellTo)

    def grab_source(self, moveTo, cellTo):
        """Replaces cell, moves player and adjusts the environment."""
        self.open_cell(moveTo, cellTo)
        self.__change_requirements(-1)

    def finish(self, moveTo, cellTo):
        """Loads the next level or congratulates then closes."""
        self.environment.reset()
        self.map.clear()
        try:
            self.level_requirements, self.end_cell = next(
                self.generated_levels)
        except StopIteration:
            tk.messagebox.showinfo("Complete", "You finished!")
            self.parent.destroy()

    def swap_objects(self, moveTo, cellTo):
        """Swaps, drops or accepts objects and other adjustments."""
        fromHand = self.hands.item(cellTo.tile.type)
        tileFromHand = self.tiles[fromHand]
        fromDrop = self.map.item(moveTo, cellTo.tile.type)
        self.hands.replace(fromHand, self.tiles[fromDrop])
        self.map.replace(moveTo, tileFromHand)
        cellTo.replace_tile_image(tileFromHand.image)
        # Level requirements +1 while holding a fromHand.
        if (fromHand != '@'):  # Returning Item
            self.__change_requirements(-1)
            self.environment.replace_tiles(':', self.tiles[':'])
        if (fromDrop != '@'):  # Accepting Item
            self.__change_requirements(1)
            self.environment.replace_tiles(':', self.tiles[';'])

    def drop_object(self, moveTo, cellTo):
        """Remove object from hands if carrying the intended object."""
        item = cellTo.type.lower()
        if self.hands.is_carrying(item):
            self.__drop_object(item)

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
            self.environment.replace_tiles(Plug, Off)

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

    def toggle(self, moveTo, cellTo):
        """Turns light on and adjusts environment and requirements."""
        Replacements = {
            'l': ('K', self.fill_tile), 'L': ('K', self.tiles['K']),
            'm': ('N', self.fill_tile), 'M': ('N', self.tiles['N'])
        }
        cellType = cellTo.type
        cellTo.replace_tile(self.tiles[cellType.swapcase()])
        currentType, replacementTile = Replacements[cellType]
        self.environment.replace_tiles(currentType, replacementTile)
        if cellType.islower():
            self.__change_requirements(1)
        else:
            self.__change_requirements(-1)

def main():
    gameWindow = tk.Tk()
    OfficeGame(gameWindow, "office_levels.txt")
    gameWindow.focus_set()
    gameWindow.mainloop()

if __name__ == "__main__":
    main()
