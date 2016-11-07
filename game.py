from collections import defaultdict
import tkinter as tk
from tkinter import messagebox

import tile_game_engine
import office_levels

db = print

# Objectives
#   Source: Position, printing.
#   Preceeding: Computer, Power, Password, USB.
#   Return items: Mop, flashlight.
#   Reset state: Light, motion.
# Obstructions
#   Removable: Key locks, wet floor.
#   Togglable: Lights, Motion detectors.
#   Portable: Cart, Plant, Papers, Garbage.
#   Preceeding: Power, Pin, replace bulb, new batteries.
# Reroute
#   Emergency: Bathroom, dying phone battery, get boss call.
#   Other: reminder, correcting mistake.
# Synergistic Mechanics
#   Once way: Flashlight-Darkness-Light, Hands-Narrow.

# Documented improvements
#   add restriction explinations: Darkness, WetFloor, Obstructions, and Plug.
#   light/darkness replacement excludes player.
#   narrow/wall replacement when item enters/released from hand inventory.

class OfficeGame(object):

    def __init__(self, Parent, playerTileType, Levels):
        self.parent = Parent
        GameTile, imagePath = tile_game_engine.GameTile, 'Images\\{}.png'.format
        self.tiles = {
            '$': GameTile('$', imagePath('Player'), None),
            ' ': GameTile(' ', imagePath('Empty'), self.move_player),
            '#': GameTile('#', imagePath('Wall'), None),
            '^': GameTile('^', imagePath('Narrow'), self.through_narrow),
            '@': GameTile('@', imagePath('DropZone'), self.swap_items),
            'a': GameTile('a', imagePath('Key_a'), self.pickup_key),
            'b': GameTile('b', imagePath('Key_b'), self.pickup_key),
            'c': GameTile('c', imagePath('Key_c'), self.pickup_key),
            'd': GameTile('d', imagePath('Key_d'), self.pickup_key),
            'A': GameTile('A', imagePath('Lock_A'), self.open_cell),
            'B': GameTile('B', imagePath('Lock_B'), self.open_cell),
            'C': GameTile('C', imagePath('Lock_C'), self.open_cell),
            'D': GameTile('D', imagePath('Lock_D'), self.open_cell),
            'e': GameTile('e', imagePath('Source'), self.grab_source),
            'E': GameTile('E', imagePath('Elevator'), self.finish),
            'g': GameTile('g', imagePath('Cart'), self.pickup_item),
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
            'G': GameTile('G', imagePath('Plant'), self.pickup_item),
            'Q': GameTile('Q', imagePath('Empty'), self.limit_plug),
            'q': GameTile('q', imagePath('LightPlug'), self.accept_hand_item),
            'S': GameTile('S', imagePath('Socket'), self.plug_in),
            's': GameTile('s', imagePath('PluggedSocket'), self.remove_plug),
            'P': GameTile('P', imagePath('Printer'), self.grab_print),
            'p': GameTile('p', imagePath('Computer'), self.print_source),
            }
        self.fill_tile, self.end_tile = self.tiles[' '], self.tiles['E']
        self.environment = tile_game_engine.NavigationalFrame(
            Parent, self.tiles, playerTileType)
        self.environment.pack()
        self.generated_levels = iter(self.prep_levels(Levels))
        self.level_requirements, self.end_cell = next(self.generated_levels)
        keyTiles = [self.tiles[tileType] for tileType in ("abcd")]
        self.keys = tile_game_engine.InventorySlots(
            Parent, keyTiles, "left", self.fill_tile, Shared=False)
        self.keys.pack(side="left")
        handTiles = [self.tiles[tileType] for tileType in ("jgGHIk@q")]
        self.hands = tile_game_engine.InventorySlots(
            Parent, handTiles, "left", self.tiles['@'], Shared=True)
        self.hands.pack(side="left")
        mapTiles = [self.tiles[tileType] for tileType in ("lk")]
        self.map = tile_game_engine.InventorySlots(
            None, mapTiles, None, self.tiles['@'], Shared=False)
        self.parent.bind("<Key>", self.environment.handle_input)

    def prep_levels(self, Levels):
        for Title, Structure, *Messages in Levels:
            self.environment.build(Structure)
            sourceCount = self.environment.count_tile_types('e')
            printerCount = self.environment.count_tile_types('p')
            Requirements = sourceCount + printerCount
            End = self.environment.cell_locations.get('E', [None])[-1]
            if End is None and Requirements:
                End = self.environment.cell_locations['$'][-1]
            yield Requirements, self.environment.cells[End]

    def move_player(self, moveTo, cellTo):
        self.environment.move_player(moveTo, cellTo)

    def pickup_key(self, moveTo, cellTo):
        Tile = cellTo.tile
        self.keys.replace(Tile.type, Tile)
        cellTo.replace_tile(self.fill_tile)
        self.move_player(moveTo, cellTo)
        
    def open_cell(self, moveTo, cellTo):
        requiredKey = self.tiles[cellTo.type.lower()]
        if self.keys.is_carrying(requiredKey.type):
            self.keys.remove(requiredKey.type)
            cellTo.replace_tile(self.fill_tile)
            self.move_player(moveTo, cellTo)

    def enter_cell(self, moveTo, cellTo):
        if self.hands.is_carrying(cellTo.type.lower()):
            self.move_player(moveTo, cellTo)

    def grab_source(self, moveTo, cellTo):
        cellTo.replace_tile(self.fill_tile)
        self.level_requirements -= 1
        self.update_end_cell()
        self.move_player(moveTo, cellTo)
        # self.message.set('Source information obtained.')

    def update_end_cell(self):
        if self.level_requirements:
            self.end_cell.replace_tile(self.fill_tile)
        else:
            self.end_cell.replace_tile(self.end_tile)

    def finish(self, moveTo, cellTo):
        self.move_player(moveTo, cellTo)
        self.map.clear()
        self.environment.reset()
        try:
            self.level_requirements, self.end_cell = next(self.generated_levels)
        except StopIteration:
            tk.messagebox.showinfo("Complete", "You finished?")
            self.parent.destroy()

    def swap_items(self, moveTo, cellTo):
        handItem = self.hands.item(cellTo.tile.type)
        dropItem = self.map.item(moveTo, cellTo.tile.type)
        tempDropItem = '@' if dropItem == ' ' else dropItem
        tempHandItem = '@' if handItem == ' ' else handItem
        self.hands.replace(handItem, self.tiles[tempDropItem])
        self.map.replace(moveTo, self.tiles[tempHandItem])
        cellTo.replace_tile_image(self.tiles[tempHandItem].image)
        # Level requirements +1 while holding a handItem.
        if (tempHandItem != '@'):  # Returning Item
            self.level_requirements -= 1
        if (tempDropItem != '@'):  # Accepting Item
            self.level_requirements += 1
        self.update_end_cell()

    def pickup_item(self, moveTo, cellTo):
        if self.hands.is_carrying('@'):
            Tile = cellTo.tile
            self.hands.replace(Tile.type, Tile)
            cellTo.replace_tile(self.fill_tile)
            self.move_player(moveTo, cellTo)
            self.level_requirements += 1;
            self.update_end_cell()

    def drop_item(self, moveTo, cellTo):
        item = cellTo.type.upper()
        if self.hands.is_carrying(item):
            self.hands.remove(item)
            self.level_requirements -= 1
            self.update_end_cell()

    def through_narrow(self, moveTo, cellTo):
        if self.hands.is_carrying('@'):
            self.move_player(moveTo, cellTo)
        # else:
            # self.explain(cellType)

    def remove_slip(self, moveTo, cellTo):
        requiredKey = self.tiles[cellTo.type.lower()]
        if self.hands.is_carrying(requiredKey.type):
            cellTo.replace_tile(self.fill_tile)
            self.move_player(moveTo, cellTo)

    def limit_plug(self, moveTo, cellTo):
        if not self.hands.is_carrying('q'):
            self.move_player(moveTo, cellTo)

    def accept_hand_item(self, moveTo, cellTo):
        if self.hands.is_carrying('@'):
            Tile = cellTo.tile
            self.hands.replace(Tile.type, Tile)
            self.level_requirements += 1
        elif self.hands.is_carrying(cellTo.type):
            self.hands.remove(cellTo.type)
            self.level_requirements -= 1
        self.update_end_cell()

    def plug_in(self, moveTo, cellTo):
        if self.hands.is_carrying('q'):
            self.hands.remove('q')
            self.map.replace(moveTo, self.tiles['q'])
            cellTo.replace_tile(self.tiles['s'])
            lightOff = self.tiles['l'];
            for cellIndex in self.environment.cell_locations['q']:
                self.environment.cells[cellIndex].replace_tile(lightOff)
            self.level_requirements -= 1
            self.update_end_cell()

    def remove_plug(self, moveTo, cellTo):
        # ? Prevent unpluging of on light.
        Plug = self.map.item(moveTo)
        lightOn = {'q': 'L'}[Plug]
        Unpowered = all(cellTypes != lightOn
                        for cellTypes in self.environment.iter_types('q'))
        if self.hands.is_carrying('@') and Unpowered:
            plugTile = self.tiles[Plug]
            self.hands.replace(Plug, plugTile)
            self.map.remove(moveTo)
            cellTo.replace_tile(self.tiles['S'])
            self.environment.replace_tiles(Plug, plugTile)
            self.level_requirements += 1
            self.update_end_cell()

    def grab_print(self, moveTo, cellTo):
        if self.map.is_carrying('p'):
            self.map.remove('p')
            cellTo.replace_tile(self.tiles['#'])
            self.level_requirements -= 1
            self.update_end_cell()
            # self.message.set('Source information obtained.')

    def print_source(self, moveTo, cellTo):
        self.map.replace(cellTo.type, cellTo.tile)
        cellTo.replace_tile(self.tiles['#'])

    def turn_light_on(self, moveTo, cellTo):
        cellTo.replace_tile(self.tiles['L'])
        self.environment.replace_tiles('K', self.fill_tile,)
        self.level_requirements += 1
        self.update_end_cell()

    def turn_light_off(self, moveTo, cellTo):
        cellTo.replace_tile(self.tiles['l'])
        self.environment.replace_tiles('K', self.tiles['K'])
        self.level_requirements -= 1
        self.update_end_cell()

def main():
    gameWindow = tk.Tk()
    OfficeGame(gameWindow, '$', office_levels.levels)
    gameWindow.focus_force()
    gameWindow.mainloop()

main()
