import time

from flasher import Flasher
from scream import Screamer
from poller import Poller

def main():
    screamer = Screamer()
    poller = Poller()
    flasher = Flasher()

    while True:
        should_scream = poller.poll_api()

        if should_scream:
            screamer.scream()
            flasher.flash()
        else:
            screamer.stop()
            flasher.stop()

        time.sleep(5)


if __name__ == '__main__':
    main()
