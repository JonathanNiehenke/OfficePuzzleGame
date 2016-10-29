from collections import defaultdict
import tkinter as tk

import tile_game_engine
import office_levels

db = print

class OfficeGame(object):

    def __init__(self, Parent, playerTileType, Levels):
        self.parent = Parent
        GameTile, imagePath = tile_game_engine.GameTile, 'Images\\{}.png'.format
        # Vim marcro: >>."zyi'f(sGameTile('z', imagePath(f,i)wiself.
        self.tiles = {
            '$': GameTile('$', imagePath('Player'), None),
            '#': GameTile('#', imagePath('Wall'), None),
            ' ': GameTile(' ', imagePath('Empty'), self.move_player),
            'a': GameTile('a', imagePath('Key_a'), self.pickup_item),
            'b': GameTile('b', imagePath('Key_b'), self.pickup_item),
            'c': GameTile('c', imagePath('Key_c'), self.pickup_item),
            'd': GameTile('d', imagePath('Key_d'), self.pickup_item),
            'A': GameTile('A', imagePath('Lock_A'), self.open_cell),
            'B': GameTile('B', imagePath('Lock_B'), self.open_cell),
            'C': GameTile('C', imagePath('Lock_C'), self.open_cell),
            'D': GameTile('D', imagePath('Lock_D'), self.open_cell),
            'e': GameTile('e', imagePath('Source'), self.grab_source),
            'E': GameTile('E', imagePath('Elevator'), self.finish),
            'j': GameTile('j', imagePath('Mop'), self.swap_items),
            'J': GameTile('J', imagePath('WetFloor'), self.open_cell),
            'k': GameTile('k', imagePath('Flashlight'), self.swap_flashlight),
            'K': GameTile('K', imagePath('Empty'), self.enter_darkness),
            'l': GameTile('l', imagePath('LightOff'), self.turn_light_on),
            'L': GameTile('L', imagePath('LightOn'), self.turn_light_off),
            '@': GameTile('@', imagePath('DropZone'), self.swap_items),
            }
        self.fill_tile, self.end_tile = self.tiles[' '], self.tiles['E']
        self.environment = tile_game_engine.NavigationalFrame(
            Parent, self.tiles, playerTileType)
        self.environment.pack()
        self.generated_levels = iter(self.prep_levels(Levels))
        self.level_requirements, self.end_cell = next(self.generated_levels)
        self.inventory = tile_game_engine.InventoryFrame(Parent)
        self.inventory.pack()
        keyTiles = [self.tiles[tileType] for tileType in ('abcd')]
        self.inventory.init_uniquely_displayed_group(
            keyTiles, self.fill_tile)
        handTiles = [self.tiles[tileType] for tileType in ('jk')]
        self.inventory.init_shared_displayed_group(
            handTiles, self.fill_tile)
        self.parent.bind("<Key>", self.environment.handle_input)

    def prep_levels(self, Levels):
        for Title, Structure, *Messages in Levels:
            self.environment.build(Structure)
            Requirements = len(self.environment.cell_locations.get('e', []))
            End = self.environment.cell_locations.get('E', [None])[-1]
            # Prevent defaulting an open end at starting location.
            if not End and Requirements:
                End = self.environment.cell_locations['$'][-1]
            yield Requirements, self.environment.cells[End]

    def move_player(self, moveTo, cellTo):
        self.environment.move_player(moveTo, cellTo)

    def pickup_item(self, moveTo, cellTo):
        self.inventory.include(cellTo.tile)
        cellTo.replace_tile(self.fill_tile)
        self.move_player(moveTo, cellTo)
        
    def open_cell(self, moveTo, cellTo):
        requiredKey = self.tiles[cellTo.type.lower()]
        if self.inventory.is_carrying(requiredKey):
            self.inventory.remove(requiredKey)
            cellTo.replace_tile(self.fill_tile)
            self.move_player(moveTo, cellTo)

    def enter_cell(self, moveTo, cellTo):
        requiredKey = self.tiles[cellTo.type.lower()]
        if self.inventory.is_carrying(requiredKey):
            self.move_player(moveTo, cellTo)

    def enter_darkness(self, moveTo, cellTo):
        acceptableKeys = (self.tiles['k'], self.tiles['l'])
        if any(self.inventory.is_carrying(Key) for Key in acceptableKeys):
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
        self.environment.reset()
        self.level_requirements, self.end_cell = next(self.generated_levels)

    def swap_items(self, moveTo, cellTo):
        pass

    def swap_flashlight(self, moveTo, cellTo):
        pass

    def turn_light_on(self, moveTo, cellTo):
        self.inventory.include(self.tiles['l'])
        cellTo.replace_tile(self.tiles['L'])
        self.level_requirements += 1
        self.update_end_cell()

    def turn_light_off(self, moveTo, cellTo):
        self.inventory.remove(self.tiles['l'])
        cellTo.replace_tile(self.tiles['l'])
        self.level_requirements -= 1
        self.update_end_cell()

def main():
    gameWindow = tk.Tk()
    OfficeGame(gameWindow, '$', office_levels.levels)
    gameWindow.focus_force()
    gameWindow.mainloop()

main()
