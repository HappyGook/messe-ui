from gpiozero import LED
import logging
import time

# ----------------------
# Logging setup
# ----------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ----------------------
# LED configuration (individual pins)
# ----------------------
LED_PINS = {"red": 16, "green": 20, "blue": 21}


class LEDController:
    def __init__(self):
        try:
            self.red = LED(LED_PINS["red"])
            self.green = LED(LED_PINS["green"])
            self.blue = LED(LED_PINS["blue"])
            self.turn_off()
            logger.info("LED pins initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LEDs: {e}")
            self.red = self.green = self.blue = None

    def set_color(self, r: bool, g: bool, b: bool) -> None:
        """Turn on/off each LED pin (True = ON, False = OFF)."""
        if None in (self.red, self.green, self.blue):
            logger.error("LEDs not initialized properly")
            return

        # Turn pins on/off
        if r:
            self.red.on()
        else:
            self.red.off()

        if g:
            self.green.on()
        else:
            self.green.off()

        if b:
            self.blue.on()
        else:
            self.blue.off()

    def blink_color(self, color: tuple[bool, bool, bool], duration: float = 0.5, times: int = 3) -> None:
        """Blink with the given color."""
        for _ in range(times):
            self.set_color(*color)
            time.sleep(duration)
            self.turn_off()
            time.sleep(duration)

    def turn_off(self) -> None:
        """Turn off all LEDs."""
        if self.red:
            self.red.off()
        if self.green:
            self.green.off()
        if self.blue:
            self.blue.off()

    def cleanup(self) -> None:
        """Release GPIO resources."""
        try:
            self.turn_off()
            logger.info("LEDs cleaned up")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# ----------------------
# Test function
# ----------------------
if __name__ == "__main__":
    controller = LEDController()
    try:
        logger.info("Testing GREEN")
        controller.set_color(False, True, False)
        time.sleep(2)

        logger.info("Testing RED")
        controller.set_color(True, False, False)
        time.sleep(2)

        logger.info("Testing BLUE blink")
        controller.blink_color((False, False, True))

        logger.info("All off")
        controller.turn_off()

    except KeyboardInterrupt:
        logger.info("Interrupted by user")

    finally:
        controller.cleanup()
