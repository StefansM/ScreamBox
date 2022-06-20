import threading
import time
from pygame import mixer


SCREAM_FILE = "Scream.mp3"
SIREN_FILE = "Siren.mp3"
ALARM_FILE = "Alarm.mp3"

class Screamer:
    def __init__(self):
        self.is_screaming = False

        self.mixer = mixer
        mixer.init()
        self.high_channel = mixer.Channel(1)
        self.low_chanel = mixer.Channel(2)
        self.scream_channel = mixer.Channel(3)

        self.alarm_sound = mixer.Sound(ALARM_FILE)
        self.siren_sound = mixer.Sound(SIREN_FILE)
        self.scream_sounds = [mixer.Sound(SCREAM_FILE)]

        threading.Thread(target=self.__run_scream).start()

    def scream(self):
        self.is_screaming = True

    def stop(self):
        print("Phew")
        self.is_screaming = False

    def __run_scream(self):
        print("AAHHH")

        self.scream_channel.play(self.scream_sounds[0], loops=-1)

        timer = 0
        while self.is_screaming:
            if timer == 50:
                self.high_channel.play(self.alarm_sound, loops=-1)

            if timer == 100:
                self.low_chanel.play(self.siren_sound, loops=-1)

            timer += 1
            time.sleep(0.1)

        self.mixer.stop()