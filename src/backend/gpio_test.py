import RPi.GPIO as GPIO
import time
import logging

# ----------------------
# Logging setup
# ----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ----------------------
# GPIO setup
# ----------------------
# Common usable GPIO pins on most Raspberry Pi models (BCM numbering)
ALL_GPIO_PINS = [2, 3, 4, 5, 6, 7,
                 12, 13, 14, 15, 16, 18, 19,
                 20, 21, 22, 23, 24, 26, 27]

def setup_pins():
    """Initialize all GPIO pins for output."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in ALL_GPIO_PINS:
        try:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        except Exception as e:
            logger.warning(f"Skipping pin {pin}: {e}")
    logger.info("Initialized GPIO pins: %s", ALL_GPIO_PINS)

def test_pins():
    """Turn on each pin for 2 seconds, then off."""
    for pin in ALL_GPIO_PINS:
        try:
            logger.info(f"Setting GPIO {pin} HIGH")
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(2)
            logger.info(f"Setting GPIO {pin} LOW")
            GPIO.output(pin, GPIO.LOW)
        except Exception as e:
            logger.error(f"Error testing pin {pin}: {e}")

def cleanup():
    """Reset all pins on exit."""
    GPIO.cleanup()
    logger.info("GPIO cleanup complete")

# ----------------------
# Main Loop
# ----------------------
if __name__ == "__main__":
    try:
        setup_pins()
        while True:
            test_pins()
            logger.info("Cycle complete. Restarting...\n")
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Interrupted by user. Exiting...")

    finally:
        cleanup()
