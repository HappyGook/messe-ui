from gpiozero import RGBLED
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
# LED configuration
# ----------------------
# Assign GPIO pins for single RGB LED per satellite
# TODO: Decide which pins are LEDs on
LED_PINS = {"red": 16, "green": 20, "blue": 21}

class LEDController:
    def __init__(self):
        try:
            self.led = RGBLED(
                red=LED_PINS["red"],
                green=LED_PINS["green"],
                blue=LED_PINS["blue"],
                active_high=True
            )
            self.led.off()
            logger.info("LED initialized")
        except Exception as e:
            logger.error(f"Failed to initialize LED: {e}")
            self.led = None

    def set_color(self, color: tuple[float, float, float]) -> None:
        """Set LED color (RGB values between 0-1)."""
        if not self.led:
            logger.error("LED not initialized")
            return
        try:
            self.led.color = color
        except Exception as e:
            logger.error(f"Error setting LED color: {e}")

    def blink_color(self, color: tuple[float, float, float], duration: float = 0.5, times: int = 3) -> None:
        """Blink LED a few times with given color."""
        if not self.led:
            return
        for _ in range(times):
            self.set_color(color)
            time.sleep(duration)
            self.led.off()
            time.sleep(duration)

    def turn_off(self) -> None:
        """Turn off LED."""
        if self.led:
            self.led.off()

    def cleanup(self) -> None:
        """Cleanup GPIO on exit."""
        if self.led:
            self.led.close()
            logger.info("LED cleaned up")


# ----------------------
# Test function
# ----------------------
if __name__ == "__main__":
    controller = LEDController()
    try:
        controller.turn_off()
        logger.info("Testing LED: GREEN")
        controller.set_color((0, 1, 0))
        time.sleep(2)

        logger.info("Testing LED: RED")
        controller.set_color((1, 0, 0))
        time.sleep(2)

        logger.info("Blink BLUE")
        controller.blink_color((0, 0, 1))

    finally:
        controller.cleanup()
