from gpiozero import RGBLED
import logging
from typing import Dict, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# LED GPIO pin configurations for each station
LED_CONFIGS = {
    "station1": {"red": 20, "green": 16, "blue": 21},
    "station2": {"red": 19, "green": 26, "blue": 6},
    "station3": {"red": 27, "green": 13, "blue": 22},
    "station4": {"red": 4, "green": 17, "blue": 3},
    "station5": {"red": 14, "green": 2, "blue": 15}
}

class LEDController:
    def __init__(self):
        self.leds: Dict[str, Optional[RGBLED]] = {}
        self._initialize_leds()
        logger.info("LED Controller initialized")

    def _initialize_leds(self) -> None:
        """Initialize all RGB LEDs with their GPIOs"""
        try:
            for station, pins in LED_CONFIGS.items():
                try:
                    self.leds[station] = RGBLED(
                        red=pins["red"],
                        green=pins["green"],
                        blue=pins["blue"],
                        active_high=True  # common anode LEDs setting, no idea what it means :(
                    )
                    self.leds[station].off()  # Ensure LED starts in off state
                    logger.info(f"Initialized LED for {station}")
                except Exception as e:
                    logger.error(f"Failed to initialize LED for {station}: {str(e)}")
                    self.leds[station] = None
        except Exception as e:
            logger.error(f"Error during LED initialization: {str(e)}")


    def set_color(self, station: str, color: tuple[float, float, float]) -> bool:
        """
        Set the color of station's LED.

        Args:
            station: The station identifier (e.g., 'station1')
            color: RGB tuple with values between 0 and 1 (e.g., (1, 0, 0) for red)

        Returns:
            bool: True if successful, False otherwise
        """
        if station not in self.leds or self.leds[station] is None:
            logger.error(f"Invalid station or LED not initialized: {station}")
            return False

        try:
            self.leds[station].color = color
            logger.debug(f"Set {station} LED to color {color}")
            return True
        except Exception as e:
            logger.error(f"Error setting color for {station}: {str(e)}")
            return False

    def turn_off(self, station: str) -> bool:
        """Turn off the LED for a station"""
        return self.set_color(station, (0, 0, 0))

    def turn_off_all(self) -> None:
        """Turn off all LEDs"""
        for station in self.leds:
            self.turn_off(station)
        logger.info("All LEDs turned off")

    def cleanup(self) -> None:
        """Clean up GPIO resources"""
        try:
            self.turn_off_all()
            for led in self.leds.values():
                if led is not None:
                    led.close()
            logger.info("LED cleanup completed")
        except Exception as e:
            logger.error(f"Error during LED cleanup: {str(e)}")



# test function
def test_leds():
    controller = LEDController()
    try:
        # Test each LED with different colors
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]  # Red, Green, Blue

        for station in LED_CONFIGS.keys():
            logger.info(f"Testing {station}")
            for color in colors:
                controller.set_color(station, color)
                logger.info(f"Set {station} to {color}")
                import time
                time.sleep(1)
            controller.turn_off(station)

    except KeyboardInterrupt:
        logger.info("LED test interrupted")
    finally:
        controller.cleanup()

if __name__ == "__main__":
    test_leds()
