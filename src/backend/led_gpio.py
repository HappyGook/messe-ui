import RPi.GPIO as GPIO
import time
import logging

# ----------------------
# Logging setup
# ----------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ----------------------
# Pin setup
# ----------------------
LED_PINS = {"red": 16, "green": 20, "blue": 21}


def setup_pins():
    """Initialize GPIO pins for output."""
    GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
    GPIO.setwarnings(False)
    for color, pin in LED_PINS.items():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # start off
    logger.info("Pins initialized: %s", LED_PINS)


def set_color(r: bool, g: bool, b: bool):
    """Set LED color by turning on/off individual color pins."""
    GPIO.output(LED_PINS["red"], GPIO.HIGH if r else GPIO.LOW)
    GPIO.output(LED_PINS["green"], GPIO.HIGH if g else GPIO.LOW)
    GPIO.output(LED_PINS["blue"], GPIO.HIGH if b else GPIO.LOW)


def blink_color(color: tuple[bool, bool, bool], duration: float = 0.5, times: int = 3):
    """Blink a color on and off."""
    for _ in range(times):
        set_color(*color)
        time.sleep(duration)
        set_color(False, False, False)
        time.sleep(duration)


def cleanup():
    """Reset all GPIO pins."""
    set_color(False, False, False)
    GPIO.cleanup()
    logger.info("GPIO cleanup complete")


# ----------------------
# Main test
# ----------------------
if __name__ == "__main__":
    try:
        setup_pins()
        set_color(False, False, False)
        time.sleep(2)

        logger.info("Testing GREEN")
        set_color(False, True, False)
        time.sleep(2)

        logger.info("Testing RED")
        set_color(True, False, False)
        time.sleep(2)

        logger.info("Blink BLUE")
        blink_color((False, False, True))

        logger.info("All off")
        set_color(False, False, False)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")

    finally:
        cleanup()
