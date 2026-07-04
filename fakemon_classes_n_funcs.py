from pathlib import Path
from random import randint

import pygame as py
from numpy.random import choice

from fakemon_constants import weakness, HEIGHT, WIDTH, AssetsPath, FontPath

miscPath = AssetsPath / 'Misc'
py.font.init()
py.joystick.init()
FONT = py.font.Font(FontPath, 60)
dataPath = Path('Data')

class Fakemon:

    def __init__(self, name, owner, aName):

        with open(dataPath/'fakemons') as file:
            for i in file:
                if i.split(',')[0] == aName:
                    self.info = i.split(',')
                    self.info[1] = int(self.info[1])
                    self.info[2] = int(self.info[2])
                    break
            else:
                self.info = [aName, 100, 0.01, 'Surf', 'Protect', 'normal']

        self.moveNames = self.info[3:-1]
        self.health = self.info[1]
        self.type = self.info[-1].rstrip('\n')
        self.owner = owner
        self.name = name
        self.aName = aName
        self.evasion = self.info[2]
        self.moves = {}
        self.dead = False

        self.effectiveness = 1
        self.hitChanceInc = 0
        self.animation = ''

        if self.owner == 'player':
            self.pronouns = ['you', 'your']
        else:
            self.pronouns = ['they', 'their']

        for move in self.moveNames:
            self.moves.update({move: Move(move)})

    def __repr__(self):
        return join([self.name, self.health, self.info[-1].capitalize()])

    def changeHealth(self, amount):
        if self.health + amount < 0:
            self.health = 0
        elif self.health + amount > self.info[1]:
            self.health = self.info[1]
        else:
            self.health += amount

    def updateOwner(self, owner):
        self.owner = owner
        if self.owner == 'player':
            self.pronouns = ['you', 'your']
        else:
            self.pronouns = ['they', 'their']

    def getHealth(self, type):
        if type == 'p':
            return self.health / self.info[1]
        elif type == 't':
            return self.info[1]
        else:
            return self.health

    def getInfo(self):
        return join([self.health, self.info[-1].capitalize()])

    def moveType(self, moveName, typeOfMove):
        if self.moves[moveName].aORd == typeOfMove:
            return True
        return False

    def getAnimation(self):
        temp = self.animation
        self.animation = ''
        return temp

    def performMove(self, moveName, enemy, audioMixer):
        move = self.moves[moveName]
        output = ''
        if move.aORd == 'Attack':
            audioMixer.playSound('attack')
            if randint(1, 100) < (move.accuracy - enemy.evasion) + self.hitChanceInc:
                for i in [0, 0.5, 1, 2]:
                    if enemy.type in weakness[move.type][i]:
                        overallEffectiveness = i * enemy.effectiveness
                        enemy.effectiveness = 1
                        self.hitChanceInc = 0
                        damage = (move.effect * overallEffectiveness)
                        enemy.changeHealth(-damage)
                        if overallEffectiveness == 0:
                            output = f'{self.pronouns[1].capitalize()} {moveName} did no damage'
                            break
                        elif overallEffectiveness < 0.75:
                            output = f"{self.pronouns[1].capitalize()} {moveName} wasn't very effective.\n{self.pronouns[0].capitalize()} did {damage} damage."
                        elif overallEffectiveness < 1.25:
                            output = f'{self.pronouns[1].capitalize()} {moveName} did {damage} damage.'
                        else:
                            output = f'{self.pronouns[1].capitalize()} {moveName} was super effective.\n{self.pronouns[0].capitalize()} did {damage} damage.'
                        enemy.animation = 'damage'
                        if damage > 0:
                            audioMixer.playSound('hit')
                        break
            else:
                output = f'{self.pronouns[1].capitalize()} {moveName} missed'
        elif move.aORd == 'Defend':
            self.effectiveness -= move.effect
            output = f"{self.pronouns[0].capitalize()} reduced {self.pronouns[1]} enemies\nnext moves' effectiveness"
            self.animation = 'statInc'
        return output

    def getDetails(self):
        fakemonType = self.info[-1].capitalize()
        space = 16 - len(fakemonType + self.name)
        return f'{self.name}{space // 2 * ' '}-{space // 2 * ' '}{fakemonType}'

    def getImage(self, imgType):
        if imgType == 'Battle':
            try:
                if self.owner == 'player':
                    image = py.transform.scale_by(
                        py.image.load(AssetsPath/'Battle'/'FakemonSprites'/f'{self.aName}Back.png').convert_alpha(), 4)
                else:
                    image = py.transform.scale_by(
                        py.image.load(AssetsPath/'Battle'/'FakemonSprites'/f'{self.aName}Front.png').convert_alpha(), 4)
            except FileNotFoundError:
                image = py.Surface((256, 256))
                image.fill('green')
        else:
            try:
                image = py.transform.scale_by(
                    py.image.load(AssetsPath/'Exploration'/'Inventory'/'FakemonSprites'/f'{self.aName}.png').convert_alpha(), 2)
            except FileNotFoundError:
                image = py.Surface((40, 40))
        return image

    def useItem(self, item):
        for effect in item.effects:
            match effect[0]:
                case 'Health':
                    self.changeHealth(int(effect[1]))
                case 'Accuracy':
                    self.hitChanceInc += int(effect[1])
                case 'Effectiveness':
                    self.effectiveness -= float(effect[1])


