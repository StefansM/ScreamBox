# External module imports
import threading
import RPi.GPIO as GPIO
import time


class Flasher:
    def __init__(self):
        self.should_flash = False
        self.led_pin = 23  # Broadcom pin 23 (P1 pin 16)

        self.init_GPIO()

    def init_GPIO(self):
        # Pin Definitons:
        self.should_flash = False

        # Pin Setup:
        GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
        GPIO.setup(self.led_pin, GPIO.OUT)  # LED pin set as output

        # Initial state for LEDs:
        GPIO.output(self.led_pin, GPIO.LOW)

        threading.Thread(target=self.__run_flash).start()

    def flash(self):
        self.should_flash = True

    def stop(self):
        self.should_flash = False

    def __run_flash(self):
        try:
            while self.should_flash:
                GPIO.output(self.led_pin, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(self.led_pin, GPIO.LOW)
                time.sleep(0.5)
        except KeyboardInterrupt:
            GPIO.cleanup()  # cleanup all GPIO