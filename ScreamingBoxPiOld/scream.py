import threading
import vlc
import time

SCREAM_FILE = "Scream.mp3"

class Screamer:
    def __init__(self):
        self.is_screaming = False
        threading.Thread(target=self.__run_scream()).start()

    def scream(self):
        self.is_screaming = True

    def stop(self):
        print("Phew")
        self.is_screaming = False

    def __run_scream(self):
        while self.is_screaming:
            p = vlc.MediaPlayer("VOXScrm_Wilhelm scream (ID 0477)_BSB.mp3")
            p.play()

            time.sleep(3)