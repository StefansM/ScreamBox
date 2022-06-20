from scream import Screamer
import screambox_api
import time


def main():
    screamer = Screamer()

    while True:
        should_scream = screambox_api.poll_api()

        if should_scream:
            screamer.scream()
        else:
            screamer.stop()
        time.sleep(0.1)


if __name__ == '__main__':
    main()
