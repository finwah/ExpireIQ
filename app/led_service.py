import platform
import time


class LEDService:
    def __init__(self, pins=(17, 27)):
        self.leds = []
        self.enabled = False

        if platform.system() != "Linux":
            print("LED service disabled: not running on Raspberry Pi.")
            return

        try:
            from gpiozero import LED

            for pin in pins:
                self.leds.append(LED(pin))

            self.enabled = True
            print("LED service enabled.")

        except Exception as e:
            print("LED service disabled:", e)

    def on(self):
        if not self.enabled:
            return

        for led in self.leds:
            led.on()

    def off(self):
        if not self.enabled:
            return

        for led in self.leds:
            led.off()

    def light_for_capture(self, delay=0.25):
        self.on()
        time.sleep(delay)


led_service = LEDService()