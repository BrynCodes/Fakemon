import pickle
from os import listdir
from os.path import getmtime, join
from pathlib import Path

import pygame as py

from fakemon_battle import Battle
from fakemon_classes_n_funcs import Fakeball, UsefulItem, Transition, CONTROLLER, Item, AudioMixer, StateManager, Player
from fakemon_constants import WIDTH, HEIGHT
from fakemon_exploration import ExploreMode
from fakemon_states import StartMenu, PauseMenu, Inventory, Dialog, Shop, SettingsMenu


class Game:

    def __init__(self):
        py.init()
        self.win = py.display.set_mode((WIDTH, HEIGHT), py.NOFRAME)
        self.clock = py.time.Clock()
        self.running = True
        self.save = None
        self.player: Player = None
        self.transition = None
        self.prevState = None
        self.directory = Path('Data') / 'saves'

        self.audioMixer = AudioMixer()
        self.stateManager = StateManager('start', self.audioMixer)

        self.battle = Battle(self.stateManager, self, self.audioMixer)
        self.exploration = ExploreMode(self.stateManager, self, self.audioMixer)
        self.startMenu = StartMenu(self.stateManager, self)
        self.pauseMenu = PauseMenu(self.stateManager, self)
        self.inventory = Inventory()
        self.dialog = Dialog(self.stateManager, audioMixer=self.audioMixer)
        self.settings = SettingsMenu()

        self.shop = Shop([Fakeball('Fakeball'), Fakeball('Fakeball'), UsefulItem('Potion'), UsefulItem('Super Potion'),
                          UsefulItem('Guard Powder'), UsefulItem('Heal Berry'), UsefulItem('Protection Berry'),
                          UsefulItem('Quick Powder'), UsefulItem('Cool Orb'), UsefulItem('Luck Incense'),
                          Fakeball('Ultraball'),
                          Fakeball('Masterball'), Fakeball('Luxuryball'),
                          Item('Frost Key', 40, 'The key for the tundra gym.')], 'sell',
                         {2: Item('Jungle Key', 65, 'The key for the jungle gym.'),
                          1: Item('Sand Key', 75, 'The key for the beach gym.')})

        self.hospital = Shop([UsefulItem('Potion'), UsefulItem('Super Potion'), UsefulItem('Hyper Potion'),
                              UsefulItem('Strength Elixir'), UsefulItem('Accuracy Potion'), UsefulItem('Accuracy Pill'),
                              UsefulItem('Revitalising Mist')], 'heal')

        states = {'battle': self.battle,
                  'exploration': self.exploration,
                  'start': self.startMenu,
                  'pause': self.pauseMenu,
                  'inventory': self.inventory,
                  'dialog': self.dialog,
                  'shop': self.shop,
                  'hospital': self.hospital,
                  'settings': self.settings
                  }
        self.stateManager.setAllStates(states)

    def pauseGameKeyBoard(self, event):

        state = self.stateManager.getState('str')
        if event.key == py.K_ESCAPE:
            if state == 'exploration':
                self.stateManager.setState('pause')
            elif state == 'pause' or state == 'shop' or state == 'hospital' or state == 'inventory':
                self.stateManager.setState('exploration')
            elif state == 'settings':
                self.stateManager.setState(self.prevState)
                self.prevState = None

        elif event.key == py.K_e:
            if state == 'exploration':
                self.stateManager.setState('inventory')
            elif state == 'inventory':
                self.stateManager.setState('exploration')

    def pauseGameController(self):

        state = self.stateManager.getState('str')
        if CONTROLLER.getPressed('X'):
            if state == 'exploration':
                self.stateManager.setState('inventory')
            elif state == 'inventory':
                self.stateManager.setState('exploration')

        if CONTROLLER.getPressed('Pause'):
            if state == 'exploration' or state == 'shop' or state == 'hospital' or state == 'inventory':
                self.stateManager.setState('pause')
            elif state == 'pause':
                self.stateManager.setState('exploration')
        elif CONTROLLER.getPressed('B') and (
                state == 'pause' or state == 'shop' or state == 'hospital' or state == 'inventory'):
            self.stateManager.setState('exploration')
        elif CONTROLLER.getPressed('B') and state == 'settings':
            self.stateManager.setState(self.prevState)
            self.prevState = None

    def newGame(self):
        self.save = f'{self.directory}/save{len(listdir(self.directory))}.bin'
        self.player = Player()
        self.exploration.createChar(self.player)
        self.inventory.addCharacter(self.player)
        self.shop.addCharacter(self.player)
        self.hospital.addCharacter(self.player)
        self.audioMixer.playSound('loadGame')
        self.transition = Transition(lambda: self.stateManager.setState('exploration'))

        with open(self.save, 'wb') as save:
            pickle.dump(self.player, save)

    def loadGame(self):
        saves = listdir(self.directory)
        if saves:
            saves = [join(self.directory, save) for save in saves]
            saves.sort(key=getmtime)
            self.save = saves[-1]
            with open(self.save, 'rb') as save:
                self.player: Player = pickle.load(save)
            self.exploration.createChar(self.player)
            self.inventory.addCharacter(self.player)
            self.shop.addCharacter(self.player)
            self.hospital.addCharacter(self.player)
            self.audioMixer.playSound('loadGame')
            self.transition = Transition(lambda: self.stateManager.setState('exploration'))
        else:
            self.newGame()

    def saveGame(self):
        self.player.updatePos(self.exploration.player.rect.center, self.exploration.map)
        with open(self.save, 'wb') as save:
            pickle.dump(self.player, save)
        self.dialog.addText(['Game Saved'], 'pause')

    def quitGame(self):
        self.running = False

    def openSettings(self, prevState):
        self.prevState = prevState
        self.stateManager.setState('settings')

    def run(self):
        while self.running:
            dt = self.clock.tick(120) / 1000

            self.win.fill('black')

            CONTROLLER.update()

            for event in py.event.get():

                if event.type == py.QUIT:
                    self.running = False

                elif event.type == py.KEYDOWN:
                    self.pauseGameKeyBoard(event)
            if CONTROLLER:
                self.pauseGameController()

            self.stateManager.getState().update(self.win, dt)

            if self.transition:
                dt = min(dt, 0.1)
                self.transition.update(self.win, dt)
                if self.transition.completed:
                    self.transition = None
            py.display.update()


if __name__ == '__main__':
    try:
        py.FRect
    except AttributeError:
        raise ImportError('WRONG PYGAME, INSTALL PYGAME-CE (pygame will have to be uninstalled)') from None

    else:
        game = Game()
        game.run()
        py.quit()
