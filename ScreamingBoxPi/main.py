from scream import Screamer
import time
from poller import Poller


def main():
    screamer = Screamer()
    poller = Poller()

    while True:
        should_scream = poller.poll_api()

        if should_scream:
            screamer.scream()
        else:
            screamer.stop()
        time.sleep(5)


if __name__ == '__main__':
    main()
