import pygame
import pygame.font
import pygame.mixer
from random import randint
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

pygame.mixer.init()


class SoundPlayer:
    def __init__(self):
        self.sounds = {"back": pygame.mixer.Sound('back.wav'),
                       "next": pygame.mixer.Sound('next.wav'),
                       "main_menu_tick": pygame.mixer.Sound('main_menu_tick.wav'),
                       "error": pygame.mixer.Sound('error2.wav'),
                       "place": pygame.mixer.Sound('place.wav'),
                       "checkbox": pygame.mixer.Sound('checkbox.wav'),
                       "reset": pygame.mixer.Sound('reset.wav'),
                       "shot": pygame.mixer.Sound("cannon.wav")
                       }

    def play(self, soundName, format0='wav'):
        sound = self.sounds.get(soundName)
        if sound is None:
            soundNameWithEx = soundName + f'.{format0}'
            try:
                sound = pygame.mixer.Sound(soundNameWithEx)
            except FileNotFoundError:
                print(f'[HATA] {soundNameWithEx} dosyasi bulunamadi!!')
                return
            self.sounds[soundName] = sound
        sound.play()

    def set_volume(self, soundName, volume):
        sound = self.sounds.get(soundName)
        if sound is None:
            print(f'[HATA] {soundName} bulunamadi!!')
        else:
            sound.set_volume(volume)

    def add(self, soundFileName):
        newSound = pygame.mixer.Sound(soundFileName)
        soundName = soundFileName.split('.')[0]
        if (newSound is not None) and (self.sounds.get(soundName) is None):
            self.sounds[soundName] = newSound
        else:
            print(f'Bir sorun var (SoundPlayer.add)')


class MusicPlayer:
    @staticmethod
    def play(musicName, format1='wav', loops=-1):
        pygame.mixer.music.load(musicName + f'.{format1}')
        pygame.mixer.music.play(loops)

    @staticmethod
    def clear():
        pygame.mixer.music.pause()
        pygame.mixer.music.unload()

    @staticmethod
    def set_volume(volume):
        pygame.mixer.music.set_volume(volume)
    # ihtiyac halinde diger fonksiyonlar eklenecek


MusicPlayer.play('menu2')
MusicPlayer.set_volume(0.03)

W, H = 1400, 700  # Ekran Ölçüleri
scene = 0  # Sahne indexi
counter = 0
firingMode = -1
warning = 0
allyCoords = [[0 for a in range(10)] for b in range(10)]
enemyCoords = [[0 for m in range(10)] for n in range(10)]
unitLength = 1400 / 24
sizeofShip = -1
shipNumber = -1
reSet = -1
lastCoords = ([-1, -1], [-1, -1])
recordCoords = ([-1, -1], [-1, -1], [-1, -1], [-1, -1])
complete = [0, 0, 0, 0]
warscene = 0
ids = [[0, 0], [0, 0], [0, 0], [0, 0]]
hit = 0
miss = 0
enemyHitCounter = 0
allyHitCounter = 0
hitCoords = [0, 0]
turn = 0
textures = list()
timer = 0
win = -1
splayer = SoundPlayer()
restart = -1


def init():
    global ids, hit, miss
    glClearColor(0.0, 0.098, 0.2, 0.0)
    gluOrtho2D(0, 24, 0, 12)
    pygame.init()

    ids[0][0] = LoadTexture("destroyer.png")
    ids[0][1] = LoadTexture("destroyer_1.png")
    ids[1][0] = LoadTexture("fırkateyn.png")
    ids[1][1] = LoadTexture("fırkateyn_1.png")
    ids[2][0] = LoadTexture("korvet_1.png")
    ids[2][1] = LoadTexture("korvet_1_1.png")
    ids[3][0] = LoadTexture("korvet_2.png")
    ids[3][1] = LoadTexture("korvet_2_1.png")
    hit = LoadTexture("hit.png")
    miss = LoadTexture("miss.png")


def randomEnemy(coords):
    ok = 0
    while ok != 4:
        a = 0
        if ok == 3:
            a = 1
        length = 5 - ok + a
        stX = randint(0, 9)
        stY = randint(0, 9)
        if coords[stX][stY] == 0:
            way = randint(0, 3)
            if way == 0:
                if stX + length > 9:
                    way = 1
                    continue
                else:
                    for j in range(stX, stX + length):
                        if coords[j][stY] != 0:
                            way = 1
                            continue
                    for j in range(stX, stX + length):
                        coords[j][stY] = 1
                    ok += 1
                    continue
            if way == 1:
                if stX - length < 0:
                    way = 2
                    continue
                else:
                    for j in range(stX, stX - length, -1):
                        if coords[j][stY] != 0:
                            way = 2
                            continue
                    for j in range(stX, stX - length, -1):
                        coords[j][stY] = 1
                    ok += 1
                    continue
            if way == 2:
                if stY + length > 9:
                    way = 3
                    continue
                else:
                    for j in range(stY, stY + length):
                        if coords[stX][j] != 0:
                            way = 3
                            continue
                    for j in range(stY, stY + length):
                        coords[stX][j] = 1
                    ok += 1
                    continue
            if way == 3:
                if stY - length < 0:
                    continue
                else:
                    for j in range(stY, stY - length, -1):
                        if coords[j][stY] != 0:
                            continue
                    for j in range(stY, stY - length, -1):
                        coords[j][stY] = 1
                    ok += 1


def pushTexture(x1, y1, incX, incY, idNumber, axis, color=(0.0, 0.098, 0.2)):
    if axis == 0:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, idNumber)
        glColor3f(color[0], color[1], color[2])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(x1 + 0.01, y1 + 0.01)
        glTexCoord2f(0, 1)
        glVertex2f(x1 + incX - 0.01, y1 + 0.01)
        glTexCoord2f(1, 1)
        glVertex2f(x1 + incX - 0.01, y1 + incY - 0.01)
        glTexCoord2f(1, 0)
        glVertex2f(x1 + 0.01, y1 + incY - 0.01)
        glEnd()
        glDisable(GL_TEXTURE_2D)
    if axis == 1:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, idNumber)
        glColor3f(0.0, 0.098, 0.2)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(x1 + 0.01, y1 + 0.01)
        glTexCoord2f(0, 1)
        glVertex2f(x1 + 0.01, y1 + incY - 0.01)
        glTexCoord2f(1, 1)
        glVertex2f(x1 + incX - 0.01, y1 + incY - 0.01)
        glTexCoord2f(1, 0)
        glVertex2f(x1 + incX - 0.01, y1 + 0.01)
        glEnd()
        glDisable(GL_TEXTURE_2D)


def LoadTexture(file):
    glPixelStoref(GL_UNPACK_ALIGNMENT, 1)

    image = Image.open(file)
    xSize = image.size[0]
    ySize = image.size[1]
    image = image.tobytes("raw", "RGB")

    idNumber = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, idNumber)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, xSize, ySize, 0, GL_RGB, GL_UNSIGNED_BYTE, image)

    return idNumber


