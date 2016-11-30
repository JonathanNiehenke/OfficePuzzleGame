from collections import OrderedDict
from functools import partial

import tkinter as tk
from tkinter import messagebox

import game

class LevelEditor(object):


    def __init__(self, Parent, levelFilename=None):
        self.parent = Parent
        self.parent.title("Level Editor")
        self.parent.bind("<Key>", self.__handle_key)
        imagePath = 'Images\\{}.png'.format
        self.tiles = OrderedDict([
            (' ', tk.PhotoImage(file=imagePath('Empty'))),
            ('#', tk.PhotoImage(file=imagePath('Wall'))),
            ('e', tk.PhotoImage(file=imagePath('Source'))),
            ('E', tk.PhotoImage(file=imagePath('Elevator'))),

            ('a', tk.PhotoImage(file=imagePath('RedKey'))),
            ('b', tk.PhotoImage(file=imagePath('BlueKey'))),
            ('c', tk.PhotoImage(file=imagePath('GreenKey'))),
            ('d', tk.PhotoImage(file=imagePath('YellowKey'))),
            ('A', tk.PhotoImage(file=imagePath('RedLock'))),
            ('B', tk.PhotoImage(file=imagePath('BlueLock'))),
            ('C', tk.PhotoImage(file=imagePath('GreenLock'))),
            ('D', tk.PhotoImage(file=imagePath('YellowLock'))),

            ('$', tk.PhotoImage(file=imagePath('Player'))),
            ('m', tk.PhotoImage(file=imagePath('MotionOn'))),
            ('N', tk.PhotoImage(file=imagePath('Signal'))),
            ('J', tk.PhotoImage(file=imagePath('WetFloor'))),

            ('k', tk.PhotoImage(file=imagePath('Flashlight'))),
            ('l', tk.PhotoImage(file=imagePath('LightOff'))),
            ('K', tk.PhotoImage(file=imagePath('Darkness'))),
            ('j', tk.PhotoImage(file=imagePath('Mop'))),

            ('@', tk.PhotoImage(file=imagePath('DropZone'))),
            (':', tk.PhotoImage(file=imagePath('OpenNarrow'))),
            ('g', tk.PhotoImage(file=imagePath('Cart'))),
            ('G', tk.PhotoImage(file=imagePath('Plant'))),

            ('h', tk.PhotoImage(file=imagePath('Papers'))),
            ('H', tk.PhotoImage(file=imagePath('Desk'))),
            ('i', tk.PhotoImage(file=imagePath('Trash'))),
            ('I', tk.PhotoImage(file=imagePath('TrashCan'))),

            ('q', tk.PhotoImage(file=imagePath('LightPlug'))),
            ('r', tk.PhotoImage(file=imagePath('Computer'))),
            ('R', tk.PhotoImage(file=imagePath('ComputerPlug'))),
            ('s', tk.PhotoImage(file=imagePath('Socket'))),

            ('p', tk.PhotoImage(file=imagePath('PrinterX'))),
            ('P', tk.PhotoImage(file=imagePath('Printer'))),

        ])
        self.test_button = tk.Button(
            Parent, text="Test", command=self.__test)
        self.reset_button = tk.Button(
            Parent, text="Reset", command=self.__reset)
        self.tile_buttons = tk.Frame(Parent)
        self.level_entry = tk.Text(
            Parent, font=('Courier', 12), width=20, height=10)
        self.level_preview = tk.Frame(Parent)
        self.test_button.grid(row=0, column=0, sticky='we')
        self.reset_button.grid(row=1, column=0, sticky='we')
        self.tile_buttons.grid(row=2, column=0, rowspan=2, sticky='n')
        self.level_entry.grid(row=0, column=1, rowspan=3)
        self.level_preview.grid(row=3, column=1)
        self.__build_tile_buttons()
        self.__reset()

    def __build_tile_buttons(self):
        Command = self.__button_update
        for i, (Char, Image) in enumerate(self.tiles.items()):
            Row, Col = divmod(i, 4)
            button = tk.Button(self.tile_buttons, image=Image,
                               command=partial(Command, Char))
            button.grid(row=Row, column=Col)

    def __handle_key(self, Event):
        """Handles keyboard input to quit or edit."""
        keyPressed = Event.keysym
        if (keyPressed == "Escape" and
                messagebox.askyesno("Quit?", "You want to quit?")):
            self.parent.destroy()
        else:
             self.__update()

    def __iter_entry(self):
        Lines = self.level_entry.get(1.0, "end").splitlines()
        for Row, rowCells in enumerate(Lines):
            for Col, Tile in enumerate(rowCells):
                yield Row, Col, Tile

    def __button_update(self, Char):
        self.level_entry.delete("insert")
        self.level_entry.insert("insert", Char)
        self.__update()

    def __update(self):
        for child in self.level_preview.winfo_children():
            child.destroy()
        for Row, Col, Tile in self.__iter_entry():
            tkImg = tk.Label(self.level_preview, image=self.tiles[Tile])
            tkImg.grid(row=Row, column=Col)

    def __test(self):
        with open("temp.txt", 'w') as File:
            print('"Editor Test"', file=File)
            print(self.level_entry.get(1.0, "end"), file=File)
        gameWindow = tk.Toplevel(self.parent)
        game.OfficeGame(gameWindow, "temp.txt")
        gameWindow.focus_set()
        self.parent.wait_window(gameWindow)
        self.parent.focus_set()

    def __reset(self):
        self.level_entry.delete(1.0, "end")
        self.level_entry.insert(1.0,
            "#######\n"
            "#     #\n"
            "#     #\n"
            "#     #\n"
            "#######\n"
        )
        self.__update()


editorWindow = tk.Tk()
LevelEditor(editorWindow)
editorWindow.focus_set()
editorWindow.mainloop()
