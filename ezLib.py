import pygame
import math
import random
import sys


def ezLib_init():
    pygame.init()

    if not pygame.mixer:
        print('Error mixer')
    else:
        pygame.mixer.pre_init(44100, -16, 4, 4096)

        pygame.mixer.init()

    print("init")


#################
class RecBound:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.xi = 0
        self.yi = 0
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.surface.fill((255, 0, 255))

    def inflate(self, xi, yi):
        self.xi = xi
        self.yi = yi
        self.rect.x += self.xi
        self.rect.y += self.yi
        self.rect.width = self.rect.width - 2*self.xi
        self.rect.height = self.rect.height - 2*self.yi

    def collides(self, targetRect):
        if self.rect.colliderect(targetRect):
            return True

        return False

    def update(self, xn, yn):
        self.rect.x = xn+self.xi
        self.rect.y = yn+self.yi

    def render(self, screen):
        screen.blit(surface, (self.rect.x, self.rect.y))
##################


class Entity:
    def __init__(self, xp, yp, image="None", width=50, height=50, color=(255, 0, 255)):
        self.x = xp
        self.y = yp

        self.dx = 0
        self.dy = 0

        self.state = ''

        self.recBound = None
        self.width = 0
        self.height = 0
        self.image = None
        self.color = color

        #
        if self.image == "None":
            print("none")
            self.image = pygame.Surface((width, height))
            self.image.fill(self.color)

            self.width = width
            self.height = height
            self.recBound = RecBound(xp, yp, self.width, self.height)

        else:
            self.image = image
            self.width, self.height = self.image.get_size()
            self.recBound = RecBound(xp, yp, self.width, self.height)

    def getLeft(self):
        return self.x

    def setLeft(self, left):
        self.x = left
        self.recBound.update(self.x, self.y)

    def getRight(self):
        return self.x + self.width

    def setRight(self, right):
        self.x = right - self.width
        self.recBound.update(self.x, self.y)

    def getTop(self):
        return self.y

    def setTop(self, top):
        self.y = top
        self.recBound.update(self.x, self.y)

    def getBottom(self):
        return self.y + self.height

    def setBottom(self, bottom):
        self.y = bottom - self.height
        self.recBound.update(self.x, self.y)

    def getCenterX(self):
        return self.x + self.width/2

    def setCenterX(self, center):
        self.x = center - self.width/2
        self.recBound.update(self.x, self.y)

    def getCenterY(self):
        return self.y + self.height/2

    def setCenterY(self, center):
        self.y = center - self.height/2
        self.recBound.update(self.x, self.y)

    def getCenter(self):
        xc = self.x+self.width/2
        yc = self.y+self.height/2
        return (xc, yc)

    def setCenter(self, xc, yc):
        self.x = xc-self.width/2
        self.y = yc-self.height/2
        self.recBound.update(self.x, self.y)

    def inflate(self, xi, yi):
        self.recBound.inflate(xi, yi)

    def collides(self, targetEntity):
        if self.recBound.collides(targetEntity.recBound):
            return True

        return False

    def update(self, dt):
        self.x += math.floor(self.dx*dt)
        self.y += math.floor(self.dy*dt)

        self.recBound.update(self.x, self.y)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def renderDebug(self, screen):
        self.recBound.render(screen)


##################


class StageManager:
    def __init__(self):
        self.tab = []
        self.current = None

    def pushStage(self, newstage):
        self.tab.append(newstage)
        self.current = self.tab[len(self.tab) - 1]
        self.current.onEnter()

    def popStage(self):
        del self.tab[len(self.tab) - 1]

    def changeStage(self, newstage=None, datas=None):
        if len(self.tab) > 0:
            self.current.onExit()
            del self.tab[len(self.tab) - 1]
            self.tab.append(newstage)
            self.current = self.tab[len(self.tab) - 1]
            self.current.onEnter(datas)

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    def render(self, screen):
        if self.current:
            self.current.render(screen)


##################
class InputManager:
    def __init__(self):
        self.tabKeyPressed = {}
        self.tabKeyReleased = {}

    def update(self):
        self.tabKeyPressed = {}
        self.tabKeyReleased = {}

    def setKeyboardPressed(self, key):
        self.tabKeyPressed[pygame.key.name(key)] = True

    def setKeyboardReleased(self, key):
        self.tabKeyReleased[pygame.key.name(key)] = True

    def isKeyPressed(self, key):
        return self.tabKeyPressed.get(pygame.key.name(key))

    def isKeyReleased(self, key):
        return self.tabKeyReleased.get(pygame.key.name(key))


