from itertools import cycle
from os import listdir
from pathlib import Path
from random import randint, choices

import pygame as py
from numpy.random import choice
from pygame.constants import *
from pygame.math import Vector2 as vect
from pytmx.util_pygame import load_pygame
from itertools import chain

from fakemon_classes_n_funcs import Character, Transition, Fakemon, CONTROLLER, Player
from fakemon_constants import fakemon_locations, AssetsPath

base_path = AssetsPath / 'Exploration'

class Group(py.sprite.Group):

    def __init__(self):
        super().__init__()
        self.offset = vect()
        self.halfScreenSize = [i // 2 for i in py.display.get_window_size()]
        self.bg = None
        self.char = None

    def addBg(self, group):
        self.bg = group

    def camera(self, target):
        self.offset = vect(target.rect.center) - self.halfScreenSize
        self.offset.x = round(self.offset.x)
        self.offset.y = round(self.offset.y)

    def cDraw(self, win, target):
        self.camera(target)
        for bg in self.bg:
            win.blit(bg.image, bg.rect.topleft - self.offset)

        for spr in sorted(self.sprites(), key=lambda sprite: sprite.ySort):
            win.blit(spr.image, spr.rect.topleft - self.offset)


class Tile(py.sprite.Sprite):

    def __init__(self, pos, image, group, properties=None, overlapOffset=0):
        super().__init__(group)
        self.image = image
        self.properties = properties
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox = self.rect.copy()
        self.ySort = self.rect.centery - overlapOffset


class CollisionTile(Tile):

    def __init__(self, pos, image, group, properties, overlapOffset=0, xhitBox=0.1, yhitBox=0.99):
        super().__init__(pos, image, group, properties, overlapOffset)
        self.hitbox = self.rect.inflate(self.rect.width * -xhitBox, self.rect.height * -yhitBox)


class PlayerSprite(py.sprite.Sprite):

    def __init__(self, player: Player, walls, audioMixer, *groups):
        super().__init__(*groups)
        self.player = player
        pos = self.player.pos

        directory = base_path / 'Character'
        self.images = {'front': dict(), 'left': dict(), 'right': dict(), 'back': dict()}
        for file, type, i in zip(listdir(directory), cycle((1, 'idle', 2)), range(12)):
            self.images[tuple(self.images.keys())[i // 3]].update(
                {type: py.transform.scale_by(py.image.load(f'{directory}/{file}').convert_alpha(), 2)})

        self.facing = 'front'

        self.animationCount = 0
        self.image = self.images[self.facing]['idle']
        self.rect = self.image.get_frect(center=pos)

        self.hitBox = self.rect.inflate(-40, -40)

        self.direction = vect((0, 0))
        self.walls = walls
        self.cooldown = 0
        self.dt = None
        self.ySort = self.rect.centery
        self.audioMixer = audioMixer

    def collisionCheck(self, axis):
        for wall in py.sprite.spritecollide(self, self.walls, False):
            if wall.hitbox.colliderect(self.hitBox):
                if axis == 'x':
                    if self.direction.x > 0:
                        self.hitBox.right = wall.hitbox.left
                    elif self.direction.x < 0:
                        self.hitBox.left = wall.hitbox.right
                    self.rect.centerx = self.hitBox.centerx
                elif axis == 'y':
                    if self.direction.y > 0:
                        self.hitBox.bottom = wall.hitbox.top
                    elif self.direction.y < 0:
                        self.hitBox.top = wall.hitbox.bottom
                    self.rect.centery = self.hitBox.centery

    def input(self):
        keys = py.key.get_pressed()
        inputDir = vect()
        if keys[K_w] or CONTROLLER.getJoystick('Up'):
            inputDir.y = -1
            self.facing = 'back'
        if keys[K_s] or CONTROLLER.getJoystick('Down'):
            inputDir.y = 1
            self.facing = 'front'
        if keys[K_a] or CONTROLLER.getJoystick('Left'):
            inputDir.x = -1
            self.facing = 'left'
        if keys[K_d] or CONTROLLER.getJoystick('Right'):
            inputDir.x = 1
            self.facing = 'right'
        if inputDir:
            inputDir.normalize_ip()
            if not py.mixer.get_busy():
                self.audioMixer.playSound('footsteps')
        self.direction = inputDir

    def walk(self):
        speed = 600  # 300
        self.input()
        self.rect.centerx += self.direction.x * speed * self.dt
        self.hitBox.centerx = self.rect.centerx
        self.collisionCheck('x')
        self.rect.centery += self.direction.y * speed * self.dt
        self.hitBox.centery = self.rect.centery
        self.collisionCheck('y')

    def animate(self):
        if self.direction:
            self.animationCount += 8 * self.dt
            order = (1, 'idle', 2, 'idle')
            if self.animationCount >= 3:
                self.animationCount = 0

            self.image = self.images[self.facing][order[round(self.animationCount)]]

        else:
            self.animationCount = 0
            self.image = self.images[self.facing]['idle']

    def resetWalls(self, walls):
        self.walls = walls

    def update(self, dt):
        self.dt = dt
        self.ySort = self.rect.centery
        self.walk()
        self.animate()


class Camera:               #Begining camera used for intro

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rect = py.Rect(randint(0, self.width - 500), randint(0, self.height - 500), 500, 500)
        self.vel = vect(1, 1)

    def update(self, dt):
        speed = 100
        if self.rect.left <= 0:
            self.vel.x = 1
        elif self.rect.right >= self.width:
            self.vel.x = -1
        if self.rect.top <= 0:
            self.vel.y = 1
        elif self.rect.bottom >= self.height:
            self.vel.y = -1

        self.rect.center += round(self.vel * dt * speed)


class ExploreMode:

    def __init__(self, stateManager, game, audioMixer):
        self.stateManager = stateManager
        self.allSprites = Group()
        self.maps = {
            'main': base_path / 'fakemonTileMap.tmx',
            'Start House': base_path / 'startHouse.tmx',
            'stanleysHouse': base_path / 'stanleyshouse.tmx',
            'shop': base_path / 'shop.tmx',
            'hospital': base_path / 'hospital.tmx',
            'SnowGym': base_path / 'SnowGym.tmx',
            'BeachGym': base_path / 'BeachGym.tmx',
            'JungleGym': base_path / 'JungleGym.tmx',
            'EndHouse': base_path / 'EndHouse.tmx',
            'Benjishouse': base_path / 'Benjishouse.tmx',
            'HenrysHouse': base_path / 'HenrysHouse.tmx',
            'MrWsHouse': base_path / 'MrWsHouse.tmx',
        }

        self.loadMap('main')

        width, height = self.tileMap.width * 64, self.tileMap.height * 64
        self.randCam = Camera(width, height)
        self.game = game
        self.audioMixer = audioMixer
        self.cooldown = 0
        self.reading = None

    def loadMap(self, map):
        self.map = map
        self.allSprites.empty()
        self.tileMap = load_pygame(self.maps[map])

        self.bgTiles = self.addTilesToGroup('below')
        self.objTiles, self.borders, self.transitionTiles, self.regions, self.dialogTiles = self.addObjToGroup()
        self.grassTiles = self.addTilesToGroup('grass')
        self.collisionTiles = self.addTilesToGroup('collision')

        self.wallTiles = py.sprite.Group(self.objTiles, self.collisionTiles, self.borders)

        self.allSprites.addBg(self.bgTiles)
        self.allSprites.add(self.addTilesToGroup(None), self.objTiles, self.collisionTiles, self.grassTiles)

    def addTilesToGroup(self, layerGroup):
        group = py.sprite.Group()
        for layer in self.tileMap.layers:
            if layerGroup == 'collision':
                tile = CollisionTile
            else:
                tile = Tile
            if layer.name == 'overlap':
                offset = 30
            elif layer.name == 'decoration':
                offset = 30
            elif layer.name == 'trim':
                offset = -90000
            else:
                offset = 0
            if layer.properties['group'] == layerGroup:
                for x, y, surf in layer.tiles():
                    tile((x * 64, y * 64), surf, group, None, offset)
        return group

    def addObjToGroup(self):
        visibleGroup = py.sprite.Group()
        borders = py.sprite.Group()
        transition = py.sprite.Group()
        regions = py.sprite.Group()
        dialog = py.sprite.Group()
        for obj in self.tileMap.objects:
            if obj.image:
                try:
                    size = [float(i) for i in obj.properties['hitbox'].split(',')]
                except KeyError:
                    size = (0.5, 0.6)

                offset = obj.properties.setdefault('offset', 0)

                x = round(obj.x)
                y = round(obj.y)
                CollisionTile((x, y), obj.image, visibleGroup, None, offset, *size)
            else:
                if 'dest' in obj.properties:
                    group = transition
                elif 'text' in obj.properties:
                    group = dialog
                elif obj.properties:
                    group = regions
                else:
                    group = borders
                Tile((obj.x, obj.y), py.Surface((obj.width, obj.height)), group, obj.properties)

        return visibleGroup, borders, transition, regions, dialog

    def createChar(self, player: Player):
        self.loadMap(player.location)
        self.player = PlayerSprite(player, self.wallTiles, self.audioMixer)
        self.allSprites.add(self.player)

    def reposChar(self, pos):
        pos = [int(i) for i in pos.split(',')]
        self.player.rect.center = pos
        self.player.hitBox.center = pos
        self.player.resetWalls(self.wallTiles)
        self.allSprites.add(self.player)

    def transitionCheck(self):
        collide = self.player.hitBox.colliderect
        transitionTiles = [sprite for sprite in self.transitionTiles if collide(sprite.rect)]
        grassTiles = [sprite for sprite in self.grassTiles if collide(sprite.rect)]
        regions = [region for region in self.regions if collide(region.rect)]
        if transitionTiles:
            props: dict = transitionTiles[0].properties
            try:
                requ = props['requirements']
            except KeyError:
                loadMap = True
            else:
                for item in self.player.player.unsellableItems:
                    if item.name == requ:
                        loadMap = True
                        break
                else:
                    loadMap = False
                    ID = -1
                    if ID != self.reading:
                        self.game.dialog.addText([props['reject text']])
                        self.reading = ID
            if props.setdefault('level', 0) > self.player.player.level:
                loadMap = False
                ID = -1
                if ID != self.reading:
                    self.game.dialog.addText([props['reject text']])
                    self.reading = ID

            if loadMap:
                funcs = [lambda: self.loadMap(props['dest']), lambda: self.reposChar(props['pos'])]
                if not self.game.transition:
                    self.game.transition = Transition(funcs)
        else:
            self.reading = None
            if grassTiles:
                self.audioMixer.footstepVolInc(True)
                if choice((True, False), 1, p=(0.01, 0.99)) and not self.cooldown:

                    try:
                        region = regions[0].properties['region']
                    except IndexError:
                        region = 'plain'
                    enemyFakemons = []

                    for i in range(choice([1, 2], p=[0.75, 0.25])):
                        fakemonName = choice(fakemon_locations[region])
                        enemyFakemons.append(
                            Fakemon(fakemonName, 'them', fakemonName))
                    print(enemyFakemons)
                    self.cooldown = 1000
                    self.game.transition = Transition(
                        lambda: self.stateManager.setState('battle', self.player.player,
                                                           Character(*enemyFakemons)))
            else:
                self.audioMixer.footstepVolInc(False)

    def dialogCheck(self):
        collide = self.player.hitBox.colliderect
        dialogTiles = [tile for tile in self.dialogTiles if collide(tile.rect)]
        if dialogTiles:

            dialogData: dict = dialogTiles[-1].properties

            autoRead = dialogData.setdefault('auto', False)
            ID = dialogData.setdefault('iD', 0)

            if (py.key.get_just_pressed()[py.K_RETURN] or autoRead or CONTROLLER.getPressed(
                    'A')) and ID not in self.player.player.read and ID != self.reading:
                text = dialogData['text'].split(',')

                if not autoRead:
                    self.audioMixer.playSound('dialog')
                if dialogData.setdefault('kill', False):
                    dialogTiles[-1].kill()
                    self.player.player.read.append(dialogData['iD'])

                state = dialogData.setdefault('state', 'exploration')
                self.reading = ID
                if state == 'battle':
                    numOfEnemies = 3 if dialogData['area'] == 'snowy' or dialogData['area'] == 'all' else 4
                    region = dialogData['area']
                    enemyFakemons = []
                    fakemonNames = []
                    if region != 'all':
                        fakemonNames = choices(fakemon_locations[region], k=numOfEnemies)
                    else:
                        fakemonNames = ['Rayquaza'] + choices(
                            list(chain.from_iterable(fakemon_locations.values())), k=numOfEnemies)

                    enemyFakemons = [Fakemon(fakemon, 'them', fakemon) for fakemon in fakemonNames]

                    args = (self.player.player, Character(*enemyFakemons), numOfEnemies * 10, ID)
                else:
                    args = ()

                self.game.dialog.addText(text, state, args)
            elif ID in self.player.player.read:
                dialogTiles[-1].kill()

        elif self.reading != -1:
            self.reading = None

    def update(self, win, dt):
        state = self.stateManager.getState('str')
        if state == 'exploration':
            self.transitionCheck()
            self.dialogCheck()
            self.allSprites.update(dt)

        if state == 'start' or self.game.prevState == 'start':
            self.allSprites.update(dt)
            self.allSprites.cDraw(win, self.randCam)
            self.randCam.update(dt)
        else:
            self.allSprites.cDraw(win, self.player)
            if self.cooldown != 0:
                self.cooldown -= 1