def drawText(position, textString, color, size, fontName=None):
    font = pygame.font.SysFont(fontName, size)
    textSurface = font.render(textString, True, color, (0, 25, 51, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)


def smaller(num1, num2):
    if num1 < num2:
        return num1
    elif num1 > num2:
        return num2
    else:
        return num1


def bigger(num1, num2):
    if num1 > num2:
        return num1
    elif num1 < num2:
        return num2
    else:
        return num1


# Pencere, el ile yeniden boyutlandırılmaya çalışılınca işlem ekranının değişmemesini sağlayan fonksiyon
def cantResize(w, h):
    glClear(GL_COLOR_BUFFER_BIT)
    glViewport(0, 0, W, H)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()


def mouse(button, state, x0, y):
    global scene, counter, firingMode, warning, sizeofShip, shipNumber, reSet, lastCoords, allyCoords, recordCoords, \
        complete, warscene, hitCoords, timer, win, enemyCoords, allyHitCounter, enemyHitCounter, splayer

    if button == GLUT_LEFT_BUTTON and state == 1:
        if lastCoords[0][0] == -1 and lastCoords[0][1] == -1:
            lastCoords[0][0] = x0
            lastCoords[0][1] = y
        else:
            lastCoords[1][0] = lastCoords[0][0]
            lastCoords[1][1] = lastCoords[0][1]
            lastCoords[0][0] = x0
            lastCoords[0][1] = y

    if scene == 0:
        if (583 <= x0 <= 816) and (290 <= y <= 408) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('main_menu_tick')
            counter = 1
            scene = 1
            MusicPlayer.clear()
            MusicPlayer.play("war")
        elif (612 <= x0 <= 786) and (466 <= y <= 524):
            splayer.play('main_menu_tick')
            sys.exit()
    elif scene == 1 and counter == 1:
        if (1166 <= x0 <= 1340) and (582 <= y <= 641) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('next')
            counter = 2
            scene = 2
    elif scene == 2 and counter == 2:
        if (58 <= x0 <= 233) and (582 <= y <= 641) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('back')
            counter = 1
            scene = 1
        if (1166 <= x0 <= 1340) and (582 <= y <= 641) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('next')
            counter = 3
            scene = 3
    elif scene == 3 and counter == 3:
        if (58 <= x0 <= 233) and (582 <= y <= 641) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('back')
            counter = 2
            scene = 2
        if (1049 <= x0 <= 1340) and (525 <= y <= 641) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('next')
            counter = 4
            scene = 4
    elif scene == 4 and counter == 4:
        if (209 <= x0 <= 256) and (589 <= y <= 634) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('checkbox')
            firingMode = 0
            warning = 0
        if (618 <= x0 <= 663) and (589 <= y <= 634) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('checkbox')
            firingMode = 1
            warning = 0
        if (1049 <= x0 <= 1340) and (525 <= y <= 641) and button == GLUT_LEFT_BUTTON and state == 1:
            if firingMode == -1:
                splayer.play('error')
                warning = 1
                # Uyarı Sesi
            else:
                splayer.play('next')
                counter = 5
                scene = 5
    elif scene == 5 and counter == 5:
        if (378 <= x0 <= 425) and (208 <= y <= 254) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('checkbox')
            sizeofShip = 5
            shipNumber = 0
        if (378 <= x0 <= 425) and (295 <= y <= 343) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('checkbox')
            sizeofShip = 4
            shipNumber = 1
        if (378 <= x0 <= 425) and (384 <= y <= 429) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('checkbox')
            sizeofShip = 3
            shipNumber = 2
        if (378 <= x0 <= 425) and (472 <= y <= 518) and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.play('checkbox')
            sizeofShip = 3
            shipNumber = 3
        if (58 <= x0 <= 232) and (582 <= y <= 639) and button == GLUT_LEFT_BUTTON and state == 1:
            reSet = 1
            splayer.play('reset')
        if reSet == 1:
            reSet = -1
            allyCoords = [[0 for i in range(10)] for j in range(10)]
            sizeofShip = -1
            shipNumber = -1
            lastCoords = ([-1, -1], [-1, -1])
            recordCoords = ([-1, -1], [-1, -1], [-1, -1], [-1, -1])
            complete = [0, 0, 0, 0]
            textures.clear()
            warscene = 0
        if (290 <= x0 <= 1108) and (173 <= y <= 522) and button == GLUT_LEFT_BUTTON and state == 1 and warscene == 1:
            controlNumbers = 0
            while controlNumbers != 1:
                randomEnemy(enemyCoords)
                numbers = 0
                for i in range(0, 9):
                    for j in range(0, 9):
                        if enemyCoords[i][j] == 1:
                            numbers += 1
                    if numbers == 15:
                        controlNumbers = 1
                        break
                    elif numbers != 15:
                        enemyCoords = [[0 for m in range(10)] for n in range(10)]
                        randomEnemy(enemyCoords)
            counter = 6
            scene = 6
            warscene = 0
            hitCoords[0] = 0
            hitCoords[1] = 0
    elif scene == 6 and counter == 6:
        if turn == 0 and button == GLUT_LEFT_BUTTON and state == 1:
            splayer.set_volume("shot", 0.1)
            splayer.play("shot")
            hitCoords[0] = x0
            hitCoords[1] = y

        if allyHitCounter == 15:
            win = 1
            counter = 7
            scene = 7
        elif enemyHitCounter == 15:
            win = 0
            counter = 7
            scene = 7
    elif scene == 7 and counter == 7:
        MusicPlayer.clear()
        if win == 0:
            MusicPlayer.play("defeat")
        if win == 1:
            MusicPlayer.play("victory")
        if (553 <= x0 <= 845) and (289 <= y <= 407) and button == GLUT_LEFT_BUTTON and state == 1:
            MusicPlayer.clear()
            MusicPlayer.play("war")
            counter = 4
            scene = 4
            allyCoords = [[0 for i in range(10)] for j in range(10)]
            enemyCoords = [[0 for i in range(10)] for j in range(10)]
            sizeofShip = -1
            shipNumber = -1
            lastCoords = ([-1, -1], [-1, -1])
            recordCoords = ([-1, -1], [-1, -1], [-1, -1], [-1, -1])
            complete = [0, 0, 0, 0]
            textures.clear()
            allyHitCounter = 0
            enemyHitCounter = 0
            win = -1
            warscene = 0
            reSet = -1
        elif (612 <= x0 <= 786) and (466 <= y <= 524):
            sys.exit()


# 10x10'luk ızgara çizimi
def drawGrid():
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(0, 1, 1)
    glLineWidth(1.0)

    glBegin(GL_LINES)

    for i in range(1, 11):
        for j in range(1, 11):
            glVertex2f(i, j)
            glVertex2f(i + 1, j)

            glVertex2f(i, j)
            glVertex2f(i, j + 1)
    glVertex2f(1, 11)
    glVertex2f(11, 11)
    glVertex2f(11, 1)
    glVertex2f(11, 11)

    for i in range(13, 23):
        for j in range(1, 11):
            glVertex2f(i, j)
            glVertex2f(i + 1, j)

            glVertex2f(i, j)
            glVertex2f(i, j + 1)
    glVertex2f(23, 1)
    glVertex2f(23, 11)
    glVertex2f(13, 11)
    glVertex2f(23, 11)

    glEnd()

    glFlush()


def drawScene0():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    gameName = "BATTLESHIP"
    drawText((3.5, 9, 0), "B", (0, 255, 255, 0), 85)
    drawText((5.25, 9, 0), "A", (0, 255, 255, 0), 100)
    drawText((7, 9, 0), "T", (0, 255, 255, 0), 115)
    drawText((9, 9, 0), "T", (0, 255, 255, 0), 130)
    drawText((11, 9, 0), "L", (0, 255, 255, 0), 145)
    drawText((13, 9, 0), "E", (0, 255, 255, 0), 145)
    drawText((15, 9, 0), "S", (0, 255, 255, 0), 130)
    drawText((17, 9, 0), "H", (0, 255, 255, 0), 115)
    drawText((19, 9, 0), "I", (0, 255, 255, 0), 100)
    drawText((20.5, 9, 0), "P", (0, 255, 255, 0), 85)

    glColor3f(1, 1, 1)
    glBegin(GL_LINE_LOOP)
    glVertex2f(10, 5)
    glVertex2f(10, 7)
    glVertex2f(10, 7)
    glVertex2f(14, 7)
    glVertex2f(14, 7)
    glVertex2f(14, 5)
    glEnd()
    drawText((10.45, 5.5, 0), "BAŞLA", (80, 186, 209), 75)

    glBegin(GL_LINE_LOOP)
    glVertex2f(10.5, 4)
    glVertex2f(13.5, 4)
    glVertex2f(13.5, 4)
    glVertex2f(13.5, 3)
    glVertex2f(13.5, 3)
    glVertex2f(10.5, 3)
    glEnd()
    drawText((11.2, 3.2, 0), "ÇIKIŞ", (80, 186, 209), 50)

    drawText((0, 0, 0), "v1.0", (80, 186, 209), 20)


def drawScene1():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    drawText((1, 11, 0), "Merhaba gelecegin kaptan adayı,", (142, 223, 255), 30, "footlight")
    drawText((1, 10, 0), "Savas simulasyon testlerine hosgeldin. Ben Interaktif Sistem Yönetim Arabirimi. Kısaca ISYA "
                         "diyebilirsin.", (142, 223, 255), 30, "footlight")
    drawText((1, 9.5, 0), "Simulasyon boyunca, moral olması açısından sana Amiral diye hitap edecegim.",
             (142, 223, 255),
             30, "footlight")
    drawText((1, 8.5, 0), "Öncelikle buraya kadar olan testlerden basarı ile geçtigin için tebrik ederim. Simdi savas "
                          "simulasyon", (142, 223, 255), 30, "footlight")
    drawText((1, 8.0, 0), "testlerine tabi tutulacaksın. Amiral Battı oyunu biliyorsun degil mi ? Ilk asama olarak "
                          "bununla", (142, 223, 255), 30, "footlight")
    drawText((1, 7.5, 0), "baslayacagız . Ileri asamalarda oldugu gibi asırı gerçekçi bir simulasyon olmayacak ancak "
                          "unutma ki ", (142, 223, 255), 30, "footlight")
    drawText((1, 7.0, 0), "en basarılı denizciler bile sıfırdan basladı.", (142, 223, 255), 30, "footlight")
    drawText((1, 5.0, 0), "Simdi vakit kaybetmeden oyun kurallarına gecelim Amiral.", (142, 223, 255), 30, "footlight")

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(20, 1)
    glVertex2f(23, 1)
    glVertex2f(23, 1)
    glVertex2f(23, 2)
    glVertex2f(23, 2)
    glVertex2f(20, 2)
    glEnd()

    drawText((20.7, 1.1, 0), "Ileri", (80, 186, 209), 50, "footlight")
    drawText((0, 0, 0), "Filo Personelı Egitim Sistemi ver1.006874", (80, 186, 209), 20)


def drawScene2():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    drawText((1, 11, 0), "Amiral, yaygın olarak bilinen oyundan biraz farklı kurallarımız var. Dikkatlice dinle.",
             (142, 223, 255), 30, "footlight")
    drawText((1, 10, 0), "Filo dört gemiden olusuyor. Komutan altında bir adet 5x1'lik destroyer, bir adet 4x1'lik "
                         "fırkateyn ve", (142, 223, 255), 30, "footlight")
    drawText((1, 9.5, 0), "iki adet 3x1'lik korvet bulunuyor. Filonu 10x10'luk bir alana dikey veya yatay "
                          "yerlestirebilirsin ve", (142, 223, 255), 30, "footlight")
    drawText((1, 9.0, 0), "gemiler birbirine temas edebilir. Gemilerin konumunu sadece savastan önce belirleyebilirsin ve",
             (142, 223, 255), 30, "footlight")
    drawText((1, 8.5, 0), "savas sırasında bunu degistiremezsin.", (142, 223, 255), 30, "footlight")
    drawText((1, 7.5, 0), "Atıs kuralları ise iki kısımdan olusuyor. Birisi seri atıs modu. Bu seçenekte atıs sırası "
                          "sende iken sadece", (142, 223, 255), 30, "footlight")
    drawText((1, 7.0, 0), "kalan gemi sayısı kadar atıs yapabilirsin. Ayrıca bir gemi tamamen yok olmadıgı müddetçe"
                          " atısa devam", (142, 223, 255), 30, "footlight")
    drawText((1, 6.5, 0), "edebilir. Digeri ise takipli atıs modu. Bu seçenekte ise atıs sırası sende iken bir kez "
                          "atıs yaparsın ancak isabet", (142, 223, 255), 30, "footlight")
    drawText((1, 6.0, 0), "kaydettigin takdirde atısa devam edebilirsin ve bunu tüm düsman gemileri yok olana  devam "
                          "ettirebilirsin.", (142, 223, 255), 30, "footlight")
    drawText((1, 5.5, 0), "Her atıs modunun kendine göre avantajları ve dezavantajları var. Bunu iyi kullanman gerek.",
             (142, 223, 255), 30, "footlight")

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(20, 1)
    glVertex2f(23, 1)
    glVertex2f(23, 1)
    glVertex2f(23, 2)
    glVertex2f(23, 2)
    glVertex2f(20, 2)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(1, 1)
    glVertex2f(4, 1)
    glVertex2f(4, 1)
    glVertex2f(4, 2)
    glVertex2f(4, 2)
    glVertex2f(1, 2)
    glEnd()

    # İçi dolu kutucuklar

    drawText((20.7, 1.1, 0), "Ileri", (80, 186, 209), 50, "footlight")
    drawText((1.7, 1.1, 0), "Geri", (80, 186, 209), 50, "footlight")
    drawText((0, 0, 0), "Filo Personelı Egitim Sistemi ver1.006874", (80, 186, 209), 20)


def drawScene3():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    drawText((1, 10, 0), "Bu testin kazandırmaya çalıstıgı sey gemilerini stratejik olarak yerlestirmen ve düsmanın "
                         "konumunu", (142, 223, 255), 30, "footlight")
    drawText((1, 9, 0), "yaptıgın atıslara göre tahmin ederek yok etmen. Son olarak önemli bir sey daha var. Karsında",
             (142, 223, 255), 30, "footlight")
    drawText((1, 8, 0), "bu teste tabi tutulanlar arasındaki en iyilerin oynayıs stratejileri ile gelistirilmis bir "
                        "yapay zeka var. ", (142, 223, 255), 30, "footlight")
    drawText((1, 7, 0), "O yüzden hamlelerini düsünerek yap ancak unutma ki karsındaki de senle aynı imkanlara sahip.",
             (142, 223, 255), 30, "footlight")
    drawText((1, 5, 0), "Amiral, aklına takılan bir sey varsa önceki konusmalarımıza giderek tekrar okuyabilirsin ancak "
                        "sonraki", (142, 223, 255), 30, "footlight")
    drawText((1, 4, 0), "asamaya geçtikten sonra bu kısımlara erisemezsin.", (142, 223, 255), 30, "footlight")

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(18, 1)
    glVertex2f(23, 1)
    glVertex2f(23, 1)
    glVertex2f(23, 3)
    glVertex2f(23, 3)
    glVertex2f(18, 3)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(1, 1)
    glVertex2f(4, 1)
    glVertex2f(4, 1)
    glVertex2f(4, 2)
    glVertex2f(4, 2)
    glVertex2f(1, 2)
    glEnd()

    drawText((18.25, 2, 0), "Savas Öncesi", (80, 186, 209), 50, "footlight")
    drawText((19, 1.1, 0), "Hazırlık", (80, 186, 209), 50, "footlight")
    drawText((1.7, 1.1, 0), "Geri", (80, 186, 209), 50, "footlight")
    drawText((0, 0, 0), "Filo Personelı Egitim Sistemi ver1.006874", (80, 186, 209), 20)


def drawScene4():
    global firingMode, warning

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glLoadIdentity()

    drawText((0.5, 11, 0), "ATIS TIPI SEÇIMI", (80, 186, 209), 30, "footlight")
    drawText((0.5, 9, 0), "Amiral, kullanmak istediginiz atıs seklini secin.", (80, 186, 209), 30, "footlight")
    drawText((2.25, 7, 0), "SERI ATIS", (80, 186, 209), 50, "footlight")
    drawText((1.5, 6, 0), "Yok olmamıs gemi sayısı kadar atıs", (80, 186, 209), 22, "footlight")
    drawText((1.5, 5.25, 0), "Isabet halinde tekrar yok", (80, 186, 209), 22, "footlight")
    drawText((1.5, 4, 0), "YAKINDA ...", (0, 186, 0), 22, "footlight")
    drawText((8.75, 7, 0), "TAKIPLI ATIS", (80, 186, 209), 50, "footlight")
    drawText((8.5, 6, 0), "Tek atıs", (80, 186, 209), 22, "footlight")
    drawText((8.5, 5.25, 0), "Isabet halinde tekrar var", (80, 186, 209), 22, "footlight")

    glBegin(GL_LINE_LOOP)
    glColor3f(0, 255, 255)
    glVertex2f(0.25, 11.75)
    glVertex2f(4.3, 11.75)
    glVertex2f(4.3, 11.75)
    glVertex2f(4.3, 10.75)
    glVertex2f(4.3, 10.75)
    glVertex2f(0.25, 10.75)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(255, 255, 255)
    glVertex2f(1, 1)
    glVertex2f(1, 8)
    glVertex2f(1, 8)
    glVertex2f(7, 8)
    glVertex2f(7, 8)
    glVertex2f(7, 1)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glVertex2f(8, 1)
    glVertex2f(8, 8)
    glVertex2f(8, 8)
    glVertex2f(14, 8)
    glVertex2f(14, 8)
    glVertex2f(14, 1)
    glEnd()

    glBegin(GL_LINES)
    glVertex2f(1, 2)
    glVertex2f(7, 2)
    glVertex2f(8, 2)
    glVertex2f(14, 2)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(3.6, 1.1)
    glVertex2f(4.4, 1.1)
    glVertex2f(4.4, 1.1)
    glVertex2f(4.4, 1.9)
    glVertex2f(4.4, 1.9)
    glVertex2f(3.6, 1.9)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(10.6, 1.1)
    glVertex2f(11.4, 1.1)
    glVertex2f(11.4, 1.1)
    glVertex2f(11.4, 1.9)
    glVertex2f(11.4, 1.9)
    glVertex2f(10.6, 1.9)
    glEnd()

    if firingMode == 0:
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glColor3f(1, 1, 1)
        glVertex2f(3.6, 1.1)
        glVertex2f(4.4, 1.1)
        glVertex2f(4.4, 1.9)
        glVertex2f(3.6, 1.9)
        glEnd()

    if firingMode == 1:
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glVertex2f(10.6, 1.1)
        glVertex2f(11.4, 1.1)
        glVertex2f(11.4, 1.9)
        glVertex2f(10.6, 1.9)
        glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(18, 1)
    glVertex2f(23, 1)
    glVertex2f(23, 1)
    glVertex2f(23, 3)
    glVertex2f(23, 3)
    glVertex2f(18, 3)
    glEnd()

    if warning == 1:
        if firingMode != -1:
            warning = 0
        drawText((19, 10, 0), "UYARI", (255, 0, 0), 50, "footlight")
        drawText((18, 9, 0), "Atıs tipi seçmediniz !", (255, 0, 0), 30, "footlight")

    drawText((18.5, 2, 0), "Filo Düzeni", (80, 186, 209), 50, "footlight")
    drawText((19.5, 1.1, 0), "Seçimi", (80, 186, 209), 50, "footlight")
    drawText((0, 0, 0), "Filo Personelı Egitim Sistemi ver1.006874", (80, 186, 209), 20)


def drawScene5():
    global lastCoords, allyCoords, unitLength, complete, recordCoords, reSet, sizeofShip, shipNumber, warscene, splayer

    #  Sıfırlama için değişkenlerin başlangıç haline getirilmesi
    if reSet == 1:
        allyCoords = [[0 for i in range(10)] for j in range(10)]
        sizeofShip = -1
        shipNumber = -1
        lastCoords = ([-1, -1], [-1, -1])
        recordCoords = ([-1, -1], [-1, -1], [-1, -1], [-1, -1])
        complete = [0, 0, 0, 0]
        warscene = 0
        reSet = -1
        return

    #  Sağ taraftaki ızgara çizimi
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glLoadIdentity()

    glBegin(GL_LINES)
    glColor3f(1, 1, 1)
    for i in range(13, 23):
        for j in range(1, 11):
            glVertex2f(i, j)
            glVertex2f(i + 1, j)

            glVertex2f(i, j)
            glVertex2f(i, j + 1)
    glVertex2f(13, 11)
    glVertex2f(23, 11)
    glVertex2f(23, 11)
    glVertex2f(23, 1)

    glColor3f(0, 1, 1)
    glVertex2f(2, 8.5)
    glVertex2f(2, 7.5)
    glVertex2f(3, 8.5)
    glVertex2f(3, 7.5)
    glVertex2f(4, 8.5)
    glVertex2f(4, 7.5)
    glVertex2f(5, 8.5)
    glVertex2f(5, 7.5)

    glVertex2f(2, 7)
    glVertex2f(2, 6)
    glVertex2f(3, 7)
    glVertex2f(3, 6)
    glVertex2f(4, 7)
    glVertex2f(4, 6)

    glVertex2f(2, 5.5)
    glVertex2f(2, 4.5)
    glVertex2f(3, 5.5)
    glVertex2f(3, 4.5)

    glVertex2f(2, 4)
    glVertex2f(2, 3)
    glVertex2f(3, 4)
    glVertex2f(3, 3)

    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(0, 255, 255)
    glVertex2f(0.25, 11.75)
    glVertex2f(5.25, 11.75)
    glVertex2f(5.25, 11.75)
    glVertex2f(5.25, 10.75)
    glVertex2f(5.25, 10.75)
    glVertex2f(0.25, 10.75)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(255, 255, 255)
    glVertex2f(1, 1)
    glVertex2f(4, 1)
    glVertex2f(4, 1)
    glVertex2f(4, 2)
    glVertex2f(4, 2)
    glVertex2f(1, 2)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(0, 1, 1)
    glVertex2f(1, 8.5)
    glVertex2f(6, 8.5)
    glVertex2f(6, 8.5)
    glVertex2f(6, 7.5)
    glVertex2f(6, 7.5)
    glVertex2f(1, 7.5)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glVertex2f(1, 7)
    glVertex2f(5, 7)
    glVertex2f(5, 7)
    glVertex2f(5, 6)
    glVertex2f(5, 6)
    glVertex2f(1, 6)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glVertex2f(1, 5.5)
    glVertex2f(4, 5.5)
    glVertex2f(4, 5.5)
    glVertex2f(4, 4.5)
    glVertex2f(4, 4.5)
    glVertex2f(1, 4.5)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glVertex2f(1, 4)
    glVertex2f(4, 4)
    glVertex2f(4, 4)
    glVertex2f(4, 3)
    glVertex2f(4, 3)
    glVertex2f(1, 3)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(6.5, 8.4)
    glVertex2f(7.3, 8.4)
    glVertex2f(7.3, 8.4)
    glVertex2f(7.3, 7.6)
    glVertex2f(7.3, 7.6)
    glVertex2f(6.5, 7.6)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(6.5, 6.9)
    glVertex2f(7.3, 6.9)
    glVertex2f(7.3, 6.9)
    glVertex2f(7.3, 6.1)
    glVertex2f(7.3, 6.1)
    glVertex2f(6.5, 6.1)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(6.5, 5.4)
    glVertex2f(7.3, 5.4)
    glVertex2f(7.3, 5.4)
    glVertex2f(7.3, 4.6)
    glVertex2f(7.3, 4.6)
    glVertex2f(6.5, 4.6)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(1, 1, 1)
    glVertex2f(6.5, 3.9)
    glVertex2f(7.3, 3.9)
    glVertex2f(7.3, 3.9)
    glVertex2f(7.3, 3.1)
    glVertex2f(7.3, 3.1)
    glVertex2f(6.5, 3.1)
    glEnd()

    #  Gemiye ait kutucuk seçildiyse ve daha önce seçim yapılmamışsa
    if shipNumber == 0 and complete[0] == 0:
        shipSize = sizeofShip
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glVertex2f(6.5, 8.4)
        glVertex2f(7.3, 8.4)
        glVertex2f(7.3, 7.6)
        glVertex2f(6.5, 7.6)
        glEnd()

        # Tıklanılan yer ızgara içerisindeyse
        if unitLength * 13 <= lastCoords[0][0] < unitLength * 23 and unitLength <= lastCoords[0][1] < unitLength * 11 and \
                allyCoords[(int(lastCoords[0][0] // unitLength)) - 13][10 - int(lastCoords[0][1] // unitLength)] == 0:
            splayer.play('place')
            glBegin(GL_LINE_LOOP)
            glColor3f(0, 0.5, 1)
            glVertex2f(lastCoords[0][0] // unitLength, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength) + 1)
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength) + 1)
            glVertex2f(lastCoords[0][0] // unitLength, 11 - (lastCoords[0][1] // unitLength) + 1)
            glEnd()

            #  İkinci tıklanılan yer dikey olarak gemi uzunluğuna eşitse
            if abs((lastCoords[0][0] // unitLength) - (lastCoords[1][0] // unitLength)) == shipSize - 1 and (
                    (lastCoords[0][1] // unitLength) - (lastCoords[1][1] // unitLength)) == 0:
                glBegin(GL_LINE_LOOP)
                glColor3f(0, 0.5, 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength),
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength),
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glEnd()
                #  Tıklanılan yer geçerliyse bu koordinatları ilerde kullanmak için değişkene atar
                recordCoords[shipNumber][0] = smaller(lastCoords[0][0], lastCoords[1][0])
                recordCoords[shipNumber][1] = smaller(lastCoords[0][1], lastCoords[1][1])

                glBegin(GL_QUADS)
                glColor3f(0, 1, 0)
                glVertex2f(6.5, 8.4)
                glVertex2f(7.3, 8.4)
                glVertex2f(7.3, 7.6)
                glVertex2f(6.5, 7.6)
                glEnd()
                #  Gemilerin bulunduğu yerleri dizide 1 yapar
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 13)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 12)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 11)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 10)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 9)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                #  Seçim işlemi bitince tekrar tıklanmamısını sağlar
                complete[shipNumber] = 1

            #  İkinci tıklanılan yer yatay olarak gemi uzunluğuna eşitse
            elif abs((lastCoords[0][1] // unitLength) - (lastCoords[1][1] // unitLength)) == shipSize - 1 and (
                    (lastCoords[0][0] // unitLength) - (lastCoords[1][0] // unitLength)) == 0:
                glBegin(GL_LINE_LOOP)
                glColor3f(0, 0.5, 1)
                glVertex2f(lastCoords[0][0] // unitLength,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glVertex2f(lastCoords[0][0] // unitLength,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glEnd()

                recordCoords[shipNumber][0] = bigger(lastCoords[0][0], lastCoords[1][0])
                recordCoords[shipNumber][1] = bigger(lastCoords[0][1], lastCoords[1][1])

                glBegin(GL_QUADS)
                glColor3f(0, 1, 0)
                glVertex2f(6.5, 8.4)
                glVertex2f(7.3, 8.4)
                glVertex2f(7.3, 7.6)
                glVertex2f(6.5, 7.6)
                glEnd()

                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))] = 1
                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength)) + 1] = 1
                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength)) + 2] = 1
                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength)) + 3] = 1
                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength)) + 4] = 1

                complete[shipNumber] = 2

    if shipNumber == 1 and complete[1] == 0:
        shipSize = sizeofShip
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glVertex2f(6.5, 6.9)
        glVertex2f(7.3, 6.9)
        glVertex2f(7.3, 6.1)
        glVertex2f(6.5, 6.1)
        glEnd()
        if unitLength * 13 <= lastCoords[0][0] < unitLength * 23 and unitLength <= lastCoords[0][1] < unitLength * 11 and \
                allyCoords[(int(lastCoords[0][0] // unitLength)) - 13][10 - int(lastCoords[0][1] // unitLength)] == 0:
            splayer.play('place')
            glBegin(GL_LINE_LOOP)
            glColor3f(0, 0.5, 1)
            glVertex2f(lastCoords[0][0] // unitLength, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength) + 1)
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength) + 1)
            glVertex2f(lastCoords[0][0] // unitLength, 11 - (lastCoords[0][1] // unitLength) + 1)
            glEnd()

            if abs((lastCoords[0][0] // unitLength) - (lastCoords[1][0] // unitLength)) == shipSize - 1 and (
                    (lastCoords[0][1] // unitLength) - (lastCoords[1][1] // unitLength)) == 0:
                glBegin(GL_LINE_LOOP)
                glColor3f(0, 0.5, 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength),
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength),
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glEnd()

                recordCoords[shipNumber][0] = smaller(lastCoords[0][0], lastCoords[1][0])
                recordCoords[shipNumber][1] = smaller(lastCoords[0][1], lastCoords[1][1])

                glBegin(GL_QUADS)
                glColor3f(0, 1, 0)
                glVertex2f(6.5, 6.9)
                glVertex2f(7.3, 6.9)
                glVertex2f(7.3, 6.1)
                glVertex2f(6.5, 6.1)
                glEnd()

                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 13)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 12)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 11)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 10)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1

                complete[shipNumber] = 1

            elif abs((lastCoords[0][1] // unitLength) - (lastCoords[1][1] // unitLength)) == shipSize - 1 and (
                    (lastCoords[0][0] // unitLength) - (lastCoords[1][0] // unitLength)) == 0:
                glBegin(GL_LINE_LOOP)
                glColor3f(0, 0.5, 1)
                glVertex2f(lastCoords[0][0] // unitLength,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glVertex2f(lastCoords[0][0] // unitLength,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glEnd()

                recordCoords[shipNumber][0] = bigger(lastCoords[0][0], lastCoords[1][0])
                recordCoords[shipNumber][1] = bigger(lastCoords[0][1], lastCoords[1][1])

                glBegin(GL_QUADS)
                glColor3f(0, 1, 0)
                glVertex2f(6.5, 6.9)
                glVertex2f(7.3, 6.9)
                glVertex2f(7.3, 6.1)
                glVertex2f(6.5, 6.1)
                glEnd()

                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))] = 1
                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength)) + 1] = 1
                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength)) + 2] = 1
                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength)) + 3] = 1

                complete[shipNumber] = 2

    if shipNumber == 2 and complete[2] == 0:
        shipSize = sizeofShip
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glVertex2f(6.5, 5.4)
        glVertex2f(7.3, 5.4)
        glVertex2f(7.3, 4.6)
        glVertex2f(6.5, 4.6)
        glEnd()
        if unitLength * 13 <= lastCoords[0][0] < unitLength * 23 and unitLength <= lastCoords[0][1] < unitLength * 11 and \
                allyCoords[(int(lastCoords[0][0] // unitLength)) - 13][10 - int(lastCoords[0][1] // unitLength)] == 0:
            splayer.play('place')
            glBegin(GL_LINE_LOOP)
            glColor3f(0, 0.5, 1)
            glVertex2f(lastCoords[0][0] // unitLength, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength) + 1)
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength) + 1)
            glVertex2f(lastCoords[0][0] // unitLength, 11 - (lastCoords[0][1] // unitLength) + 1)
            glEnd()

            if abs((lastCoords[0][0] // unitLength) - (lastCoords[1][0] // unitLength)) == shipSize - 1 and (
                    (lastCoords[0][1] // unitLength) - (lastCoords[1][1] // unitLength)) == 0:
                glBegin(GL_LINE_LOOP)
                glColor3f(0, 0.5, 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength),
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength),
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glEnd()

                recordCoords[shipNumber][0] = smaller(lastCoords[0][0], lastCoords[1][0])
                recordCoords[shipNumber][1] = smaller(lastCoords[0][1], lastCoords[1][1])

                glBegin(GL_QUADS)
                glColor3f(0, 1, 0)
                glVertex2f(6.5, 8.4)
                glVertex2f(7.3, 8.4)
                glVertex2f(7.3, 7.6)
                glVertex2f(6.5, 7.6)
                glEnd()

                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 13)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 12)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 11)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1

                complete[shipNumber] = 1

            elif abs((lastCoords[0][1] // unitLength) - (lastCoords[1][1] // unitLength)) == shipSize - 1 and (
                    (lastCoords[0][0] // unitLength) - (lastCoords[1][0] // unitLength)) == 0:
                glBegin(GL_LINE_LOOP)
                glColor3f(0, 0.5, 1)
                glVertex2f(lastCoords[0][0] // unitLength,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glVertex2f(lastCoords[0][0] // unitLength,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glEnd()

                recordCoords[shipNumber][0] = bigger(lastCoords[0][0], lastCoords[1][0])
                recordCoords[shipNumber][1] = bigger(lastCoords[0][1], lastCoords[1][1])

                glBegin(GL_QUADS)
                glColor3f(0, 1, 0)
                glVertex2f(6.5, 8.4)
                glVertex2f(7.3, 8.4)
                glVertex2f(7.3, 7.6)
                glVertex2f(6.5, 7.6)
                glEnd()

                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))] = 1
                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength)) + 1] = 1
                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength)) + 2] = 1

                complete[shipNumber] = 2

    if shipNumber == 3 and complete[3] == 0:
        shipSize = sizeofShip
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glVertex2f(6.5, 3.9)
        glVertex2f(7.3, 3.9)
        glVertex2f(7.3, 3.1)
        glVertex2f(6.5, 3.1)
        glEnd()
        if unitLength * 13 <= lastCoords[0][0] < unitLength * 23 and unitLength <= lastCoords[0][1] < unitLength * 11 and \
                allyCoords[(int(lastCoords[0][0] // unitLength)) - 13][10 - int(lastCoords[0][1] // unitLength)] == 0:
            splayer.play('place')
            glBegin(GL_LINE_LOOP)
            glColor3f(0, 0.5, 1)
            glVertex2f(lastCoords[0][0] // unitLength, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength))
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength) + 1)
            glVertex2f((lastCoords[0][0] // unitLength) + 1, 11 - (lastCoords[0][1] // unitLength) + 1)
            glVertex2f(lastCoords[0][0] // unitLength, 11 - (lastCoords[0][1] // unitLength) + 1)
            glEnd()

            if abs((lastCoords[0][0] // unitLength) - (lastCoords[1][0] // unitLength)) == shipSize - 1 and (
                    (lastCoords[0][1] // unitLength) - (lastCoords[1][1] // unitLength)) == 0:
                glBegin(GL_LINE_LOOP)
                glColor3f(0, 0.5, 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength),
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength))
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) + shipSize,
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glVertex2f(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength),
                           11 - (lastCoords[0][1] // unitLength) + 1)
                glEnd()

                recordCoords[shipNumber][0] = smaller(lastCoords[0][0], lastCoords[1][0])
                recordCoords[shipNumber][1] = smaller(lastCoords[0][1], lastCoords[1][1])

                glBegin(GL_QUADS)
                glColor3f(0, 1, 0)
                glVertex2f(6.5, 8.4)
                glVertex2f(7.3, 8.4)
                glVertex2f(7.3, 7.6)
                glVertex2f(6.5, 7.6)
                glEnd()

                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 13)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 12)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1
                allyCoords[int(smaller(lastCoords[0][0] // unitLength, lastCoords[1][0] // unitLength) - 11)][
                    int(10 - int(lastCoords[0][1] // unitLength))] = 1

                complete[shipNumber] = 1

            elif abs((lastCoords[0][1] // unitLength) - (lastCoords[1][1] // unitLength)) == shipSize - 1 and (
                    (lastCoords[0][0] // unitLength) - (lastCoords[1][0] // unitLength)) == 0:
                glBegin(GL_LINE_LOOP)
                glColor3f(0, 0.5, 1)
                glVertex2f(lastCoords[0][0] // unitLength,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glVertex2f((lastCoords[0][0] // unitLength) + 1,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glVertex2f(lastCoords[0][0] // unitLength,
                           11 - bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength) + shipSize)
                glEnd()

                recordCoords[shipNumber][0] = bigger(lastCoords[0][0], lastCoords[1][0])
                recordCoords[shipNumber][1] = bigger(lastCoords[0][1], lastCoords[1][1])

                glBegin(GL_QUADS)
                glColor3f(0, 1, 0)
                glVertex2f(6.5, 8.4)
                glVertex2f(7.3, 8.4)
                glVertex2f(7.3, 7.6)
                glVertex2f(6.5, 7.6)
                glEnd()

                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength))] = 1
                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength)) + 1] = 1
                allyCoords[int(lastCoords[0][0] // unitLength) - 13][
                    10 - int(bigger(lastCoords[0][1] // unitLength, lastCoords[1][1] // unitLength)) + 2] = 1

                complete[shipNumber] = 2

    #  Yukarıda kaydedilen koordinatların eğer dikeyse renkli olarak çizdirilmesi
    if complete[0] == 1:
        glBegin(GL_LINE_LOOP)
        glColor3f(0, 0.5, 1)
        glVertex2f(recordCoords[0][0] // unitLength, 11 - (recordCoords[0][1] // unitLength))
        glVertex2f(recordCoords[0][0] // unitLength + 5, 11 - (recordCoords[0][1] // unitLength))
        glVertex2f(recordCoords[0][0] // unitLength + 5, 11 - (recordCoords[0][1] // unitLength))
        glVertex2f(recordCoords[0][0] // unitLength + 5, 11 - (recordCoords[0][1] // unitLength) + 1)
        glVertex2f(recordCoords[0][0] // unitLength + 5, 11 - (recordCoords[0][1] // unitLength) + 1)
        glVertex2f(recordCoords[0][0] // unitLength, 11 - (recordCoords[0][1] // unitLength) + 1)
        glEnd()
        # Seçim kutucuğunun yeşil olması
        glBegin(GL_QUADS)
        glColor3f(0, 1, 0)
        glVertex2f(6.5, 8.4)
        glVertex2f(7.3, 8.4)
        glVertex2f(7.3, 7.6)
        glVertex2f(6.5, 7.6)
        glEnd()
    #  Yukarıda kaydedilen koordinatların eğer dikeyse renkli olarak çizdirilmesi
    if complete[0] == 2:
        shipSize = sizeofShip
        glBegin(GL_LINE_LOOP)
        glColor3f(0, 0.5, 1)
        glVertex2f(recordCoords[0][0] // unitLength, 11 - (recordCoords[0][1] // unitLength))
        glVertex2f(recordCoords[0][0] // unitLength + 1, 11 - (recordCoords[0][1] // unitLength))
        glVertex2f(recordCoords[0][0] // unitLength + 1, 11 - (recordCoords[0][1] // unitLength))
        glVertex2f(recordCoords[0][0] // unitLength + 1, 11 - (recordCoords[0][1] // unitLength) + 5)
        glVertex2f(recordCoords[0][0] // unitLength + 1, 11 - (recordCoords[0][1] // unitLength) + 5)
        glVertex2f(recordCoords[0][0] // unitLength, 11 - (recordCoords[0][1] // unitLength) + 5)
        glEnd()

        glBegin(GL_QUADS)
        glColor3f(0, 1, 0)
        glVertex2f(6.5, 8.4)
        glVertex2f(7.3, 8.4)
        glVertex2f(7.3, 7.6)
        glVertex2f(6.5, 7.6)
        glEnd()

    if complete[1] == 1:
        glBegin(GL_LINE_LOOP)
        glColor3f(0, 0.5, 1)
        glVertex2f(recordCoords[1][0] // unitLength, 11 - (recordCoords[1][1] // unitLength))
        glVertex2f(recordCoords[1][0] // unitLength + 4, 11 - (recordCoords[1][1] // unitLength))
        glVertex2f(recordCoords[1][0] // unitLength + 4, 11 - (recordCoords[1][1] // unitLength))
        glVertex2f(recordCoords[1][0] // unitLength + 4, 11 - (recordCoords[1][1] // unitLength) + 1)
        glVertex2f(recordCoords[1][0] // unitLength + 4, 11 - (recordCoords[1][1] // unitLength) + 1)
        glVertex2f(recordCoords[1][0] // unitLength, 11 - (recordCoords[1][1] // unitLength) + 1)
        glEnd()

        glBegin(GL_QUADS)
        glColor3f(0, 1, 0)
        glVertex2f(6.5, 6.9)
        glVertex2f(7.3, 6.9)
        glVertex2f(7.3, 6.1)
        glVertex2f(6.5, 6.1)
        glEnd()
    if complete[1] == 2:
        shipSize = sizeofShip
        glBegin(GL_LINE_LOOP)
        glColor3f(0, 0.5, 1)
        glVertex2f(recordCoords[1][0] // unitLength, 11 - (recordCoords[1][1] // unitLength))
        glVertex2f(recordCoords[1][0] // unitLength + 1, 11 - (recordCoords[1][1] // unitLength))
        glVertex2f(recordCoords[1][0] // unitLength + 1, 11 - (recordCoords[1][1] // unitLength))
        glVertex2f(recordCoords[1][0] // unitLength + 1, 11 - (recordCoords[1][1] // unitLength) + 4)
        glVertex2f(recordCoords[1][0] // unitLength + 1, 11 - (recordCoords[1][1] // unitLength) + 4)
        glVertex2f(recordCoords[1][0] // unitLength, 11 - (recordCoords[1][1] // unitLength) + 4)
        glEnd()

        glBegin(GL_QUADS)
        glColor3f(0, 1, 0)
        glVertex2f(6.5, 6.9)
        glVertex2f(7.3, 6.9)
        glVertex2f(7.3, 6.1)
        glVertex2f(6.5, 6.1)
        glEnd()

    if complete[2] == 1:
        glBegin(GL_LINE_LOOP)
        glColor3f(0, 0.5, 1)
        glVertex2f(recordCoords[2][0] // unitLength, 11 - (recordCoords[2][1] // unitLength))
        glVertex2f(recordCoords[2][0] // unitLength + 3, 11 - (recordCoords[2][1] // unitLength))
        glVertex2f(recordCoords[2][0] // unitLength + 3, 11 - (recordCoords[2][1] // unitLength))
        glVertex2f(recordCoords[2][0] // unitLength + 3, 11 - (recordCoords[2][1] // unitLength) + 1)
        glVertex2f(recordCoords[2][0] // unitLength + 3, 11 - (recordCoords[2][1] // unitLength) + 1)
        glVertex2f(recordCoords[2][0] // unitLength, 11 - (recordCoords[2][1] // unitLength) + 1)
        glEnd()

        glBegin(GL_QUADS)
        glColor3f(0, 1, 0)
        glVertex2f(6.5, 5.4)
        glVertex2f(7.3, 5.4)
        glVertex2f(7.3, 4.6)
        glVertex2f(6.5, 4.6)
        glEnd()
    if complete[2] == 2:
        shipSize = sizeofShip
        glBegin(GL_LINE_LOOP)
        glColor3f(0, 0.5, 1)
        glVertex2f(recordCoords[2][0] // unitLength, 11 - (recordCoords[2][1] // unitLength))
        glVertex2f(recordCoords[2][0] // unitLength + 1, 11 - (recordCoords[2][1] // unitLength))
        glVertex2f(recordCoords[2][0] // unitLength + 1, 11 - (recordCoords[2][1] // unitLength))
        glVertex2f(recordCoords[2][0] // unitLength + 1, 11 - (recordCoords[2][1] // unitLength) + 3)
        glVertex2f(recordCoords[2][0] // unitLength + 1, 11 - (recordCoords[2][1] // unitLength) + 3)
        glVertex2f(recordCoords[2][0] // unitLength, 11 - (recordCoords[2][1] // unitLength) + 3)
        glEnd()

        glBegin(GL_QUADS)
        glColor3f(0, 1, 0)
        glVertex2f(6.5, 5.4)
        glVertex2f(7.3, 5.4)
        glVertex2f(7.3, 4.6)
        glVertex2f(6.5, 4.6)
        glEnd()

    if complete[3] == 1:
        glBegin(GL_LINE_LOOP)
        glColor3f(0, 0.5, 1)
        glVertex2f(recordCoords[3][0] // unitLength, 11 - (recordCoords[3][1] // unitLength))
        glVertex2f(recordCoords[3][0] // unitLength + 3, 11 - (recordCoords[3][1] // unitLength))
        glVertex2f(recordCoords[3][0] // unitLength + 3, 11 - (recordCoords[3][1] // unitLength))
        glVertex2f(recordCoords[3][0] // unitLength + 3, 11 - (recordCoords[3][1] // unitLength) + 1)
        glVertex2f(recordCoords[3][0] // unitLength + 3, 11 - (recordCoords[3][1] // unitLength) + 1)
        glVertex2f(recordCoords[3][0] // unitLength, 11 - (recordCoords[3][1] // unitLength) + 1)
        glEnd()

        glBegin(GL_QUADS)
        glColor3f(0, 1, 0)
        glVertex2f(6.5, 3.9)
        glVertex2f(7.3, 3.9)
        glVertex2f(7.3, 3.1)
        glVertex2f(6.5, 3.1)
        glEnd()
    if complete[3] == 2:
        shipSize = sizeofShip
        glBegin(GL_LINE_LOOP)
        glColor3f(0, 0.5, 1)
        glVertex2f(recordCoords[3][0] // unitLength, 11 - (recordCoords[3][1] // unitLength))
        glVertex2f(recordCoords[3][0] // unitLength + 1, 11 - (recordCoords[3][1] // unitLength))
        glVertex2f(recordCoords[3][0] // unitLength + 1, 11 - (recordCoords[3][1] // unitLength))
        glVertex2f(recordCoords[3][0] // unitLength + 1, 11 - (recordCoords[3][1] // unitLength) + 3)
        glVertex2f(recordCoords[3][0] // unitLength + 1, 11 - (recordCoords[3][1] // unitLength) + 3)
        glVertex2f(recordCoords[3][0] // unitLength, 11 - (recordCoords[3][1] // unitLength) + 3)
        glEnd()

        glBegin(GL_QUADS)
        glColor3f(0, 1, 0)
        glVertex2f(6.5, 3.9)
        glVertex2f(7.3, 3.9)
        glVertex2f(7.3, 3.1)
        glVertex2f(6.5, 3.1)
        glEnd()

    #  Tüm gemilerin seçimi tamamlandıysa savaş ekranına geçmeyi sağlayan kısım gelir
    if complete[0] != 0 and complete[1] != 0 and complete[2] != 0 and complete[3] != 0:
        warscene = 1

        glBegin(GL_LINE_LOOP)
        glColor3f(1, 0, 0)
        glVertex2f(5, 3)
        glVertex2f(5, 9)
        glVertex2f(5, 9)
        glVertex2f(19, 9)
        glVertex2f(19, 9)
        glVertex2f(19, 3)
        glEnd()

        glBegin(GL_QUADS)
        glColor3f(0.0, 0.098, 0.2)
        glVertex2f(5.01, 3.01)
        glVertex2f(5.01, 8.99)
        glVertex2f(18.99, 8.99)
        glVertex2f(18.99, 3.01)
        glEnd()

        drawText((5.6, 4.55, 0), "S A V A S", (1, 0, 0), 200, "footlight")

    drawText((1.4, 1.15, 0), "SIFIRLA", (255, 255, 255), 40, "footlight")
    drawText((0.5, 10, 0), "Amiral, önce gemiyi ardından harita üzerinde baslangıç", (80, 186, 209), 30, "footlight")
    drawText((0.5, 9.5, 0), "ve bitis noktasını seçin.", (80, 186, 209), 30, "footlight")
    drawText((0.5, 11, 0), "FILO DÜZENI SEÇIMI", (80, 186, 209), 30, "footlight")
    drawText((0, 0, 0), "Filo Personelı Egitim Sistemi ver1.006874", (80, 186, 209), 20)


def drawScene6():
    global allyCoords, enemyCoords, complete, recordCoords, unitLength, firingMode, ids, hit, miss, turn, textures, \
        hitCoords, timer, enemyHitCounter, allyHitCounter

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    #  Izgarayı çizdirir
    drawGrid()
    #  Gemilerin texture'larını bastırır
    for i in range(0, 4):
        a = 0
        if i == 3:
            a = 1
        if complete[i] == 1:
            pushTexture(int(recordCoords[i][0] / unitLength) - 12, abs(11 - int(recordCoords[i][1] / unitLength)), 5 - i + a,
                        1, ids[i][1], 1)
        elif complete[i] == 2:
            pushTexture(int(recordCoords[i][0] / unitLength) - 12, abs(11 - int(recordCoords[i][1] / unitLength)), 1,
                        5 - i + a, ids[i][0], 0)
    #  Savaş sırasında vurulan kısımların sürekli belirgin olmasını sağlayan texture'ı bastırır.
    for k in range(0, len(textures)):
        if textures[k][0] == 0:
            pushTexture(textures[k][1], textures[k][2], 1, 1, miss, 0, (1, 1, 1))
        if textures[k][0] == 1:
            pushTexture(textures[k][1], textures[k][2], 1, 1, hit, 0, (1, 1, 1))
    #  Müttefik gemilerin olduğu kısım yeşil ile belirtilir
    glBegin(GL_QUADS)
    glColor3f(0, 1, 0)
    glVertex2f(0.2, 5.7)
    glVertex2f(0.2, 6.3)
    glVertex2f(0.8, 6.3)
    glVertex2f(0.8, 5.7)
    glEnd()
    #  Düşman gemilerin olduğu kısım kırmızı ile belirtilir
    glBegin(GL_QUADS)
    glColor3f(1, 0, 0)
    glVertex2f(23.2, 5.7)
    glVertex2f(23.2, 6.3)
    glVertex2f(23.8, 6.3)
    glVertex2f(23.8, 5.7)
    glEnd()

    if firingMode == 1 or firingMode == 0:
        #  Oyuncu sırası
        if turn == 0:
            #  Tıklanılan yerin düşman haritasında olursa
            if unitLength * 13 <= hitCoords[0] < unitLength * 23 and unitLength <= hitCoords[1] < unitLength * 11:
                glBegin(GL_LINE_LOOP)
                glColor3f(1, 0, 0)
                glVertex2f(hitCoords[0] // unitLength, 11 - (hitCoords[1] // unitLength))
                glVertex2f((hitCoords[0] // unitLength) + 1, 11 - (hitCoords[1] // unitLength))
                glVertex2f((hitCoords[0] // unitLength) + 1, 11 - (hitCoords[1] // unitLength))
                glVertex2f((hitCoords[0] // unitLength) + 1, 11 - (hitCoords[1] // unitLength) + 1)
                glVertex2f((hitCoords[0] // unitLength) + 1, 11 - (hitCoords[1] // unitLength) + 1)
                glVertex2f(hitCoords[0] // unitLength, 11 - (hitCoords[1] // unitLength) + 1)
                glEnd()
                #  Eğer vurulan yerde düşman gemisi varsa
                if enemyCoords[int(hitCoords[0] // unitLength) - 13][10 - int(hitCoords[1] // unitLength)] == 1:
                    pushTexture(hitCoords[0] // unitLength, 11 - (hitCoords[1] // unitLength), 1, 1, hit, 0, (1, 1, 1))
                    textures.append([1, hitCoords[0] // unitLength, 11 - (hitCoords[1] // unitLength)])
                    turn = 0
                    allyHitCounter += 1
                    enemyCoords[int(hitCoords[0] // unitLength) - 13][10 - int(hitCoords[1] // unitLength)] = 2
                #  Eğer vurulan yerde düşman gemisi yoksa
                elif enemyCoords[int(hitCoords[0] // unitLength) - 13][10 - int(hitCoords[1] // unitLength)] == 0:
                    pushTexture(hitCoords[0] // unitLength, 11 - (hitCoords[1] // unitLength), 1, 1, miss, 0, (1, 1, 1))
                    textures.append([0, hitCoords[0] // unitLength, 11 - (hitCoords[1] // unitLength)])
                    turn = 1
        #  Bilgisayar sırası
        if turn == 1:
            #  Rastgele koordinat seçimi
            randomX = randint(0, 9)
            randomY = randint(0, 9)
            #  Eğer vurulan yer bir daha vurulursa, bu hitCounter'ı artırmaz
            control = 0
            while control != 1:
                glBegin(GL_LINE_LOOP)
                glColor3f(1, 0, 0)
                glVertex2f(randomX + 1, randomY + 1)
                glVertex2f(randomX + 1, randomY + 2)
                glVertex2f(randomX + 1, randomY + 2)
                glVertex2f(randomX + 2, randomY + 2)
                glVertex2f(randomX + 2, randomY + 2)
                glVertex2f(randomX + 2, randomY + 1)
                glEnd()
                #  Vurulan yer gemiye isabet ettiyse
                if allyCoords[randomX][randomY] == 1:
                    pushTexture(randomX + 1, randomY + 1, 1, 1, hit, 0, (1, 1, 1))
                    textures.append([1, randomX + 1, randomY + 1])
                    turn = 1
                    enemyHitCounter += 1
                    allyCoords[randomX][randomY] = 2
                    print(enemyHitCounter)
                    control = 1
                #  Vurulan yer gemiye isabet etmediyse
                elif allyCoords[randomX][randomY] == 0:
                    pushTexture(randomX + 1, randomY + 1, 1, 1, miss, 0, (1, 1, 1))
                    textures.append([0, randomX + 1, randomY + 1])
                    turn = 0
                    control = 1
                #  Vurulan yer tekrar vurulursa
                else:
                    randomX = randint(0, 9)
                    randomY = randint(0, 9)

    drawText((0, 0, 0), "Filo Personelı Egitim Sistemi ver1.006874", (80, 186, 209), 20)


def drawScene7():
    global win

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if win == 1:
        drawText((3.5, 9, 0), "K", (0, 255, 0, 0), 145)
        drawText((5.25, 9, 0), "A", (0, 255, 0, 0), 145)
        drawText((7, 9, 0), "Z", (0, 255, 0, 0), 145)
        drawText((9, 9, 0), "A", (0, 255, 0, 0), 145)
        drawText((11, 9, 0), "N", (0, 255, 0, 0), 145)
        drawText((13, 9, 0), "D", (0, 255, 0, 0), 145)
        drawText((15.05, 9, 0), "I", (0, 255, 0, 0), 145)
        drawText((16.5, 9, 0), "N", (0, 255, 0, 0), 145)
        drawText((18.5, 9, 0), "I", (0, 255, 0, 0), 145)
        drawText((19.5, 9, 0), "Z", (0, 255, 0, 0), 145)

    if win == 0:
        drawText((2.5, 9, 0), "K", (255, 0, 0, 0), 145)
        drawText((4.25, 9, 0), "A", (255, 0, 0, 0), 145)
        drawText((6, 9, 0), "Y", (255, 0, 0, 0), 145)
        drawText((7.75, 9, 0), "B", (255, 0, 0, 0), 145)
        drawText((9.75, 9, 0), "E", (255, 0, 0, 0), 145)
        drawText((11.75, 9, 0), "T", (255, 0, 0, 0), 145)
        drawText((13.75, 9, 0), "T", (255, 0, 0, 0), 145)
        drawText((15.5, 9, 0), "I", (255, 0, 0, 0), 145)
        drawText((16.5, 9, 0), "N", (255, 0, 0, 0), 145)
        drawText((18.5, 9, 0), "I", (255, 0, 0, 0), 145)
        drawText((19.5, 9, 0), "Z", (255, 0, 0, 0), 145)

    glColor3f(1, 1, 1)
    glBegin(GL_LINE_LOOP)
    glVertex2f(9.5, 5)
    glVertex2f(9.5, 7)
    glVertex2f(9.5, 7)
    glVertex2f(14.5, 7)
    glVertex2f(14.5, 7)
    glVertex2f(14.5, 5)
    glEnd()
    drawText((10.05, 5.5, 0), "TEKRAR", (80, 186, 209), 75)

    glBegin(GL_LINE_LOOP)
    glVertex2f(10.5, 4)
    glVertex2f(13.5, 4)
    glVertex2f(13.5, 4)
    glVertex2f(13.5, 3)
    glVertex2f(13.5, 3)
    glVertex2f(10.5, 3)
    glEnd()
    drawText((11.2, 3.2, 0), "ÇIKIŞ", (80, 186, 209), 50)

    drawText((0, 0, 0), "Filo Personelı Egitim Sistemi ver1.006874", (80, 186, 209), 20)


def display():
    global scene

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if scene == 0:
        drawScene0()
    elif scene == 1:
        drawScene1()
    elif scene == 2:
        drawScene2()
    elif scene == 3:
        drawScene3()
    elif scene == 4:
        drawScene4()
    elif scene == 5:
        drawScene5()
    elif scene == 6:
        drawScene6()
    elif scene == 7:
        drawScene7()

    glutSwapBuffers()


"""
        if scene == 0:
        drawScene0()
    elif scene == 1:
        drawScene1()
    elif scene == 2:
        drawScene2()
    elif scene == 3:
        drawScene3()
    elif scene == 4:
        drawScene4()
    elif scene == 5:
        drawScene5()
    elif scene == 6:
        drawScene6()
    elif scene == 7:
        drawScene7()
"""


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(W, H)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Battleship")
    glutReshapeFunc(cantResize)  # Pencere boyutu değiştirilse bile şekiller değişmiyor.
    glutDisplayFunc(display)
    glutMouseFunc(mouse)
    #  glutIdleFunc(display)
    init()
    glutMainLoop()


main()