###########
class Stage:
    def __init__(self, screenWidth, screenHeight):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        pass

    def onEnter(self, datas=None):
        pass

    def onExit(self):
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        pass
############


class AssetsManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}

    def loadImage(self, id, path):
        img = pygame.image.load(path)
        opaq = img.get_alpha()
        if opaq == None:
            img = img.convert()
        else:
            img = img.convert_alpha()

        self.images[id] = img

    def loadSound(self, id, path, volume):
        self.sounds[id] = pygame.mixer.Sound(path)
        self.sounds[id].set_volume(volume)

    def getImage(self, id):
        return self.images.get(id)

    def getSound(self, id):
        return self.sounds.get(id)

###########


class Game:

    def __init__(self, screenWidth, screenHeight, title="titre"):

        flags = pygame.SHOWN

        self.screen = pygame.display.set_mode(
            (screenWidth, screenHeight), flags, vsync=1)

        pygame.display.set_caption(title)

        self.inputManager = InputManager()

        self.stageManager = StageManager()

        self.assetsManager = AssetsManager()

        self.looping = True
        self.clock = pygame.time.Clock()
        self.stage = None
        self.fps = 30
        self.timer = 0
        self.compteur = 0

    def start(self):
        self.looping = True

        while self.looping:
            self.__mainLoop()

        print("pygame quit")
        pygame.quit()
        sys.exit()

    def __mainLoop(self):
        dt = self.clock.tick(self.fps) / 1000.0
        # affiche fps
        self.timer += dt
        self.compteur += 1
        if self.timer >= 1.0:
            self.timer = 0
            print("Fps= {}".format(self.compteur))
            self.compteur = 0
        # event
        for event in pygame.event.get():
            self.__doEvents(event)

            if event.type == pygame.QUIT:
                self.looping = False

        #
        self.__doUpdate(dt)

        self._doRender(self.screen)

    def __doEvents(self, event):
        if event.type == pygame.KEYDOWN:
            self.inputManager.setKeyboardPressed(event.key)

            if event.key == pygame.K_ESCAPE:
                self.looping = False

        if event.type == pygame.KEYUP:
            self.inputManager.setKeyboardReleased(event.key)

    def __doUpdate(self, dt):
        self.stageManager.update(dt)

        self.inputManager.update()

    def _doRender(self, screen):
        self.stageManager.render(screen)
        pygame.display.flip()

    def getInputManager(self):
        return self.inputManager

    def getStageManager(self):
        return self.stageManager

    def getAssetsManager(self):
        return self.assetsManager


###############
class Label():

    def __init__(self, fontName='None', size=30):

        self.text = "-"
        self.size = size
        self.image = None

        if fontName == 'None':
            self.font = pygame.font.SysFont(fontName, self.size, 0, 0)
        else:
            self.font = pygame.font.Font(fontName, self.size)

        self.color = (255, 255, 255)
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()

    def setColor(self, color):
        self.color = color

    def setText(self, text):
        self.text = text
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()

    def render(self, screen, xp, yp):
        self.rect.x = xp
        self.rect.y = yp
        screen.blit(self.image, self.rect)


###################
class ScoreManager():
    def __init__(self, screenWidth, screenHeight):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.name = 'name'
        self.points = 0
        self.lives = 3

        self.labelScore = Label('None', 50)

        self.labelName = Label('None', 50)

        self.color = (255, 255, 255)

    def isGameOver(self):
        if self.lives < 0:
            return True

        else:
            return False

    def getPoints(self):
        return self.points

    def incrementsPoints(self, amt):
        self.points += amt
        txt = "Score= {}".format(self.points)

        self.labelScore.setText(txt)

    def getLives(self):
        return self.lives

    def decrementsLives(self):
        self.lives -= 1

    def incrementsLives(self, amt):
        self.lives += amt

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name
        self.labelName.setText(self.name)

    def setColor(self, color):
        self.color = color
        self.labelName.setColor(color)
        self.labelName.setText(self.name)

        self.labelScore.setColor(color)
        txt = "Score= {}".format(self.points)
        self.labelScore.setText(txt)

    def drawLives(self, screen):
        if self.lives > 0:
            xp = self.screenWidth-100
            for i in range(self.lives):
                pygame.draw.circle(screen, self.color, (xp+25*i, 20), 10, 0)

    def render(self, screen):
        self.labelScore.render(screen, 10, 10)
        self.labelName.render(screen, self.screenWidth/2-50, 10)

        self.drawLives(screen)

