# External module imports
import threading
import RPi.GPIO as GPIO
import time


class Flasher:
    def __init__(self):
        self.should_flash = False

        # Pin Definitons:
        self.led_pin = 23  # Broadcom pin 23 (P1 pin 16)
        self.should_flash = False

        # Pin Setup:
        GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
        GPIO.setup(self.led_pin, GPIO.OUT)  # LED pin set as output

        # Initial state for LEDs:
        GPIO.output(self.led_pin, GPIO.LOW)

    def flash(self):
        if not self.should_flash:
            self.should_flash = True
            t = threading.Thread(target=self.__run_flash)
            t.start()

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