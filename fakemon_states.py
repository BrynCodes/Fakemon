import os

import numpy as np
import pygame as py

from OutlinedText import render
from fakemon_classes_n_funcs import Character, Fakemon, TextBox, UsefulItem, Fakeball, CONTROLLER, Player
from fakemon_constants import WIDTH, HEIGHT, FontPath, AssetsPath

py.font.init()
FONT = py.font.Font(FontPath, 50)
FONT1 = py.font.Font(FontPath, 75)
FONT2 = py.font.Font(FontPath, 200)
FONT3 = py.font.Font(FontPath, 30)


class Button(py.sprite.Sprite):

    def __init__(self, text, pos, function, *groups):
        super().__init__(*groups)
        directory = AssetsPath / 'Misc'/'Button'
        self.images = []
        for image in os.listdir(directory):
            self.images.append(py.image.load(f'{directory}/{image}').convert_alpha())

        self.image = self.images[0]
        self.function = function
        self.rect = self.image.get_rect(midtop=pos)
        self.text = FONT.render(text, False, 'White')
        self.textRect = self.text.get_rect(center=(150, 50))
        self.pressed = False

    def update(self):
        mouse_pos = py.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.image = self.images[1]
            if py.mouse.get_pressed()[0]:
                if not self.pressed:
                    self.textRect.centery += 13

                self.image = self.images[2]
                self.pressed = True

            else:
                self.image = self.images[1]
                if self.pressed:
                    self.function()
                    self.textRect.centery -= 13
                    self.pressed = False
        else:
            self.image = self.images[0]
            if self.pressed:
                self.function()
                self.textRect.centery -= 13
                self.pressed = False
        self.image.blit(self.text, self.textRect)


