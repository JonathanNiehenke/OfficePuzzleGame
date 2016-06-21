import tkinter as tk

import tile_game_engine

class OfficeGame(object):

    def __init__(self, Parent, playerTile, Level):
        MapTile = tile_game_engine.MapTile
        Tiles = {
            '$': MapTile('$', 'Images\Player.png', None),
            '#': MapTile('#', 'Images\Wall.png', None),
            ' ': MapTile(' ', 'Images\Empty.png', self.move_player),
            }
        self.parent, self.level = Parent, Level
        self.game_environment = tile_game_engine.MapFrame(Parent, Tiles, playerTile)
        self.game_environment.build(Level)
        self.parent.bind("<Key>", self.game_environment.handle_input)

    def move_player(self, moveTo, cellTo):
        self.game_environment.move_player(moveTo, cellTo)

    def open_cell(self, moveTo, cellTo):
        requiredKey = cellTo.type.lower()
        

def main():
    gameWindow = tk.Tk()
    OfficeGame(gameWindow, '$', Level)
    gameWindow.focus_force()
    gameWindow.mainloop()

Level = (
    '#####',
    '#$  #',
    '### #',
    '#   #',
    '#####')

main()