##########


class Quad:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def affiche(self):
        print("x= {} y={}".format(self.x, self.y))

###############


class Animation:
    def __init__(self, atlas, spriteWidth, spriteHeight, duration=1/30, looping=False):
        self.atlas = atlas
        self.spriteWidth = spriteWidth
        self.spriteHeight = spriteHeight
        self.duration = duration
        self.looping = looping
        self.atlasWidth, self.atlasHeight = self.atlas.get_size()

        self.nbCols = math.floor(self.atlasWidth/self.spriteWidth)
        self.nbRows = math.floor(self.atlasHeight/self.spriteHeight)

        self.currentFrame = 0

        self.timer = 0
        self.go = False

        self.quads = []

        self.createQuads()

    def createQuads(self):
        for row in range(self.nbRows):
            for col in range(self.nbCols):
                self.quads.append(
                    Quad(col, row, self.spriteWidth, self.spriteHeight))

    def play(self):
        self.go = True

    def stop(self):
        self.go = False

    def isPlaying(self):
        return self.go

    def update(self, dt):
        if self.go and len(self.quads) > 1:
            self.timer += dt
            if self.timer > self.duration:
                self.timer = 0
                self.currentFrame += 1
                if self.currentFrame > len(self.quads)-1:
                    self.currentFrame = 0
                    if self.looping == False:
                        self.go = False

    def render(self, screen, xp, yp):
        quad = self.quads[self.currentFrame]

        offset = (quad.x * self.spriteWidth, quad.y * self.spriteWidth)

        size = (self.spriteWidth, self.spriteWidth)

        screen.blit(self.atlas, (xp, yp), (offset, size))

#############


class Particule:
    STATE_LIVE = 100
    STATE_DEAD = 200

    def __init__(self, x, y, width=10, color=(70, 70, 70, 250)):
        self.x = x
        self.y = y
        self.xi = x
        self.yi = y
        self.dx = 0
        self.dy = 0
        self.width = width
        self.color = color
        self.radius = self.width
        #self.image = pygame.Surface((self.width, self.width))
        #self.image.set_colorkey((0, 0, 0))
        # self.image.set_alpha(self.color[3])

        #pygame.draw.circle(self.image, self.color,(self.width/2, self.width/2), self.width/2)

        self.timer = 0
        self.live = random.random()*1
        self.state = Particule.STATE_LIVE

    def isDead(self):
        if self.state == Particule.STATE_DEAD:
            return True
        return False

    def move(self, xn, yn):
        self.xi = xn
        self.yi = yn

    def reset(self, xn, yn):
        self.xi = xn
        self.yi = yn
        self.x = self.xi
        self.y = self.yi

        self.timer = 0
        self.state = Particule.STATE_LIVE

        self.live = random.random()*1

    def setSpeed(self, module, angle):
        self.dx = math.floor(module*math.cos(angle))
        self.dy = math.floor(module*math.sin(angle))

    def update(self, dt):
        self.timer += dt
        self.radius -= 0.3

        self.x = self.x+self.dx*dt
        self.y = self.y+self.dy*dt

        if self.timer > self.live or self.radius <= 0:
            self.radius = self.width
            self.timer = 0
            self.state = Particule.STATE_DEAD

    def render(self, screen):
        if self.state == Particule.STATE_LIVE:
            pygame.draw.circle(screen, self.color,
                               (self.x, self.y), self.radius, width=0)
            #screen.blit(self.image, (self.x, self.y))


#######################


class ParticulesGenerator:
    def __init__(self, x, y, speedMin=100, speedMax=200, angleMin=170, angleMax=190):
        self.x = x
        self.y = y
        self.speedMin = speedMin
        self.speedMax = speedMax

        self.angleMin = angleMin
        self.angleMax = angleMax
        self.go = False

        self.particules = []

        self.create()

    def create(self):
        for i in range(100):
            self.particules.append(Particule(self.x, self.y))

            angleDeg = random.randrange(self.angleMin, self.angleMax)

            speed = random.randrange(self.speedMin, self.speedMax)

            angle = math.pi*angleDeg/180.0

            self.particules[i].setSpeed(speed, angle)

    def play(self):
        self.go = True

    def stop(self):
        self.go = False

    def move(self, xn, yn):
        self.x = xn
        self.y = yn

    def update(self, dt):
        for p in self.particules:
            p.update(dt)
            if p.isDead():
                p.reset(self.x, self.y)

    def render(self, screen):
        for p in self.particules:
            p.render(screen)
