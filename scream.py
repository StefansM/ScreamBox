import vlc


class Screamer:
    def __init__(self):
        self.is_screaming = False

    def scream(self):
        print("AAHHH")
        # blink
        # scream
        p = vlc.MediaPlayer("VOXScrm_Wilhelm scream (ID 0477)_BSB.mp3")
        p.play()

    def stop(self):
        print("Phew")
