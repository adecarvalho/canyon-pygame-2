"""Canyon game"""

from ezLib import *
from actors import *

#global variables
screenWidth = 800
screenHeight = 480

ezLib_init()
game = Game(screenWidth, screenHeight, "Canyon-2K21.py")

#####################


class IntroStage(Stage):

    def __init__(self, screenWidth, screenHeight):
        #Stage.__init__(self, screenWidth, screenHeight)
        super().__init__(screenWidth, screenHeight)

        self.img = game.getAssetsManager().getImage("paysage")

        pygame.mixer.music.load('./assets/musics/underground.ogg')
        pygame.mixer.music.set_volume(0.4)

        self.labelTitle = Label("./assets/fonts/free.ttf", 70)
        self.labelTitle.setColor((200, 20, 200))
        self.labelTitle.setText(("Canyon"))

        self.labelCom = Label()
        self.labelCom.setColor((200, 20, 200))
        self.labelCom.setText(("Press space to start ..."))

        self.labelName = Label("./assets/fonts/free.ttf", 50)
        self.labelName.setColor((200, 20, 200))
        self.labelName.setText("AAA")

        self.tab = [65, 65, 65]
        self.indice = 0
        self.timer = 0
        self.toggle = True

    def onEnter(self, datas=None):
        pygame.mixer.music.play(-1)
        print('on enter')

    def onExit(self):
        pygame.mixer.music.stop()
        print('on exit')

    def update(self, dt):
        self.timer += dt

        self.afficheText()

        if self.timer > 0.4:
            self.timer = 0
            self.toggle = not self.toggle

        if game.getInputManager().isKeyPressed(pygame.K_LEFT) and self.indice > 0:
            self.indice = self.indice - 1

        if game.getInputManager().isKeyPressed(pygame.K_RIGHT) and self.indice < 2:
            self.indice = self.indice + 1

        if game.getInputManager().isKeyPressed(pygame.K_UP):
            self.tab[self.indice] = self.tab[self.indice]+1
            if self.tab[self.indice] > 90:
                self.tab[self.indice] = 65

        if game.getInputManager().isKeyPressed(pygame.K_DOWN):
            self.tab[self.indice] = self.tab[self.indice]-1
            if self.tab[self.indice] < 65:
                self.tab[self.indice] = 90

        if game.getInputManager().isKeyPressed(pygame.K_SPACE):
            txt = ""+chr(self.tab[0])+chr(self.tab[1])+chr(self.tab[2])
            datas = {"name": txt}

            game.getStageManager().changeStage(
                PlayStage(self.screenWidth, self.screenHeight), datas)

    def afficheText(self):
        zetxt = ""
        if self.indice == 0:
            if self.toggle:
                zetxt = '_'+chr(self.tab[1])+chr(self.tab[2])
            else:
                zetxt = chr(self.tab[0])+chr(self.tab[1])+chr(self.tab[2])

        #
        if self.indice == 1:
            if self.toggle:
                zetxt = chr(self.tab[0])+'_'+chr(self.tab[2])
            else:
                zetxt = chr(self.tab[0])+chr(self.tab[1])+chr(self.tab[2])

        #
        if self.indice == 2:
            if self.toggle:
                zetxt = chr(self.tab[0])+chr(self.tab[1])+'_'
            else:
                zetxt = chr(self.tab[0])+chr(self.tab[1])+chr(self.tab[2])

        self.labelName.setText(zetxt)

    def render(self, screen):
        screen.blit(self.img, (0, 0))

        self.labelTitle.render(screen, 200, 50)

        self.labelName.render(screen, 250, 200)

        self.labelCom.render(screen, 200, self.screenHeight-100)