class Move:

    def __init__(self, name):
        self.name = name
        with open(dataPath/'moves') as file:
            for line in file:
                temp = line.split(',')
                if temp[0] == self.name:
                    self.effect = temp[1]
                    self.accuracy = int(temp[2])
                    self.type = temp[3]
                    self.aORd = temp[4].rstrip('\n')
                    break
            else:
                print()

        self.effect = int(self.effect) if self.aORd == 'Attack' else float(self.effect)

    def getInfo(self):
        return join([self.effect, self.type.capitalize(), self.aORd])


class Item:

    def __init__(self, name, cost=None, description=''):
        self.name = name
        self.col = list(choice(range(256), size=3))
        self.cost = cost
        self.description = description

    def getImage(self, x):
        try:
            image = py.transform.scale_by(
                py.image.load(AssetsPath/'Exploration'/'Inventory'/'ItemSprites'/f'{self.name}.png').convert_alpha(), 2)
        except FileNotFoundError:
            image = py.Surface((40, 40))
            image.fill(self.col)
        return image

    def getInfo(self):
        return self.description

    def changeDescription(self, description):
        self.description = description


class UsefulItem(Item):

    def __init__(self, name):
        super().__init__(name)

        with open(dataPath/'items') as file:
            for lineNum, line in enumerate(file):
                if lineNum < 13:
                    temp = line.split(',')
                    if temp[0] == self.name:
                        self.effectInfo = temp[1:-1]
                        self.cost = int(temp[-1])
                        break
        self.effects = []
        for i in self.effectInfo:
            self.effects.append(i.split('-'))

    def __repr__(self):
        return f'\033[1m{self.name}\033[0m : {self.effects} {self.cost}'

    def getInfo(self):
        return join(self.effectInfo)


class Fakeball(Item):

    def __init__(self, name):
        super().__init__(name)

        with open(dataPath/'items') as file:
            for lineNum, line in enumerate(file):
                if lineNum > 12:
                    temp = line.split(',')
                    if temp[0] == self.name:
                        self.accuracy = int(temp[1])
                        self.cost = int(temp[2])

    def __repr__(self):
        return f'\033[1m{self.name}\033[0m: {self.accuracy} {self.cost}'

    def getInfo(self):
        return f'Accuracy-{str(self.accuracy)}'


