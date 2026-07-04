import pygame as py
from pygame.constants import *

from fakemon_classes_n_funcs import Character, TextBox, Transition, Move, Fakeball, CONTROLLER, AudioMixer, Player
from fakemon_constants import FontPath, AssetsPath

py.font.init()
FONT1 = py.font.Font(FontPath, 45)
FONt2 = py.font.Font(FontPath, 100)
FONT3 = py.font.Font(FontPath, 70)
FONT4 = py.font.SysFont('arialblack', 25)

BattlePath = AssetsPath / 'Battle'

class FakemonSprite(py.sprite.Sprite):

    def __init__(self, fakemon, *groups):
        super().__init__(*groups)
        self.ogImage: py.Surface = fakemon.getImage('Battle')
        self.blankImg = py.image.load(BattlePath/'FakemonSprites'/'Blank.png')
        self.image = self.ogImage.copy()
        self.rect = self.image.get_frect()
        self.fakemon = fakemon
        self.animation = ''
        self.count = 0

    def update(self, *args, **kwargs):

        if self.animation == 'damage':
            if self.count == 0:
                self.count = 100
            elif self.count == 1:
                self.image = self.ogImage.copy()
                self.animation = ''
                self.count -= 1
            else:
                self.count -= 1
                if self.count % 24 == 0:
                    self.image = self.blankImg.copy()
                elif self.count % 12 == 0:
                    self.image = self.ogImage.copy()
        else:
            self.animation = self.fakemon.getAnimation()


class HealthBar(py.sprite.Sprite):

    def __init__(self, fakemon, *groups):
        super().__init__(*groups)
        self.ogImage = py.image.load(BattlePath/'HealthBarSurf.png').convert_alpha()
        self.image = self.ogImage.copy()
        self.rect = self.image.get_frect()
        self.fakemon = fakemon
        self.fakemonPercentage = self.fakemon.getHealth('p')
        self.healthDir = ''

        self.showHealth()

    def showHealth(self):
        self.image = self.ogImage.copy()
        py.draw.rect(self.image, 'red', (8, 50, 165, 25), border_radius=5)
        py.draw.rect(self.image, 'green', (8, 50, 165 * self.fakemonPercentage, 25), border_radius=5)
        healthText = FONT1.render(f'{int(self.fakemon.getHealth('a'))}/{self.fakemon.getHealth('t')}', True, 'black')
        nameText = FONT1.render(self.fakemon.getDetails(), True, 'black')
        self.image.blit(nameText, (15, 10))
        self.image.blit(healthText, (180, 45))

    def update(self, dt):
        fakemonPercentage = self.fakemon.getHealth('p')
        if self.fakemonPercentage != fakemonPercentage:
            if self.fakemonPercentage > fakemonPercentage and not self.healthDir:
                self.healthDir = '-'
            elif self.fakemonPercentage < fakemonPercentage and not self.healthDir:
                self.healthDir = '+'

            if self.healthDir == '-':
                self.fakemonPercentage -= dt * 2
                if self.fakemonPercentage <= fakemonPercentage:
                    self.fakemonPercentage = fakemonPercentage
                    self.healthDir = ''
            elif self.healthDir == '+':
                self.fakemonPercentage += dt * 2
                if self.fakemonPercentage >= fakemonPercentage:
                    self.fakemonPercentage = fakemonPercentage
                    self.healthDir = ''

            self.showHealth()


class BattlePart:

    def __init__(self, char: Character):
        self.char = char
        self.fakemon = char.selectedFakemon
        self.group = py.sprite.Group()
        self.fakemonSprite = FakemonSprite(self.fakemon, self.group)
        self.health = HealthBar(self.fakemon, self.group)
        self.setPosOfSprites()

    def slideIn(self, dt):
        speed = 650 * dt
        if self.fakemon.owner == 'player':
            velocity = speed
            pos = 380
            if self.fakemonSprite.rect.centerx <= pos:
                self.fakemonSprite.rect.centerx += velocity
                self.health.rect.centerx += velocity
                return False
            return True
        else:
            velocity = -speed
            pos = 900
            if self.fakemonSprite.rect.centerx >= pos:
                self.fakemonSprite.rect.centerx += velocity
                self.health.rect.centerx += velocity
                return False
            return True

    def setPosOfSprites(self):
        if self.fakemon.owner == 'player':
            self.fakemonSprite.rect.midbottom = (-150, 470)
            self.health.rect.center = (-150, 100)
        else:
            self.fakemonSprite.rect.center = (1450, 300)
            self.health.rect.center = (1450, 100)

    def update(self, win, dt, audioMixer):
        if self.char.selectedFakemon != self.fakemon:
            self.group.empty()
            self.fakemon = self.char.selectedFakemon
            if self.fakemon:
                self.fakemonSprite = FakemonSprite(self.fakemon, self.group)
                self.health = HealthBar(self.fakemon, self.group)
                self.setPosOfSprites()

        if self.fakemon:
            if self.slideIn(dt):
                self.group.update(dt)
            else:
                if not py.mixer.get_busy():
                    audioMixer.playSound('slideIn')
            self.group.draw(win)