class Menu:
    def __init__(self, numButtons, offset=0):
        self.sprites = py.sprite.Group()
        self.size = 38 + (125 * numButtons)
        self.image = py.Surface((450, self.size), py.SRCALPHA)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + offset))

    def addButton(self, text, func):
        pos = self.rect.top + 25 + (len(self.sprites) * 125)
        Button(text, (WIDTH // 2, pos), func, self.sprites)

    def update(self, win, dt):
        win.blit(self.image, self.rect)
        py.draw.rect(self.image, (67, 67, 67, 230), py.Rect(0, 0, 450, self.size), border_radius=10)
        self.sprites.update()
        self.sprites.draw(win)


class PauseMenu(Menu):

    def __init__(self, stateManager, game):
        super().__init__(4)

        self.addButton('Resume', lambda: stateManager.setState('exploration'))
        self.addButton('Settings', lambda: game.openSettings('pause'))
        self.addButton('Save', game.saveGame)
        self.addButton('Quit', game.quitGame)


class StartMenu(Menu):

    def __init__(self, stateManager, game):
        super().__init__(4, 80)

        self.titleText = render('FAKEMON', FONT2, '#5d5d5d', (0, 0, 0), 3)
        self.titleTextRect = self.titleText.get_rect(center=(WIDTH // 2, 80))
        self.creditText = render('Made And Produced By Bryn M', FONT3, '#4c4c4c', (0, 0, 0))
        self.creditTextRect = self.creditText.get_rect(center=(WIDTH // 2, 150))

        self.addButton('Continue', game.loadGame)
        self.addButton('New Game', game.newGame)
        self.addButton('Settings', lambda: game.openSettings('start'))
        self.addButton('Quit', game.quitGame)

    def update(self, win, dt):
        super().update(win, dt)
        win.blit(self.titleText, self.titleTextRect)
        win.blit(self.creditText, self.creditTextRect)


class SettingsMenu(Menu):

    def __init__(self):
        super().__init__(1)
        self.addButton('Forgot This Bit.', lambda: None)


class InventoryItem:

    def __init__(self, pos, index, group):
        self.surf = py.Surface((64, 64), py.SRCALPHA)
        self.col = (45, 45, 45)

        self.rect = self.surf.get_rect(topleft=pos)
        self.center = tuple(map(lambda x: x + 32, pos))
        path = AssetsPath / 'Exploration'/'Inventory'
        self.highlightImg = py.image.load(path/'Highlight.png')
        self.selectImg = py.image.load(path/'Selection.png')
        self.outlineRect = self.selectImg.get_rect(center=self.center)

        self.image = None
        self.imageRect = None
        self.item = None

        self.selected = False
        self.highlighted = False
        self.index = index
        self.group = group

    def highlight(self):
        self.col = (34, 34, 34)
        self.showDead(80)
        self.highlighted = True

    def select(self):
        if self.item and not self.selected:
            self.selected = True
            return self
        return False

    def deselect(self):
        if self.item and self.selected:
            self.selected = False
            return self
        return False

    def showDead(self, col=100):
        if type(self.item) == Fakemon:
            if self.item.getHealth('') == 0:
                self.col = (col, 0, 0)

    def updateItem(self, item):
        self.item = item
        if self.item:
            self.image = self.item.getImage('Inventory')
            self.imageRect = self.image.get_rect(center=self.center)
        else:
            self.image = None
            self.imageRect = None

    def update(self, surf):
        surf.blit(self.surf, self.rect)
        py.draw.rect(self.surf, self.col, py.Rect(0, 0, 64, 64), border_radius=10)
        if self.image:
            surf.blit(self.image, self.imageRect)
        if self.selected:
            surf.blit(self.selectImg, self.outlineRect)
        elif self.highlighted:
            surf.blit(self.highlightImg, self.outlineRect)

        self.col = (45, 45, 45)
        self.showDead()
        self.highlighted = False


class ItemInfo:

    def __init__(self):
        self.surf = py.Surface((336, 416))
        self.rect = self.surf.get_rect(topleft=(928, 152))
        self.surf.fill((61, 61, 61))
        self.item = None
        self.image = py.Surface((192, 192))
        self.imgRect = self.image.get_rect(center=(170, 114))

    def updateItem(self, item, image):
        self.item = item
        self.image = image

    def update(self, win):
        if self.item:
            win.blit(self.surf, self.rect)
            self.surf.fill((61, 61, 61))

            py.draw.rect(self.surf, (45, 45, 45), py.Rect(72, 16, 192, 192), border_radius=30)
            py.draw.line(self.surf, (41, 41, 41), (16, 224), (320, 224), 4)

            self.surf.blit(self.image, self.imgRect)
            nameText = render(self.item.name, FONT, 'Black', 'White')
            self.surf.blit(nameText, nameText.get_rect(midtop=(168, 232)))
            self.surf.blit(FONT.render(self.item.getInfo(), True, 'Black', wraplength=330), (8, 272))

            if type(self.item) != Fakemon and self.item.name != 'Money':
                costText = render(f'Cost-${self.item.cost}', FONT, 'Black', 'White')
                self.surf.blit(costText, costText.get_rect(midbottom=(168, 408)))


class InteractableMenu:

    def __init__(self, slots, size):
        self.itemInfo = ItemInfo()
        self.allSlots = slots
        self.image = py.Surface((672, size))
        self.player: Player = None
        self.rect = self.image.get_rect(center=(WIDTH // 2 - 64, HEIGHT // 2))
        self.image.fill((61, 61, 61))
        self.highlightedSlot: InventoryItem = self.allSlots[0, 0]
        self.highlightedPos = [0, 0]
        self.selectedSlots: list[InventoryItem] = []

    @staticmethod
    def genInventorySlots(rows, columns, startPos, group):
        slots = [[] for _ in range(rows)]
        for i in range(rows):
            for j in range(columns):
                slots[i].append(InventoryItem((80 * j + startPos[0], 80 * i + startPos[1]), (i * 4) + j, group))
        return np.array(slots)

    @staticmethod
    def iterInventory(array):
        allItems = []
        for row in array:
            for item in row:
                allItems.append(item)
        return allItems

    def updateSlots(self, reset=False):
        for slot in self.iterInventory(self.allSlots):
            slot.updateItem(None)
            if reset:
                slot.highlighted = slot.selected = False
        if reset:
            self.selectedSlots = []

    def getHighlightedSlot(self):
        keys = py.key.get_just_pressed()
        shape = self.allSlots.shape
        if (keys[py.K_w] or CONTROLLER.getJustJoystick('Up')) and self.highlightedPos[0] != 0:
            self.highlightedPos[0] -= 1
        elif (keys[py.K_s] or CONTROLLER.getJustJoystick('Down')) and self.highlightedPos[0] != shape[0] - 1:
            self.highlightedPos[0] += 1
        if (keys[py.K_a] or CONTROLLER.getJustJoystick('Left')) and self.highlightedPos[1] != 0:
            self.highlightedPos[1] -= 1
        elif (keys[py.K_d] or CONTROLLER.getJustJoystick('Right')) and self.highlightedPos[1] != shape[1] - 1:
            self.highlightedPos[1] += 1
        self.highlightedSlot: InventoryItem = self.allSlots[*self.highlightedPos]
        self.highlightedSlot.highlight()
        if self.highlightedSlot.item:
            self.itemInfo.updateItem(self.highlightedSlot.item, py.transform.scale_by(self.highlightedSlot.image, 3))
        else:
            self.itemInfo.updateItem(None, None)
        self.selectSlot(keys[py.K_RETURN] or CONTROLLER.getPressed('A'))

    def selectSlot(self, key):
        if key and not self.highlightedSlot.selected:
            slot = self.highlightedSlot.select()
            if slot:
                self.selectedSlots.append(slot)
        elif key:
            slot = self.highlightedSlot.deselect()
            if slot:
                self.selectedSlots.remove(slot)

    def update(self, win, dt):
        self.itemInfo.update(win)


class Inventory(InteractableMenu):

    def __init__(self):

        self.fakemonsInUse = np.array([[InventoryItem(((80 * i) + 16, 16), i, 'fakemonsInUse') for i in range(4)]])
        self.itemsInUse = np.array([[InventoryItem(((80 * i) + 352, 16), i, 'itemsInUse') for i in range(4)]])
        self.fakemons = self.genInventorySlots(5, 4, (16, 112), 'fakemons')
        self.items = self.genInventorySlots(4, 4, (352, 112), 'items')
        self.unsellables = np.array([[InventoryItem(((80 * i) + 352, 432), i, 'unsellables') for i in range(4)]])
        self.allItems = np.concatenate((self.itemsInUse, self.items))
        self.allFakemons = np.concatenate((self.fakemonsInUse, self.fakemons))

        super().__init__(np.concatenate((self.allFakemons, np.concatenate((self.allItems, self.unsellables))), axis=1),
                         512)

        self.text = [render(f'Fakemons', FONT1, 'Black', 'White'), render(f'Items', FONT1, 'Black', 'White')]
        self.textRect = [self.text[0].get_rect(midbottom=(408, 116)), self.text[1].get_rect(midbottom=(744, 116))]

    def addCharacter(self, player):
        self.player: Player = player
        self.updateItems()

    def updateItems(self):
        self.updateSlots()
        for fakemon, slot in zip(self.player.fakemonsInUse, self.fakemonsInUse[0]):
            slot.updateItem(fakemon)

        for fakemon, slot in zip(self.player.fakemonsNotInUse, self.iterInventory(self.fakemons)):
            slot.updateItem(fakemon)

        for item, slot in zip(self.player.itemsInUse, self.itemsInUse[0]):
            slot.updateItem(item)

        for item, slot in zip(self.player.itemsNotInUse, self.iterInventory(self.items)):
            slot.updateItem(item)

        for item, slot in zip(self.player.unsellableItems, self.unsellables[0]):
            slot.updateItem(item)

    def swapSelected(self):
        if len(self.selectedSlots) == 2:
            if self.selectedSlots[0] in self.iterInventory(self.allFakemons):
                group = self.allFakemons
                iORf = 'Fakemons'
            else:
                group = self.allItems
                iORf = 'Items'
            if self.selectedSlots[1] in self.iterInventory(group):
                selectedFakemon = []
                for i in self.selectedSlots:
                    selectedFakemon.append(i)

                self.player.swap(iORf, selectedFakemon)
                for i in self.selectedSlots:
                    i.deselect()
                self.selectedSlots = []

    def update(self, win, dt):
        super().update(win, dt)
        win.blit(self.image, self.rect)
        self.image.fill((61, 61, 61))
        for text, rect in zip(self.text, self.textRect):
            win.blit(text, rect)
        py.draw.line(self.image, (41, 41, 41), (16, 94), (640, 94), 4)
        py.draw.line(self.image, (41, 41, 41), (336, 16), (336, 496), 4)
        py.draw.line(self.image, (41, 41, 41), (352, 424), (656, 424), 4)
        self.player.updateLists()
        self.getHighlightedSlot()
        self.swapSelected()
        self.updateItems()
        for row in self.allSlots:
            for slot in row:
                slot.update(self.image)


class Shop(InteractableMenu):

    def __init__(self, items: list[UsefulItem | Fakeball], option2='sell', levelLockedItems=None):
        super().__init__(self.genInventorySlots(5, 4, (352, 16), 'shopItems'), 416)
        self.products = items
        self.levelLockedItems = levelLockedItems
        self.buttons = py.sprite.Group()

        Button('Confirm', (406, 440), lambda: self.confirm(), self.buttons)
        Button('BUY', (406, 168), lambda: self.switchModes('buy'), self.buttons)
        Button(option2.capitalize(), (406, 293), lambda: self.switchModes(option2), self.buttons)

        self.mode = 'buy'
        self.items = self.products
        self.textInv = render('INVENTORY', FONT1, 'Black', 'White')
        self.textShop = render('SHOP', FONT1, 'Black', 'White')
        self.invRect = self.textInv.get_rect(midtop=(744, 82))
        self.shopRect = self.textShop.get_rect(midtop=(744, 82))

    def updateItems(self, reset=False):
        self.updateSlots(reset)
        try:
            self.products.append(self.levelLockedItems.pop(self.player.level))
        except (KeyError, AttributeError):
            pass

        for item, slot in zip(self.items, self.iterInventory(self.allSlots)):
            slot.updateItem(item)

    def addCharacter(self, player):
        self.player = player

    def switchModes(self, mode):
        if self.mode != mode:
            self.mode = mode
            if mode == 'sell':
                self.items = self.player.itemsNotInUse
            elif mode == 'heal':
                self.getDamagedFakemon()
            else:
                self.items = self.products
            self.updateItems(True)

    def getDamagedFakemon(self):
        self.items = []
        for fakemon in self.player.fakemons:
            if fakemon.getHealth('p') != 1:
                self.items.append(fakemon)

    def confirm(self):
        if self.mode == 'buy':
            total = 0
            for slot in self.selectedSlots:
                total += slot.item.cost
            if self.player.money - total >= 0:
                self.player.addItem(*[slot.item for slot in self.selectedSlots])
                for slot in self.selectedSlots:
                    self.products.remove(slot.item)
                    slot.updateItem(None)
                self.player.changeMoney(-total)
                self.updateItems(True)

        elif self.mode == 'heal':
            total = len(self.selectedSlots) * 5
            if self.player.money - total >= 0:
                for slot in self.selectedSlots:
                    slot.item.changeHealth(1000)
                    slot.updateItem(None)
                self.player.changeMoney(-total)
                self.getDamagedFakemon()
                self.updateItems(True)

        else:
            total = 0
            for slot in self.selectedSlots:
                total += slot.item.cost

            for slot in self.selectedSlots:
                self.player.itemsNotInUse.remove(slot.item)
                slot.updateItem(None)
            self.player.changeMoney(total)
            self.updateItems(True)

    def update(self, win, dt):
        super().update(win, dt)
        win.blit(self.image, self.rect)
        self.image.fill((61, 61, 61))
        self.getHighlightedSlot()
        self.updateItems()
        self.player.updateLists()
        py.draw.line(self.image, (41, 41, 41), (336, 16), (336, 400), 4)
        py.draw.line(self.image, (41, 41, 41), (16, 271), (320, 271), 4)

        if self.mode == 'sell' or self.mode == 'heal':
            win.blit(self.textInv, self.invRect)
        else:
            win.blit(self.textShop, self.shopRect)

        win.blit(render(f'MONEY: ${self.player.money}', FONT1, 'Black', 'White'), (286, 82))

        for row in self.allSlots:
            for slot in row:
                slot.update(self.image)
        self.buttons.update()
        self.buttons.draw(win)


class Dialog:

    def __init__(self, stateManager, audioMixer):
        self.text = ''
        self.audioMixer = audioMixer
        self.textBox = py.sprite.GroupSingle()
        self.stateManager = stateManager
        self.count = 0
        self.state = 'exploration'
        self.args = ()

    def addText(self, text, state='exploration', args=()):
        self.text: list[str] = text
        self.state = state
        if state == 'battle':
            self.args = args
        self.stateManager.setState('dialog')
        TextBox(text[0], self.textBox)

    def update(self, win, dt):
        key = py.key.get_just_pressed()[py.K_RETURN] or CONTROLLER.getPressed('A')
        if key:
            self.audioMixer.playSound('read')
            self.count += 1
            if self.count == len(self.text):
                self.count = 0
                self.stateManager.setState(self.state, *self.args)
            else:
                TextBox(self.text[self.count], self.textBox)
        self.textBox.update(True)
        self.textBox.draw(win)


def main():
    win = py.display.set_mode((WIDTH, HEIGHT))
    rr = py.time.Clock()
    running = True
    char = Player()
    char.selectedFakemon.changeHealth(-30)
    shop = Shop([
        Fakeball('Fakeball'),
        UsefulItem('Potion'),
        UsefulItem('Luck Incense')
    ], 'heal')
    shop.addCharacter(char)
    while running:
        win.fill('black')
        dt = rr.tick(120) // 1000
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False

        shop.update(win, dt)

        py.display.update()


if __name__ == '__main__':
    py.init()
    main()
    py.quit()
