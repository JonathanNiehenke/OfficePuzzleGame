"""

"""
# Navigational Hinderences - Solutions
#   Locks and Standard Key (Unique).
#   Slots and KeyCards (Stable).
#   Lighting and switches or their sockets and plugs (Masked Stable).
#   Motion detector and the security code and terminals (Masked Stable).
#   Wet floor and Mop (Dependant).
#   Cart and mess of papers - free hands.
# One way mechanic - Narrow Passageways and two handed object.
# Distance limitation - sockets and plugs.
# Rerouting
#   Emergency = Bathroom, dying phone battery, disable security alarm.
#   forget current task, Reminder, and correcting a mistake.

from random import randint
from tkinter import font, messagebox
import tkinter as tk

import tile_game
import office_levels

class OfficeGame(object):

    def __init__(self, Parent, Levels, Legend, legendPath):
        self.parent, self.level = Parent, Levels
        self.tile, self.handler = tile_game.understand_legend(
            Legend, legendPath)
        Displayed= [('Standard Key', 'abcd'),('Hands', ('Hands',))]
        inventoryGraphic = tile_game.Inventory(Parent, self.tile, Displayed)
        Map = tile_game.MapFrame(Parent, self.tile, self.handler)
        Map.build(*self.level)

    def build_levels(self, Levels):
        for Title, Structure, *Messages in Levels:
            for Message in Messages:
               pass 

def move_player(self, moveTo, cellType):
    self.map_frame.move_player(moveTo, cellType)
    self.message.set('')

def enter_cell(self, moveTo, cellType):
    self.open_cell(moveTo, cellType, onTile=cellType)

def open_lock(self, moveTo, cellType):
    self.open_cell(moveTo, cellType, onTile=' ', keyRemain=False)

def open_cell(self, moveTo, cellType, onTile=' ', keyRemain=True):
    requiredKey = cellType.lower()
    if self.inventory.get(requiredKey):
        self.change_inventory_item(requiredKey, keyRemain)
        self.move_player(moveTo, onTile)
    else:
        self.explain(cellType)

def explain(self, cellType):
    Explination = {
        '^': "Too narrow to pass while hands are full.",
        'K': "Too dark to pass.",
        'N': "Security sensor ahead.",
        'Q': "You've reached the end of the cord.",
        }
    try:
        Reason = Explination[cellType]
    except KeyError:
        pass
    else:
        self.message.set(Reason)

def pickup_hand_item(self, moveTo, cellType):
    if self.inventory.get('Hand', ' ') == ' ':
        self.pickup_item(moveTo, cellType)
        self.change_hand_item(cellType)
        self.change_requirements(+1)

def pickup_item(self, moveTo, cellType):
    self.change_inventory_item(cellType, True)
    self.move_player(moveTo, ' ')

def accept_hand_item(self, moveTo, cellType):
    self.accept_item(moveTo, cellType, cellType)
    self.change_hand_item(cellType)

def accept_required_item(self, moveTo, cellType, Replace='#'):
    self.accept_item(moveTo, cellType, Replace)
    self.change_requirements(+1)

def accept_item(self, moveTo, cellType, Replace='#'):
    self.change_inventory_item(cellType, True)
    self.map_frame.change_cells((moveTo, Replace))

def finish(self, moveTo, _):
    self.move_player(moveTo, ' ')
    self.locations, self.requirements, self.end = next(self.levels)

def grab_source(self, moveTo, _):
    self.change_requirements(-1)
    self.move_player(moveTo, ' ')
    self.message.set('Source information obtained.')

def enter_pin_lock(self, moveTo, cellType, inventoryKey='LockPin'):
    pinNumber = self.generate_pin(inventoryKey)
    tile_game2.PinEntry(
        self.parent, pinNumber, self.move_player, moveTo, cellType)

def display_lock_pin(self, moveTo, cellType, inventoryKey='LockPin'):
    pinNumber = self.generate_pin(inventoryKey)
    Message = 'The Pin Number is {}.'.format(pinNumber)
    self.message.set(Message)

def generate_pin(self, inventoryKey):
    try:
        pinNumber = self.inventory[inventoryKey]
    except KeyError:
        pinNumber = str(randint(100000, 999999))
        self.inventory[inventoryKey] = pinNumber
    return pinNumber

def drop_paper(self, moveTo, _):
    if self.inventory.get('Hand') == 'H':
        self.drop('H')

def drop_trash(self, moveTo, _):
    if self.inventory.get('Hand') == 'I':
        self.drop('I')

def drop(self, handItem):
        self.change_hand_item(' ')
        self.change_requirements(-1)

def swap_mop(self, moveTo, cellType):
    self.swap_returned_item(moveTo, cellType, 'j')

def swap_flashlight(self, moveTo, cellType):
    self.swap_returned_item(moveTo, cellType, 'k')

def swap_returned_item(self, moveTo, cellType, returningItem):
    self.swap_items(moveTo, cellType, returningItem)
    if self.inventory[returningItem]:
        self.change_requirements(+1)
    elif self.inventory[moveTo] == returningItem:
        self.change_requirements(-1)
    else:
        pass  # A swap not including the returning item was enacted.
        
def swap_items(self, moveTo, cellType, emptyDrop='@'):
    fromHand = self.inventory.get('Hand', ' ')
    fromDrop = self.inventory.get(moveTo, emptyDrop)
    toHand = {'@': ' '}.get(fromDrop, fromDrop)
    toDrop = {' ': '@'}.get(fromHand, fromHand)
    self.change_inventory_item(toHand, True)
    self.change_inventory_item(toDrop, False)
    self.change_hand_item(toHand)
    self.inventory[moveTo] = toDrop
    self.map_frame.change_cell_image((moveTo, toDrop))

    if fromHand == ' ':
        self.change_requirements(+1)
    if toHand == ' ':
        self.change_requirements(-1)