class Options(TextBox):

    def __init__(self, player: Player, audioMixer: AudioMixer, option='start', *groups):
        super().__init__('', *groups)

        self.player = player
        self.option = option
        self.audioMixer = audioMixer
        self.end = False
        font = FONT3
        extraInfo = []
        col = ['Black'] * 4
        match option:
            case 'start':
                self.options = ('Fight', 'Fakemons', 'Items', 'Run')
                font = FONt2
            case 'Fight':
                self.options = [move for move in player.selectedFakemon.moves.keys()]
                extraInfo = [move.getInfo() for move in player.selectedFakemon.moves.values()]
            case 'Items':
                self.options = [item.name for item in player.itemsInUse if item]
                extraInfo = [item.getInfo() for item in player.itemsInUse]
            case 'Fakemons':
                col = []
                self.options = [fakemon.name for fakemon in player.fakemonsInUse if fakemon]
                self.IDS = [fakemon.getHealth('') for fakemon in player.fakemonsInUse if fakemon]
                for fakemon in player.fakemonsInUse:
                    if fakemon.getHealth('') == 0:
                        col.append('Dark Red')
                    else:
                        col.append('Black')
                extraInfo = [fakemon.getInfo() for fakemon in player.fakemonsInUse if fakemon]
            case _:
                self.options = []
                self.end = True

        self.cursorIndex = [0, 0]
        self.textPositions = ((75, 20), (75, 145), (575, 20), (575, 145))
        self.infoPos = ((75, 60), (75, 185), (575, 60), (575, 185))
        self.cursorPos = None

        self.texts = []
        for option, color in zip(self.options, col):
            self.texts.append(
                font.render(option, False, color)
            )
        self.info = []
        for info, color in zip(extraInfo, col):
            self.info.append(
                FONT4.render(info, True, color)
            )

        self.emptyText = font.render('EMPTY', False, 'Black')

    def getOption(self):
        if self.end:
            return self.option
        return False

    def getCursorIndex(self):
        return self.cursorIndex[0] + (self.cursorIndex[1] * 2)

    def drawCursor(self):
        try:
            self.cursorPos = self.getCursorPos(tuple(zip(self.options, self.textPositions))[self.getCursorIndex()][1])
        except IndexError:
            pass
        py.draw.polygon(self.image, 'black', self.cursorPos)
        py.draw.aalines(self.image, 'black', True, self.cursorPos)

    def InOutOfOptions(self):
        keys = py.key.get_just_pressed()
        if (keys[K_RETURN] or CONTROLLER.getPressed('A')) and self.options:
            index = self.getCursorIndex()
            self.audioMixer.playSound('select')
            if self.option == 'Fakemons':
                option = self.options[index], self.IDS[index]
            else:
                option = self.options[index]
            Options(self.player, self.audioMixer, option, self.groups())
            self.kill()
        if keys[K_ESCAPE] or CONTROLLER.getPressed('B'):
            self.audioMixer.playSound('exit')
            Options(self.player, self.audioMixer, 'start', self.groups())

    @staticmethod
    def getCursorPos(pos):
        return ((pos[0] - 35, pos[1] + 10),
                (pos[0] - 5, pos[1] + 35),
                (pos[0] - 35, pos[1] + 60))

    def cursorMovement(self):
        keys = py.key.get_pressed()
        if (keys[K_w] or CONTROLLER.getJoystick('Up')) and self.cursorIndex[0] != 0:
            self.cursorIndex[0] -= 1
        if (keys[K_s] or CONTROLLER.getJoystick('Down')) and self.cursorIndex[0] != 1 and (
                len(self.options) > 3 or self.cursorIndex[1] == 0):
            self.cursorIndex[0] += 1
        if (keys[K_a] or CONTROLLER.getJoystick('Left')) and self.cursorIndex[1] != 0:
            self.cursorIndex[1] -= 1
        if (keys[K_d] or CONTROLLER.getJoystick('Right')) and self.cursorIndex[1] != 1 and (
                (len(self.options) > 3 or self.cursorIndex[0] == 0) and len(self.options) > 2):
            self.cursorIndex[1] += 1
        self.InOutOfOptions()
        if self.options:
            self.drawCursor()

    def update(self):
        self.flip()
        if self.options:
            for i in zip(self.texts, self.textPositions):
                self.image.blit(*i)
            for i in zip(self.info, self.infoPos):
                self.image.blit(*i)
        else:
            self.image.blit(self.emptyText, self.textPositions[0])
        self.cursorMovement()