################
class PlayStage(Stage):

    def __init__(self, screenWidth, screenHeight):
        #Stage.__init__(self, screenWidth, screenHeight)
        super().__init__(screenWidth, screenHeight)

        self.score = ScoreManager(self.screenWidth, self.screenHeight)
        self.score.setColor((70, 70, 70))

        self.paysage = Paysage(
            self.screenWidth, self.screenHeight, game.getAssetsManager().getImage("paysage"))

        self.rocks = []

        self.rocks.append(
            Rock(self.screenWidth, self.screenHeight, "UP",
                 game.getAssetsManager().getImage("rock_up")))

        self.rocks.append(Rock(self.screenWidth, self.screenHeight,
                               "DOWN", game.getAssetsManager().getImage("rock_down")))

        self.pillars = Pillars(
            self.screenWidth, self.screenHeight, game.getAssetsManager().getImage("pillar_up"),
            game.getAssetsManager().getImage("pillar_down"))

        self.plane = Plane(self.screenWidth, self.screenHeight, self.screenWidth/3,
                           self.screenHeight/3, {"plane": game.getAssetsManager().getImage("plane"),
                                                 "flying": game.getAssetsManager().getImage("flying"),
                                                 "explosion": game.getAssetsManager().getImage("explosion")})

        pygame.mixer.music.load('./assets/musics/plane.ogg')

    def onEnter(self, datas=None):
        if datas:
            self.score.setName(datas["name"])

        pygame.mixer.music.play(-1)

        print("play enter")

    def onExit(self):
        pygame.mixer.music.stop()
        print("play on exit")

    def update(self, dt):
        if game.getInputManager().isKeyPressed(pygame.K_SPACE):
            self.plane.pushUp()

        self.paysage.update(dt)

        self.pillars.update(dt)

        for rock in self.rocks:
            rock.update(dt)

        self.plane.update(dt)

        if self.pillars.isWinPoint() and self.plane.state == Plane.STATE_LIVE:
            self.pillars.newWave()
            self.score.incrementsPoints(1)

            game.getAssetsManager().getSound("check").play()

        self.checkCollisions()

        self.checkIsGameOver()

    def checkIsGameOver(self):
        if self.score.isGameOver():
            print('game over')

            datas = {}
            datas["name"] = self.score.getName()
            datas["points"] = self.score.getPoints()

            game.getStageManager().changeStage(GameOverStage(
                self.screenWidth, self.screenHeight), datas)

    def checkCollisions(self):
        # collision rocks
        for rock in self.rocks:
            if rock.collides(self.plane) and self.plane.state == Plane.STATE_LIVE:
                game.getAssetsManager().getSound("boom").play()
                self.plane.touched()
                self.score.decrementsLives()

        # collision plane pillars
        if self.pillars.isCollideWithPlane(self.plane):
            game.getAssetsManager().getSound("boom").play()
            self.plane.touched()
            self.score.decrementsLives()

    def render(self, screen):

        self.paysage.render(screen)

        self.pillars.render(screen)

        for rock in self.rocks:
            rock.render(screen)

        self.plane.render(screen)

        self.score.render(screen)


##########################
class GameOverStage(Stage):
    def __init__(self, screenWidth, screenHeight):
        #Stage.__init__(self, screenWidth, screenHeight)
        super().__init__(screenWidth, screenHeight)

        pygame.mixer.music.load('./assets/musics/underground.ogg')

        self.background = game.getAssetsManager().getImage("paysage")

        self.label = Label('./assets/fonts/free.ttf', 50)
        self.label.setColor((250, 20, 250))
        self.label.setText(("Game Over"))

        self.lbName = Label('./assets/fonts/free.ttf', 40)
        self.lbName.setColor((250, 20, 250))
        self.lbName.setText(("name"))

        self.lbPoints = Label('./assets/fonts/free.ttf', 40)
        self.lbPoints.setColor((200, 20, 250))
        self.lbPoints.setText("O pts")

        self.lbCom = Label('None', 30)
        self.lbCom.setColor((200, 20, 200))
        self.lbCom.setText(("Press Enter to continu"))

    def onEnter(self, datas=None):
        if datas:
            self.lbName.setText(datas["name"])

            txt = "Score = {}".format(datas["points"])

            self.lbPoints.setText(txt)

        pygame.mixer.music.play(-1)

    def onExit(self):
        pygame.mixer.music.stop()

    def update(self, dt):
        if game.getInputManager().isKeyPressed(pygame.K_RETURN):
            game.getStageManager().changeStage(IntroStage(self.screenWidth, self.screenHeight))

    def render(self, screen):
        screen.blit(self.background, (0, 0))

        self.label.render(screen, 200, 100)

        self.lbName.render(screen, 200, 200)

        self.lbPoints.render(screen, 200, 300)

        self.lbCom.render(screen, 200, 400)


##########
def main():
    # images
    game.getAssetsManager().loadImage("flying", "./assets/images/flying.png")

    game.getAssetsManager().loadImage("explosion", "./assets/images/explosion.png")

    game.getAssetsManager().loadImage("paysage", "./assets/images/paysage.png")

    game.getAssetsManager().loadImage("rock_up", "./assets/images/rock_up.png")

    game.getAssetsManager().loadImage("rock_down", "./assets/images/rock_down.png")

    game.getAssetsManager().loadImage("pillar_down", "./assets/images/pillar_bas.png")

    game.getAssetsManager().loadImage("pillar_up", "./assets/images/pillar_haut.png")

    game.getAssetsManager().loadImage("plane", "./assets/images/plane1.png")

    # sounds
    game.getAssetsManager().loadSound("check", "./assets/sounds/check.wav", 1.0)
    game.getAssetsManager().loadSound("boom", "./assets/sounds/boom.ogg", 1.0)

    #
    game.getStageManager().pushStage(IntroStage(screenWidth, screenHeight))

    #
    game.start()


######################
if __name__ == "__main__":
    main()
