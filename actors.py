
from ezLib import *

import random
import math

#####################


class Plane(Entity):
    STATE_IDLE = 10
    STATE_LIVE = 20
    STATE_TOUCHED = 30

    def __init__(self, screenWidth, screenHeight, xp, yp, textures):
        #Entity.__init__(self, xp, yp, textures["plane"])
        super().__init__(xp, yp, textures["plane"])

        self.flying = Animation(textures['flying'], 90, 75, 0.033, True)
        self.flying.play()

        self.gaz = ParticulesGenerator(xp, yp)
        self.gaz.play()

        self.explosion = Animation(textures['explosion'], 102, 102)

        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.label = Label("None", 40)
        self.label.setColor((50, 50, 50))
        self.label.setText(("Press Space Bar"))

        self.posInit = (xp, yp)

        self.state = Plane.STATE_IDLE
        self.gravity = 10
        self.inflate(5, 5)

    def pushUp(self):
        if self.state == Plane.STATE_IDLE:
            self.state = Plane.STATE_LIVE

        if self.state == Plane.STATE_LIVE:
            self.dy = -self.gravity/2

    def reset(self):
        self.x = self.posInit[0]
        self.y = self.posInit[1]
        self.state = Plane.STATE_IDLE
        self.dx = 0
        self.dy = 0

    def touched(self):
        if self.state == Plane.STATE_LIVE:
            self.state = Plane.STATE_TOUCHED
            self.dx = 0
            self.dy = 0
            self.explosion.play()

    def update(self, dt):
        Entity.update(self, dt)

        self.flying.update(dt)

        self.gaz.move(self.x, self.y+20)
        self.gaz.update(dt)

        if self.state == Plane.STATE_LIVE:
            self.dy += self.gravity*dt
            self.y += self.dy

        self.explosion.update(dt)

        if self.state == Plane.STATE_TOUCHED and self.explosion.isPlaying() == False:
            self.reset()

        # limites
        if self.getBottom() > self.screenHeight:
            self.setBottom(self.screenHeight)

        if self.getTop() < 0:
            self.setTop(0)

    def render(self, screen):
        #Entity.renderDebug(self, screen)
        #Entity.render(self, screen)

        if self.state == Plane.STATE_IDLE or self.state == Plane.STATE_LIVE:
            self.gaz.render(screen)

            self.flying.render(screen, self.x, self.y)

        if self.state == Plane.STATE_TOUCHED:
            self.explosion.render(screen, self.x, self.y)

        if self.state == Plane.STATE_IDLE:
            self.label.render(screen, self.screenHeight/2, self.screenHeight/2)

##################


class Paysage():
    def __init__(self, screenWidth, screenHeight, image):
        self.image = image
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.x = 0
        self.y = 0
        self.dx = 20

    def update(self, dt):
        self.x -= self.dx*dt

        if self.x < -self.screenWidth:
            self.x = 0

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))


###################
class Rock(Entity):

    def __init__(self, screenWidth, screenHeight, type, image):
        #Entity.__init__(self, 0, 0, image)
        super().__init__(0, 0, image)
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.type = type

        self.dx = -350
        self.dy = 0

        self.inflate(0, 20)

        if self.type == "UP":
            self.setTop(0)
            self.setLeft(0)

        elif self.type == "DOWN":
            self.setBottom(self.screenHeight)
            self.setLeft(0)

    def update(self, dt):
        Entity.update(self, dt)

        if self.getRight() < self.screenWidth:
            self.setLeft(0)

    def render(self, screen):
        #Entity.renderDebug(self, screen)
        Entity.render(self, screen)

#####################


class Pillar(Entity):

    def __init__(self, screenWidth, screenHeight, type, image):
        #Entity.__init__(self, 0, 0, image)
        super().__init__(0, 0, image)
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.type = type
        self.touchLeft = False
        self.inflate(30, 20)

        if type == "UP":
            self.setLeft(self.screenWidth)

        elif type == "DOWN":
            self.setLeft(self.screenWidth)
            self.setBottom(self.screenHeight)

    def reset(self):
        self.touchLeft = False
        self.dx = 0
        self.setLeft(self.screenWidth)

    def move(self, speed):
        self.dx = -speed

    def isTouchLeft(self):
        return self.touchLeft

    def update(self, dt):
        Entity.update(self, dt)

        if self.getRight() < 0:
            self.touchLeft = True

    def render(self, screen):
        #Entity.renderDebug(self, screen)
        Entity.render(self, screen)


###############


class Pillars():

    def __init__(self, screenWidth, screenHeight, img_pillar_up, img_pillar_down):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.speed = 300

        self.pillar_up = Pillar(screenWidth, screenHeight,
                                "UP", img_pillar_up)

        self.pillar_down = Pillar(
            screenWidth, screenHeight, "DOWN", img_pillar_down)

        self.winPoint = False

        self.newWave()

    def isWinPoint(self):
        return self.winPoint

    def newWave(self):
        self.reset()
        self.action()

    def action(self):
        val = random.randint(0, 10)
        self.winPoint = False

        if val < 5:
            self.pillar_down.move(self.speed)
        else:
            self.pillar_up.move(self.speed)

    def reset(self):
        self.pillar_down.reset()
        self.pillar_up.reset()

    def isCollideWithPlane(self, plane):
        if plane.state == Plane.STATE_LIVE:
            if self.pillar_down.collides(plane) or self.pillar_up.collides(plane):
                self.reset()
                self.action()
                return True
        return False

    def update(self, dt):
        self.pillar_down.update(dt)
        self.pillar_up.update(dt)

        if self.pillar_down.isTouchLeft() or self.pillar_up.isTouchLeft():
            self.winPoint = True

    def render(self, screen):
        self.pillar_up.render(screen)
        self.pillar_down.render(screen)
