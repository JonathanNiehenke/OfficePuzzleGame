from collections import defaultdict
import tkinter as tk

import tile_game_engine
import office_levels

db = print

class OfficeGame(object):

    def __init__(self, Parent, playerTileType, Levels):
        self.parent = Parent
        MapTile, imagePath = tile_game_engine.MapTile, 'Images\\{}.png'.format
        # Vim marcro: >>."zyi'f(sMapTile('z', imagePath(f,i)wiself.
        self.tiles = {
            '$': MapTile('$', imagePath('Player'), None),
            '#': MapTile('#', imagePath('Wall'), None),
            ' ': MapTile(' ', imagePath('Empty'), self.move_player),
            'a': MapTile('a', imagePath('Key_a'), self.pickup_item),
            'b': MapTile('b', imagePath('Key_b'), self.pickup_item),
            'c': MapTile('c', imagePath('Key_c'), self.pickup_item),
            'd': MapTile('d', imagePath('Key_d'), self.pickup_item),
            'A': MapTile('A', imagePath('Lock_A'), self.open_cell),
            'B': MapTile('B', imagePath('Lock_B'), self.open_cell),
            'C': MapTile('C', imagePath('Lock_C'), self.open_cell),
            'D': MapTile('D', imagePath('Lock_D'), self.open_cell),
            'e': MapTile('e', imagePath('Source'), self.grab_source),
            'E': MapTile('E', imagePath('Elevator'), self.finish),
            }
        self.fill_tile, self.end_tile = self.tiles[' '], self.tiles['E']
        self.environment = tile_game_engine.NavigationalFrame(
            Parent, self.tiles, playerTileType)
        self.environment.pack()
        self.generated_levels = iter(self.prep_levels(Levels))
        self.level_requirements, self.end_cell = next(self.generated_levels)
        self.inventory = tile_game_engine.InventoryFrame(Parent)
        self.inventory.pack()
        self.inventory.initialize_group("Keys", self.fill_tile, 4)
        self.inventory.initialize_group("Hands", self.fill_tile, 2)
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
        self.inventory.include("Keys", cellTo.tile)
        cellTo.replace_tile(self.fill_tile)
        self.move_player(moveTo, cellTo)
        
    def open_cell(self, moveTo, cellTo):
        requiredKey = self.tiles[cellTo.type.lower()]
        if self.inventory.is_carrying("Keys", requiredKey):
            self.inventory.remove("Keys", requiredKey)
            cellTo.replace_tile(self.fill_tile)
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


def main():
    gameWindow = tk.Tk()
    OfficeGame(gameWindow, '$', office_levels.levels)
    gameWindow.focus_force()
    gameWindow.mainloop()

main()