class Character:

    def __init__(self, *fakemon, identity='them'):

        self.fakemons = list(fakemon)

        self.selectedFakemon: Fakemon = self.fakemons[0]
        self.identity = identity

        self.fakemonsInUse = self.fakemons[:4]
        self.fakemonsNotInUse = self.fakemons[4:]

        self.justDied = None

    def changeSelectedFakemon(self, fakemon: Fakemon = None):  #
        if fakemon:
            if fakemon in self.fakemonsInUse and not fakemon.dead:
                self.selectedFakemon = fakemon
        else:
            for fakemon in self.fakemonsInUse:
                if not fakemon.dead:
                    self.selectedFakemon = fakemon
                    break
            else:
                self.selectedFakemon = None

    def getFreshlyDead(self):  #
        justDied = self.justDied
        self.justDied = False
        return justDied

    def checkIfFainted(self):  #
        if self.selectedFakemon:
            if self.selectedFakemon.dead:
                for fakemon in self.fakemonsInUse:
                    if not fakemon.dead:
                        self.selectedFakemon = fakemon
                        return False
                else:
                    return True
            return False
        return 'x'

    def updateLists(self):  #
        for fakemon in self.fakemonsInUse:
            if not fakemon.dead:
                if fakemon.getHealth('') == 0:
                    fakemon.dead = True
                    self.justDied = fakemon
            else:
                if fakemon.getHealth('') > 0:
                    fakemon.dead = False
        while True:
            if self.fakemonsNotInUse and len(self.fakemonsInUse) != 4:
                self.addFakemon(self.fakemonsNotInUse.pop(0))
            elif not self.fakemonsNotInUse or len(self.fakemonsInUse) == 4:
                break
        self.fakemons = self.fakemonsInUse + self.fakemonsNotInUse

    def addFakemon(self, fakemon):  #
        fakemon.updateOwner(self.identity)
        if len(self.fakemonsInUse) == 4:
            self.fakemonsNotInUse.append(fakemon)
        else:
            self.fakemonsInUse.append(fakemon)


class Player(Character):

    def __init__(self):
        super().__init__(Fakemon('Ben', 'player', 'Mightyena'), identity='player')

        self.items = [UsefulItem('Potion'), Fakeball('Fakeball'), UsefulItem('Potion')]
        self.itemsInUse = self.items[:4]
        self.itemsNotInUse = self.items[4:]
        self.pos = (189, 191)
        self.read = []
        self.level = 0
        self.location = 'Start House'
        self.money = 20
        self.unsellableItems = [Item('Money', description=f'Amount-${self.money}'), ]

    def getList(self, inventoryItem):
        match inventoryItem.group:
            case 'fakemons':
                return self.fakemonsNotInUse
            case 'fakemonsInUse':
                return self.fakemonsInUse
            case 'items':
                return self.itemsNotInUse
            case _:
                return self.itemsInUse

    def swap(self, group, swapped: list):
        list1 = self.getList(swapped[0])
        list2 = self.getList(swapped[1])
        list1[swapped[0].index], list2[swapped[1].index] = list2[swapped[1].index], list1[swapped[0].index]
        if group == 'Fakemons':
            for i in swapped:
                if i.item == self.selectedFakemon:
                    self.selectedFakemon = self.fakemonsInUse[0]

    def updatePos(self, pos, location):
        self.pos = pos
        self.location = location

    def addItem(self, *items):
        for item in items:
            if type(item) == Item:
                self.unsellableItems.append(item)
            elif len(self.itemsInUse) == 4:
                self.itemsNotInUse.append(item)
            else:
                self.itemsInUse.append(item)

    def useFakeball(self, item: Fakeball, enemy):
        enemyFakemon = enemy.selectedFakemon
        if randint(1, 100) < (item.accuracy - enemyFakemon.evasion):
            self.addFakemon(enemyFakemon)
            enemy.fakemonsInUse.remove(enemyFakemon)
            enemy.changeSelectedFakemon()
            return f'You Caught {enemyFakemon.name}'
        return 'Your Fakeball Missed'

    def changeMoney(self, amount):
        self.money += amount
        self.unsellableItems[0].changeDescription(f'Amount-${self.money}')

    def completeGym(self, gymTextID):
        if gymTextID:
            self.read.append(gymTextID)
            self.level += 1

    def updateLists(self):
        super().updateLists()
        while True:
            if self.itemsNotInUse and len(self.itemsInUse) != 4:
                self.addItem(self.itemsNotInUse.pop(0))
            elif not self.itemsNotInUse or len(self.itemsInUse) == 4:
                break
        self.items = self.itemsInUse + self.itemsNotInUse