class Battle:

    def __init__(self, stateManager, game, audioMixer):
        self.stateManager = stateManager
        self.game = game
        self.audioMixer = audioMixer

    def start(self, player: Player, enemy: Character, reward=7, gym=''):
        self.quitAfterInfo = False
        self.bg = py.image.load(BattlePath/'fightBackground.png').convert_alpha()
        self.count = 0
        self.quit = False
        self.turn = True
        self.repeatTurn = False
        self.info = False
        self.choice = False
        self.check = [False, True]
        self.player = player
        self.enemy = enemy
        self.mySide = BattlePart(player)
        self.theirSide = BattlePart(enemy)
        self.optionsBar = py.sprite.GroupSingle()
        self.optionsBar.add(Options(self.player, self.audioMixer))
        self.reward = reward
        self.gym = gym

    def aiTurn(self, win):
        if self.count == 0:

            moveChoice = ['', 0]
            temp: dict[str, Move] = self.enemy.selectedFakemon.moves
            for move in temp.keys():
                if temp[move].effect > moveChoice[1]:
                    moveChoice = [move, temp[move].effect]
            self.optionsBar.add(
                TextBox(self.enemy.selectedFakemon.performMove(moveChoice[0], self.mySide.fakemon, self.audioMixer)))
            self.count = 200

        elif self.count == 1:

            self.optionsBar.empty()
            self.optionsBar.add(Options(self.player, self.audioMixer))
            self.turn = True
            self.check = [True, False]
            self.count -= 1

        else:
            self.count -= 1
            self.optionsBar.update()
            self.optionsBar.draw(win)

    def playerTurn(self, win):
        if not self.choice:
            if self.count == 0:
                self.choice = self.optionsBar.sprite.getOption()
            elif self.count == 1:
                self.optionsBar.empty()
                if self.repeatTurn:
                    self.optionsBar.add(Options(self.player, self.audioMixer))
                    self.turn = True
                else:
                    self.turn = False
                self.check = [True, False]
                self.count -= 1
            else:
                self.count -= 1
            self.optionsBar.update()
            self.optionsBar.draw(win)

        else:
            self.optionsBar.empty()
            if type(self.choice) != tuple:
                if self.choice in self.player.selectedFakemon.moveNames:
                    self.optionsBar.add(
                        TextBox(self.player.selectedFakemon.performMove(self.choice, self.theirSide.fakemon,
                                                                        self.audioMixer)))
                    self.count = 200
                    self.repeatTurn = self.player.selectedFakemon.moveType(self.choice,
                                                                           'Defend') and not self.repeatTurn


                elif self.choice == 'Run':
                    self.quit = True
                else:
                    for item in self.player.itemsInUse:
                        if self.choice == item.name:
                            if type(item) == Fakeball and self.enemy.selectedFakemon.name != 'Rayquaza':
                                self.optionsBar.add(
                                    TextBox(self.player.useFakeball(item, self.enemy)))
                                self.count = 200
                            else:
                                self.audioMixer.playSound('useItem')
                                self.player.selectedFakemon.useItem(item)
                            self.player.itemsInUse.remove(item)
                            break
            else:
                for fakemon in self.player.fakemonsInUse:
                    if self.choice[0] == fakemon.name and self.choice[1] == fakemon.getHealth(''):
                        self.player.changeSelectedFakemon(fakemon)
                        break

            if not self.count:
                self.optionsBar.add(Options(self.player, self.audioMixer))

            self.choice = False

    def checkIfDefeated(self):

        if self.check[0]:
            deadFakemon = [self.player.getFreshlyDead(), self.enemy.getFreshlyDead()]
            if deadFakemon[0]:
                self.displayInfo(None, False, f"Player's Fakemon {deadFakemon[0].name} has Fainted")
            if deadFakemon[1]:
                self.displayInfo(None, False, f"Enemy's Fakemon {deadFakemon[1].name} has Fainted")
            self.check = [False, True]
        else:
            self.check = [False, False]
            temp = self.enemy.checkIfFainted()
            if self.player.checkIfFainted():
                self.count = 0
                self.displayInfo(None, True, 'Player Has Lost')
            elif temp:
                self.count = 0
                self.displayInfo(None, True, 'Player Has WON')
                if temp != 'x':
                    self.player.changeMoney(self.reward)
                    self.player.completeGym(self.gym)

    def displayInfo(self, win, quitGame=False, text=''):
        if self.count == 0:
            self.quitAfterInfo = quitGame
            self.optionsBar.add(TextBox(text))
            self.count = 200
            self.info = True
        elif self.count == 1:
            self.optionsBar.empty()
            self.count -= 1
            if self.quitAfterInfo:
                self.quit = True
            else:
                self.optionsBar.add(Options(self.player, self.audioMixer))
                self.info = False
        else:
            self.count -= 1
            self.optionsBar.update()
            self.optionsBar.draw(win)

    def update(self, win, dt):
        if not self.quit:
            win.blit(self.bg, (0, 0))
            self.mySide.update(win, dt, self.audioMixer)
            self.theirSide.update(win, dt, self.audioMixer)

            self.enemy.updateLists()
            self.player.updateLists()
            if self.info:
                self.displayInfo(win)
            elif not any(self.check):
                if self.turn:
                    self.playerTurn(win)
                else:
                    self.aiTurn(win)
            else:
                self.checkIfDefeated()
        else:
            if not self.game.transition:
                self.game.transition = Transition(lambda: self.stateManager.setState('exploration'))
