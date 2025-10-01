#!/usr/bin/env python
# import libraries
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

# initialize object for rfid module
reader = SimpleMFRC522()

class NFCState:
    def __init__(self):
        self.last_read = {
            "id": None,
            "timestamp": None
        }
        self.lock = threading.Lock()
        logger.info("NFCState initialized")

    def update(self, nfc_id):
        with self.lock:
            nfc_id=str(nfc_id)
            self.last_read = {
                "id": nfc_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            logger.debug(f"Raw NFC card detected - ID: {nfc_id}")

    def get_reading(self):
        with self.lock:
            logger.debug(f"Current NFC state: {self.last_read}")
            return dict(self.last_read)

nfc_state = NFCState()

# Function to continuously read NFC tags
def read_nfc():
    logger.info("NFC Reader starting...")
    try:
        while True:
            try:
                logger.debug("Attempting to read card...")
                # Use regular read() instead of read_id_no_block()
                # since joyit library might have different methods
                id, text = reader.read()
                if id:
                    logger.info(f"Successfully read card - ID: {id}")
                    nfc_state.update(id)
                    time.sleep(0.5)
                else:
                    logger.debug("No card detected")
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error reading NFC: {str(e)}")
                time.sleep(1)  # Wait a bit longer if there's an error

    except KeyboardInterrupt:
        logger.info("NFC Reader stopping (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"Critical error in read_nfc: {str(e)}")
    finally:
        try:
            reader.cleanup()  # Use cleanup() if available in joyit library
            logger.info("NFC Reader cleaned up")
        except:
            pass

# Add a function to check if the reader is working
def test_reader():
    logger.info("Testing NFC reader...")
    try:
        id, text = reader.read()
        logger.info(f"Test read successful - ID: {id}, Text: {text}")
        return True
    except Exception as e:
        logger.error(f"Test read failed: {str(e)}")
        return False

# Optional: Add this to your server startup to test the reader
if __name__ == "__main__":
    if test_reader():
        logger.info("NFC Reader test passed, starting continuous reading...")
        read_nfc()
    else:
        logger.error("NFC Reader test failed!")