class TextBox(py.sprite.Sprite):

    def __init__(self, text='', *groups):
        super().__init__(*groups)
        self.ogImage = py.image.load(miscPath/'TextBox.png')
        self.image = self.ogImage.copy()
        self.rect = self.image.get_rect(topleft=(165, 470))
        self.text = []
        self.arrowPos = ((860, 170), (885, 200), (910, 170))
        for i in text.split('\n'):
            self.text.append(FONT.render(i, True, 'black'))

    def flip(self):
        self.image = self.ogImage.copy()

    def update(self, arrow=False):
        for i in range(len(self.text)):
            self.image.blit(self.text[i], (25, (i * 50) + 25))
        if arrow:
            py.draw.polygon(self.image, 'black', self.arrowPos)
            py.draw.aalines(self.image, 'black', True, self.arrowPos)


class State:

    def __init__(self, *states):
        self.states = states

    def update(self, win, dt):
        for state in self.states:
            state.update(win, dt)


class StateManager:

    def __init__(self, state, audioMixer):
        self.prevState = None
        self.state = state
        self.bgMusicStates = ['exploration', 'dialog', 'shop', 'hospital', 'inventory', 'pause']
        self.setState(state)
        self.states = None
        self.audioMixer = audioMixer

    def getState(self, category='class'):
        if category == 'class':
            if type(self.state) == tuple:
                return State(*[self.states[i] for i in self.state])
            else:
                return State(self.states[self.state])
        else:
            if type(self.state) == tuple:
                return self.state[1]
            return self.state

    def setState(self, state, *args):
        self.prevState = self.state[-1] if type(self.state) == tuple else self.state
        self.state = state
        if self.state == 'pause' or self.prevState == 'pause':
            self.audioMixer.playSound('pause')
        if self.state == 'battle':
            self.states['battle'].start(*args)
            self.audioMixer.playSound('fightStart')

        elif self.state != 'exploration':
            self.state = ('exploration', self.state)

        self.playBGmusic(state)

    def setAllStates(self, states: dict):
        self.states = states

    def playBGmusic(self, state):
        music = True
        state = state[-1] if type(state) == tuple else state

        if state == 'battle':
            py.mixer.music.load(AssetsPath/'Sounds'/'BattleMusic.mp3')
            py.mixer.music.set_volume(1)
            py.mixer.music.play(-1, 0.0, 3000)
        elif state == 'start':
            py.mixer.music.load(AssetsPath/'Sounds'/'startMusic.mp3')
            py.mixer.music.set_volume(1)
            py.mixer.music.play(-1, 0.0, 1000)
        elif state in self.bgMusicStates and self.prevState not in self.bgMusicStates:
            if self.prevState == 'battle' or 'start':
                py.mixer.music.fadeout(500)
            py.mixer.music.load(AssetsPath/'Sounds'/'bgMusic.mp3')
            py.mixer.music.set_volume(0.2)
            py.mixer.music.play(-1, 0.0, 3000)
        elif state in self.bgMusicStates:
            pass
        else:
            music = False

        if not music:
            py.mixer.music.fadeout(2000)


