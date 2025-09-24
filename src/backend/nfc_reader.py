#!/usr/bin/env python
import logging
import time
import threading
from pirc522 import RFID

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use BOARD numbering (physical pins)
READER_CONFIGS = {
    "reader1": {"cs": 18},  # GPIO24 → physical pin 18
    "reader2": {"cs": 32},  # GPIO12 → physical pin 32
    "reader3": {"cs": 24},  # GPIO8  → physical pin 24
    "reader4": {"cs": 16},  # GPIO23 → physical pin 16
    "reader5": {"cs": 12},  # GPIO18 → physical pin 12
}

# Shared reset pin (BOARD numbering)
RST_PIN = 21  # GPIO9 → physical pin 21

class NFCReader:
    def __init__(self, name: str, cs_pin: int, rst_pin: int = RST_PIN):
        self.name = name
        self.cs_pin = cs_pin
        try:
            # Initialize RFID instance with given CE and RST
            self.rdr = RFID(pin_ce=cs_pin, pin_rst=rst_pin)
            logger.info(f"Initialized {name} on CS pin GPIO{cs_pin}")
        except Exception as e:
            logger.error(f"Failed to init {name} on CS GPIO{cs_pin}: {e}")
            self.rdr = None

    def read_id(self):
        """Try to read a card ID from this reader"""
        if not self.rdr:
            return None

        try:
            # Request tag
            (error, data) = self.rdr.request()
            if not error:
                (error, uid) = self.rdr.anticoll()
                if not error and uid:
                    # Convert UID list to hex string
                    return "".join([f"{x:02X}" for x in uid])
        except Exception as e:
            logger.error(f"Error reading {self.name}: {e}")
        return None

    def cleanup(self):
        if self.rdr:
            self.rdr.cleanup()



class NFCState:
    """Keeps the last read per reader"""
    def __init__(self):
        self.last_reads: dict[str, dict[str, str | None]] = {
            name: {"id": None, "timestamp": None}
            for name in READER_CONFIGS.keys()
        }
        self.lock = threading.Lock()

    def update(self, reader_name: str, nfc_id: str):
        with self.lock:
            self.last_reads[reader_name] = {
                "id": nfc_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def get(self, reader_name=None):
        with self.lock:
            if reader_name:
                return dict(self.last_reads.get(reader_name, {}))
            return dict(self.last_reads)


def read_loop(reader: NFCReader, state: NFCState):
    logger.info(f"{reader.name} started polling")
    while True:
        card_id = reader.read_id()
        if card_id:
            logger.info(f"Card {card_id} detected on {reader.name}")
            state.update(reader.name, card_id)
            time.sleep(0.5)  # Debounce
        else:
            time.sleep(0.1)


def main():
    # Init readers
    readers = {
        name: NFCReader(name, cfg["cs"], RST_PIN)
        for name, cfg in READER_CONFIGS.items()
    }

    # Shared state
    nfc_state = NFCState()

    # Start threads
    threads = []
    for r in readers.values():
        if r.rdr:
            t = threading.Thread(target=read_loop, args=(r, nfc_state), daemon=True)
            t.start()
            threads.append(t)

    logger.info("All readers initialized, press Ctrl+C to stop")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping readers...")
        for r in readers.values():
            r.cleanup()


if __name__ == "__main__":
    main()