import math
import threading

from gpiozero import RGBLED
import logging
import time

from sat_config import SATELLITE_ID

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
LED_PINS = {"red": 19, "green": 13, "blue": 26}

class LEDController:
    def __init__(self):
        self.idle_active = None
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

    def start_idle_mode(self, start_timestamp):
        self.idle_active = True
        threading.Thread(target=self._idle_loop, args=(start_timestamp,), daemon=True).start()

    def stop_idle_mode(self):
        self.idle_active = False
        self.turn_off()

    def _idle_loop(self, start_ts):
        # Idle mode constants
        SWING = 30
        OFF1 = 5
        RUNNER = 60
        OFF2 = 5

        CYCLE = SWING + OFF1 + RUNNER + OFF2   # = 100 seconds

        while self.idle_active:
            now = time.time()
            t = (now - start_ts) % CYCLE

            # 1: SWING (0–30)
            if t < SWING:
                level = (1 + math.sin(now * 4)) / 2  # smooth breathing
                self.set_color((0, 0, level))

            # 2: OFF (30–35)
            elif t < SWING + OFF1:
                self.turn_off()

            # 3: RUNNER (35–95)
            elif t < SWING + OFF1 + RUNNER:
                phase = int((t - (SWING + OFF1)) % 10)  # 0–9

                if phase < 5:
                    active_index = phase
                else:
                    active_index = 9 - phase

                if active_index == int(SATELLITE_ID[-1]):
                    self.set_color((0, 0, 1))  # BLUE
                else:
                    self.turn_off()

            # 4: OFF (95–100)
            else:
                self.turn_off()

            time.sleep(0.05)  # 20 FPS


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
