import logging
import gpiozero
from joyit_mfrc522 import SimpleMFRC522
import time
import threading

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize multiple readers
readers = {
    "reader1": SimpleMFRC522(pin_ce=24),  # First reader
    "reader2": SimpleMFRC522(pin_ce=12),  # Second reader
    "reader3": SimpleMFRC522(pin_ce=8), # Third reader
    "reader4": SimpleMFRC522(pin_ce=23), # Fourth reader
    "reader5": SimpleMFRC522(pin_ce=18)  # Fifth reader
}

class NFCState:
    def __init__(self):
        self.last_reads: dict[str, dict[str, str | None]] = {
            reader_name: {
                "id": None,
                "timestamp": None
            } for reader_name in readers.keys()
        }
        self.lock = threading.Lock()
        logger.info("NFCState initialized with multiple readers")

    def update(self, reader_name: str, nfc_id: int | str) -> None:
        with self.lock:
            if reader_name not in self.last_reads:
                logger.error(f"Invalid reader name: {reader_name}")
                return

            nfc_id = str(nfc_id)
            self.last_reads[reader_name] = {
                "id": nfc_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            logger.debug(f"Raw NFC card detected on {reader_name} - ID: {nfc_id}")

    def get_reading(self, reader_name: str | None = None) -> dict:
        with self.lock:
            if reader_name is not None:
                if reader_name not in self.last_reads:
                    logger.error(f"Invalid reader name: {reader_name}")
                    return {}
                logger.debug(f"Current NFC state for {reader_name}: {self.last_reads[reader_name]}")
                return dict(self.last_reads[reader_name])
            else:
                logger.debug(f"Current NFC state for all readers: {self.last_reads}")
                return dict(self.last_reads)

nfc_state = NFCState()

# Function to continuously read from a specific NFC reader
def read_nfc_from_reader(reader_name, reader):
    logger.info(f"NFC Reader {reader_name} starting...")
    try:
        while True:
            try:
                logger.debug(f"Attempting to read card on {reader_name}...")
                id, text = reader.read()
                if id:
                    logger.info(f"Successfully read card on {reader_name} - ID: {id}")
                    nfc_state.update(reader_name, id)
                    time.sleep(0.5)
                else:
                    logger.debug(f"No card detected on {reader_name}")
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error reading NFC on {reader_name}: {str(e)}")
                time.sleep(1)

    except KeyboardInterrupt:
        logger.info(f"NFC Reader {reader_name} stopping (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"Critical error in read_nfc for {reader_name}: {str(e)}")
    finally:
        try:
            reader.cleanup()
            logger.info(f"NFC Reader {reader_name} cleaned up")
        except:
            pass

# Function to test a specific reader
def test_reader(reader_name, reader):
    logger.info(f"Testing NFC reader {reader_name}...")
    try:
        id, text = reader.read()
        logger.info(f"Test read successful on {reader_name} - ID: {id}, Text: {text}")
        return True
    except Exception as e:
        logger.error(f"Test read failed on {reader_name}: {str(e)}")
        return False

if __name__ == "__main__":
    # Test all readers
    working_readers = {name: reader for name, reader in readers.items()
                       if test_reader(name, reader)}

    if working_readers:
        logger.info(f"Starting continuous reading for {len(working_readers)} working readers...")
        # Create threads for each working reader
        threads = []
        for reader_name, reader in working_readers.items():
            thread = threading.Thread(target=read_nfc_from_reader,
                                      args=(reader_name, reader),
                                      daemon=True)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("Stopping all readers...")
    else:
        logger.error("No working readers found!")
