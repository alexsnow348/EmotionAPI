from random import randint
import time


class MyFace:
    tracks = []

    def __init__(self, i, xi, yi, max_age):
        self.i = i
        self.x = xi
        self.y = yi
        self.tracks = []
        self.R = randint(0, 255)
        self.G = randint(0, 255)
        self.B = randint(0, 255)
        self.done = False
        self.emotion = []
        self.gender = []
        self.age = 0
        self.max_age = max_age

    def getRGB(self):
        return (self.R, self.G, self.B)

    def getTracks(self):
        return self.tracks

    def getId(self):
        return self.i

    def getX(self):
        return self.x

    def getAge(self):
        return self.age

    def getEmotion(self):
        return self.emotion

    def getGender(self):
        return self.gender

    def getY(self):
        return self.y

    def setDone(self):
        self.done = True

    def age_one(self):
        self.age += 1
        if self.age > self.max_age:
            self.done = True
        return True

    def getDone(self):
        return self.done

    def timedOut(self):
        return self.done

    def age_one(self):
        self.age += 1
        if self.age > self.max_age:
            self.done = True
        return True

    def updateCoords(self, xn, yn):
        self.tracks.append([self.x, self.y])
        self.x = xn
        self.y = yn

    def updateEmotion(self, emotion):
        self.emotion.append(emotion)

    def updateGender(self, gender):
        self.gender.append(gender)
