from collections import defaultdict
from random import randint
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
        self.parent.protocol('WM_DELETE_WINDOW', self.__handle_key)
        self.quiting = False;
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
            'f': GameTile('f', imagePath('LockNumber'), self.display_pin),
            'F': GameTile('F', imagePath('PinLock'), self.enter_lock_pin),
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
            'm': GameTile('m', imagePath('MotionOn'), self.motion_toggle),
            'M': GameTile('M', imagePath('MotionOff'), self.motion_toggle),
            'n': GameTile('n', imagePath('MotionNumber'), self.display_pin),
            'N': GameTile('N', imagePath('Signal'), None),
            'q': GameTile('q', imagePath('LightPlug'), self.swap_plug),
            'Q': GameTile('Q', imagePath('Empty'), self.limit_plug),
            'r': GameTile('r', imagePath('Computer'), self.print_source),
            'R': GameTile('R', imagePath('ComputerPlug'), self.swap_plug),
            's': GameTile('s', imagePath('Socket'), self.plug_in),
            'S': GameTile('S', imagePath('PluggedSocket'), self.remove_plug),
            'p': GameTile('p', imagePath('PrinterX'), None),
            'P': GameTile('P', imagePath('Printer'), self.grab_print),
            '0': GameTile('0', imagePath('DD0'), None),
            '1': GameTile('1', imagePath('DD1'), None),
            '2': GameTile('2', imagePath('DD2'), None),
            '3': GameTile('3', imagePath('DD3'), None),
            '4': GameTile('4', imagePath('DD4'), None),
            '5': GameTile('5', imagePath('DD5'), None),
            '6': GameTile('6', imagePath('DD6'), None),
            '7': GameTile('7', imagePath('DD7'), None),
            '8': GameTile('8', imagePath('DD8'), None),
            '9': GameTile('9', imagePath('DD9'), None),
        }
        self.fill_tile, self.end_tile = self.tiles[' '], self.tiles['E']
        self.keys, self.hands, self.map = self.__build_inventories()
        self.environment = tile_game_engine.NavigationalFrame(
            self.game_frame, self.tiles, playerTileType='$')
        self.generated_levels = iter(self.__prep_levels(levelFilename))
        self.structure, self.level_requirements, self.end_cell = next(
            self.generated_levels)
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
        Map = {}
        return Keys, Hands, Map

    def __file_parser(self, fileName):
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
            tile_game_engine.InscribedFrame(self.parent).show_msg(Info, 250)
        self.game_frame.pack()

    def __build_level(self, Structure):
        self.environment.build(Structure)
        End = self.environment.cell_locations.get('E', [None])[-1]
        Requirements = self.environment.count_tile_types('e')
        Requirements += self.environment.count_tile_types('p')
        Requirements += self.environment.count_tile_types('P')
        if End is None and Requirements:
            End = self.environment.cell_locations['$'][-1]
        return Structure, Requirements, self.environment.cells[End]

    def __prep_levels(self, levelFilename):
        """Load level, their messages and their requirements."""
        for Messages, Structure in self.__file_parser(levelFilename):
            self.__display_messages(Messages)
            yield self.__build_level(Structure)

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

    def __handle_key(self, Event=None):
        """Handles keyboard input to quit or move in direction."""
        try:
            keyPressed = Event.keysym
        except AttributeError:
            keyPressed = "Escape"
        if keyPressed == "Escape" and not self.quiting:
            self.quiting = True;
            self.game_frame.pack_forget()
            Buttons = ("Reset Level", "Quit Game", "Cancel")
            Idx = tile_game_engine.InscribedFrame(self.parent).button_prompt(
                "You want too?", Buttons, Wrap=250)
            {0: self.__reset_level,
             1: self.parent.destroy,
             2: self.game_frame.pack}[Idx]()
            self.quiting = False;
        else:
             self.environment.handle_key(keyPressed)

    def __reset_level(self):
        self.environment.reset()
        self.keys.empty()
        self.hands.empty()
        self.map.clear()
        self.structure, self.level_requirements, self.end_cell = (
            self.__build_level(self.structure))
        self.game_frame.pack()

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
            self.structure, self.level_requirements, self.end_cell = next(
                self.generated_levels)
        except StopIteration:
            self.game_frame.pack_forget()
            tile_game_engine.InscribedFrame(self.parent).show_msg(
                "You finished! Hooray!")
            self.parent.destroy()

    def swap_objects(self, moveTo, cellTo):
        """Swaps, drops or accepts objects and other adjustments."""
        fromHand = self.hands.item(cellTo.tile.type)
        if fromHand not in "qRr": # Do not swap plug types.
            tileFromHand = self.tiles[fromHand]
            fromDrop = self.map.get(moveTo, cellTo.tile.type)
            self.hands.replace(fromHand, self.tiles[fromDrop])
            self.map[moveTo] = tileFromHand.type
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
            self.map[moveTo] = Plug
            cellTo.replace_tile(self.tiles['S'])
            Off = self.tiles[{'q': 'l', 'R': 'r'}[Plug]]
            self.environment.replace_tiles(Plug, Off)

    def remove_plug(self, moveTo, cellTo):
        """Accepts plug type and adjusts environment."""
        Plug = self.map.get(moveTo, '@')
        On = {'q': 'L', 'r': 'p', 'R': 'P'}[Plug]
        Unpowered = all(
            cellTypes != On for cellTypes in self.environment.iter_types(Plug))
        if self.hands.is_carrying('@') and Unpowered:
            plugTile = self.tiles[Plug]
            self.__accept_object(Plug, plugTile)
            self.map[moveTo] = '@'
            cellTo.replace_tile(self.tiles['s'])
            self.environment.replace_tiles(Plug, plugTile)

    def print_source(self, moveTo, cellTo):
        """Replaces all PrinterX tiles to Printer."""
        self.environment.replace_tiles('p', self.tiles['P'], isOriginal=True)

    def grab_print(self, moveTo, cellTo):
        """Reduces a requirement and cellTo tile is replace by wall."""
        cellTo.replace_tile(self.tiles['#'])
        self.__change_requirements(-1)
        # self.message.set('Source information obtained.')

    def __generate_pin(self, moveTo, cellType):
        pinNumber = self.map.get(moveTo)
        if (not pinNumber):
            pinNumber = str(randint(100000, 999999))
            applyTo = [pair for pair in ("fF", "mn") if cellType in pair][0]
            for cellIdx in self.environment.iter_locations(applyTo):
                self.map[cellIdx] = pinNumber
        return pinNumber

    def __input_pin(self):
        self.game_frame.pack_forget()
        userPin = tile_game_engine.InscribedFrame(self.parent).text_prompt(
            "Enter the required pin number.", 6)
        self.game_frame.pack()
        return userPin.strip()

    def display_pin(self, moveTo, cellTo):
        pinNumber = self.__generate_pin(moveTo, cellTo.type)
        self.game_frame.pack_forget()
        tile_game_engine.InscribedFrame(self.parent).show_msg(
            'Pin Number: {}.'.format(pinNumber))
        self.game_frame.pack()

    def enter_lock_pin(self, moveTo, cellTo):
        userPin = self.__input_pin()
        if (userPin == self.__generate_pin(moveTo, cellTo.type)):
            self.move_player(moveTo, cellTo)
        else:
            self.game_frame.pack_forget()
            tile_game_engine.InscribedFrame(self.parent).show_msg(
                "#{}: Failed to unlock".format(userPin))
            self.game_frame.pack()

    def motion_toggle(self, moveTo, cellTo):
        userPin = self.__input_pin()
        if (userPin == self.__generate_pin(moveTo, cellTo.type)):
            # Delaying change to environment after redisplaying.
            self.environment.after(750, self.toggle, moveTo, cellTo)
        else:
            self.game_frame.pack_forget()
            tile_game_engine.InscribedFrame(self.parent).show_msg(
                "#{}: Failed to deactivate".format(userPin))
            self.game_frame.pack()

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