class Transition:

    def __init__(self, funcs, **kwargs):
        self.tintSpeed = 800
        self.funcs = funcs
        self.tint = 'tint'
        self.tintSurf = py.Surface((WIDTH, HEIGHT))
        self.tintPercent = 0
        self.props = kwargs
        self.completed = False

    def update(self, win, dt):
        if self.tint == 'untint':
            self.tintPercent -= self.tintSpeed * dt
            if self.tintPercent <= 0:
                self.completed = True

        if self.tint == 'tint':
            self.tintPercent += self.tintSpeed * dt
            if self.tintPercent >= 255:
                if type(self.funcs) == list:
                    for func in self.funcs:
                        func()
                else:
                    self.funcs()
                self.tint = 'untint'

        self.tintPercent = max(0, min(self.tintPercent, 255))
        self.tintSurf.set_alpha(self.tintPercent)
        win.blit(self.tintSurf, (0, 0))


class Controller:

    def __init__(self):
        self.controller = None
        self.controllerCheck()
        self.prevButtons = {'A': False, 'B': False, 'X': False, 'Pause': False}
        self.currButtons = {'A': False, 'B': False, 'X': False, 'Pause': False}
        self.axis = {'Left': False, 'Right': False, 'Up': False, 'Down': False}
        self.prevAxis = {'Left': False, 'Right': False, 'Up': False, 'Down': False}

    def __bool__(self):
        return bool(self.controller)

    def controllerCheck(self):
        if py.joystick.get_count() >= 1:
            self.controller: py.joystick.JoystickType = py.joystick.Joystick(0)
        else:
            self.controller = False

    def update(self):
        self.controllerCheck()
        self.prevButtons = self.currButtons.copy()
        self.currButtons = {
            'A': self.controller.get_button(0) if self.controller else False,
            'B': self.controller.get_button(1) if self.controller else False,
            'X': self.controller.get_button(2) if self.controller else False,
            'Pause': self.controller.get_button(4) or self.controller.get_button(6) if self.controller else False
        }
        self.prevAxis = self.axis
        self.axis = {'Left': False, 'Right': False, 'Up': False, 'Down': False}
        if self.controller:
            x = self.controller.get_axis(0)
            y = self.controller.get_axis(1)
            if x > 0.4:
                self.axis['Right'] = True
            elif x < -0.4:
                self.axis['Left'] = True
            if y > 0.4:
                self.axis['Down'] = True
            elif y < -0.4:
                self.axis['Up'] = True

    def getPressed(self, button):
        return self.currButtons[button] and not self.prevButtons[button]

    def getJoystick(self, direction):
        return self.axis[direction]

    def getJustJoystick(self, direction):
        return self.axis[direction] and not self.prevAxis[direction]


class AudioMixer:

    def __init__(self):
        self.soundfx = {
            'hit': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/hit.mp3'),
            'select': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/select.mp3'),
            'attack': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/attack.mp3'),
            'fightStart': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/fightStart.mp3'),
            'footsteps': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/footsteps.mp3'),
            'dialog': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/dialog.mp3'),
            'slideIn': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/slideIn.mp3'),
            'useItem': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/useItem.mp3'),
            'loadGame': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/loadGame.mp3'),
            'read': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/read.mp3'),
            'exit': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/exit.mp3'),
            'pause': py.mixer.Sound(r'/home/BrynM/Desktop/Code/Python/Fakemon/Assets/Sounds/pause.mp3')
        }
        self.soundfx['footsteps'].set_volume(0.2)
        self.soundfx['dialog'].set_volume(0.2)
        self.soundfx['read'].set_volume(0.5)

    def footstepVolInc(self, Up):
        if Up:
            self.soundfx['footsteps'].set_volume(0.5)
        else:
            self.soundfx['footsteps'].set_volume(0.2)

    def playSound(self, sound):
        self.soundfx[sound].play()


def join(iterable):
    temp = ''
    for i in iterable:
        temp += f'{i} '
    return temp


CONTROLLER = Controller()


def main():
    pass


if __name__ == '__main__':
    main()