def enter_darkness(self, moveTo, cellType):
    for Val in 'Kl':
        self.open_cell(moveTo, Val, onTile=cellType)

def turn_light_on(self, moveTo, cellType):
    self.accept_required_item(moveTo, cellType, Replace='L')

def turn_light_off(self, moveTo, _):
    self.change_inventory_item('l', False)
    self.map_frame.change_cells((moveTo, 'l'))
    self.change_requirements(-1)

def turn_motion_off(self, moveTo, cellType):
    pinNumber = self.generate_pin('MotionPin')
    tile_game2.PinEntry(
        self.parent,
        pinNumber,
        self.accept_required_item,
        moveTo,
        cellType,
        'M',
        )

def turn_motion_on(self, moveTo, cellType):
    self.change_inventory_item('m', False)
    self.map_frame.change_cells((moveTo, 'm'))
    self.change_requirements(-1)

def enter_motion(self, moveTo, cellType):
    self.open_cell(moveTo, 'M', cellType)

def display_motion_pin(self, moveTo, cellType):
    self.display_lock_pin(moveTo, cellType, 'MotionPin')

def grab_print(self, moveTo, cellType):
    if self.inventory.get('p'):
        self.inventory['p'] = False
        self.change_requirements(-1)
        self.message.set('Source information obtained.')

def print_source(self, moveTo, cellType):
    self.accept_item(moveTo, cellType)
    self.message.set('Print job sent.')

def plug_in(self, moveTo, cellType):
    handItem = self.inventory.get('Hand')
    if handItem in 'qRr':
        self.change_inventory_item(handItem, False)
        self.change_hand_item(' ')
        Replacing = ((Index, 'l') for Index in self.locations[handItem])
        self.map_frame.change_cells((moveTo, 's'), *Replacing)
        self.inventory[moveTo] = cellType

def limit_plug(self, moveTo, cellType):
    if any(self.inventory.get(Plug) for Plug in 'qRr'):
        self.explain(cellType)
    else:
        self.move_player(moveTo, cellType)

def remove_plug(self, moveTo, _):
    pass

def remote_activate(cellType):
    for Index in self.locations[cellType]:
        self.handlers[cellType](Index, cellType)

def through_narrow(self, moveTo, cellType):
    if self.inventory.get('Hand', ' ') == ' ':
        self.move_player(moveTo, cellType)
    else:
        self.explain(cellType)

def open_card_lock(self, moveTo, cellType):
    if cellType in 'EFGHIJ':
        self.move_player(moveTo, ' ')

def change_inventory_item(self, Item, Include):
    self.inventory[Item] = Include
    if Include:
        self.inventory_frame.display(Item)
    else:
        self.inventory_frame.mask(Item)

def change_hand_item(self, Item):
    self.inventory['Hand'] = Item
    self.tkHands.config(image=self.tile[Item])

def change_requirements(self, Value):
    self.requirements += Value
    if self.requirements:
        self.map_frame.change_cells((self.end, ' '))
    else:
        self.map_frame.change_cells((self.end, 'E'))
    print(self.requirements)

Levels = office_levels.levels
Legend = {
    '#': ('Wall', None),
    '$': ('Person', None),
    ' ': ('Blank', move_player),
    'A': ('Lock1', open_lock),
    'B': ('Lock2', open_lock),
    'C': ('Lock3', open_lock),
    'D': ('Lock4', open_lock),
    'a': ('Key1', pickup_item),
    'b': ('Key2', pickup_item),
    'c': ('Key3', pickup_item),
    'd': ('Key4', pickup_item),
    'E': ('Elevator', finish),
    'e': ('Source', grab_source),
    'F': ('PinLock', enter_pin_lock),
    'f': ('PinNumber', display_lock_pin),
    'G': ('Plant', pickup_hand_item),
    'g': ('Cart', pickup_hand_item),
    'H': ('Papers', pickup_hand_item),
    'h': ('Desk', drop_paper),
    'I': ('Trash', pickup_hand_item),
    'i': ('TrashCan', drop_trash),
    'J': ('WetFloor', open_cell),
    'j': ('Mop', swap_mop),
    'K': ('Blank', enter_darkness),
    'k': ('Flashlight', swap_flashlight),
    'L': ('LightOn', turn_light_off),
    'l': ('LightOff', turn_light_on),
    'M': ('KeyCard_Yellow', turn_motion_on),
    'm': ('Eye', turn_motion_off),
    'N': ('Blank', enter_motion),
    'n': ('PinNumber', display_motion_pin),
    'P': ('Printer', grab_print),
    'p': ('Computer', print_source),
    'Q': ('Blank', limit_plug),
    'q': ('LightPlug', accept_hand_item),
    'R': ('PrinterPlug', accept_hand_item),
    'r': ('ComputerPlug', accept_hand_item),
    'S': ('Socket', plug_in),
    's': ('PluggedSocket', remove_plug),
    '@': ('DropZone', swap_items),
    }
legendPath = './{}.png'.format

def main():
    gameWindow = tk.Tk()
    gameWindow.option_add("*Background", 'lightblue')
    OfficeGame(gameWindow, Levels, Legend, legendPath)
    gameWindow.focus_force()
    gameWindow.mainloop()


main()
