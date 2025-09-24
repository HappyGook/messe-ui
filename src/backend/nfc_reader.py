#!/usr/bin/env python
import logging
import os
import spidev
from mfrc522 import MFRC522
import time
import threading
from gpiozero import Device
from gpiozero.pins.native import NativeFactory

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set the pin factory to native
Device.pin_factory = NativeFactory()

# Initialize multiple readers with your existing pin assignments
READER_CONFIGS = {
    "reader1": {"cs": 24},  # First reader
    "reader2": {"cs": 12},  # Second reader
    "reader3": {"cs": 8},   # Third reader
    "reader4": {"cs": 23},  # Fourth reader
    "reader5": {"cs": 18}   # Fifth reader
}

def check_spi_setup():
    """Check if SPI is properly configured"""
    import spidev
    available_spi = []

    # List all devices in /dev
    logger.info(f"All devices in /dev: {[f for f in os.listdir('/dev') if 'spi' in f]}")

    # Check specific SPI devices
    for i in range(2):
        device_path = f'/dev/spidev0.{i}'
        if os.path.exists(device_path):
            # Check permissions
            stats = os.stat(device_path)
            logger.info(f"SPI device {device_path} exists with permissions: {oct(stats.st_mode)}")
            available_spi.append(f'spidev0.{i}')

    if not available_spi:
        logger.error("No SPI devices found")
        return False

    # Try to open each available SPI device
    spi = spidev.SpiDev()
    for device_num in range(len(available_spi)):
        try:
            spi.open(0, device_num)
            logger.info(f"Successfully opened SPI bus 0, device {device_num}")
            spi.max_speed_hz = 1000000
            spi.mode = 0
            logger.info(f"Device {device_num} config: speed={spi.max_speed_hz}, mode={spi.mode}")
            spi.close()
        except Exception as e:
            logger.error(f"Failed to open SPI device {device_num}: {str(e)}")

    return bool(available_spi)

def check_spi_kernel_module():
    """Check if SPI kernel module is loaded"""
    try:
        with open('/proc/modules', 'r') as f:
            modules = f.read()
        logger.info("Loaded kernel modules related to SPI:")
        for line in modules.split('\n'):
            if 'spi' in line.lower():
                logger.info(line)
        return 'spi_bcm2835' in modules
    except Exception as e:
        logger.error(f"Error checking kernel modules: {str(e)}")
        return False


class NFCReader:
    def __init__(self, reader_name: str, cs_pin: int):
        self.reader_name = reader_name
        logger.info(f"Attempting to initialize {reader_name} on CS pin {cs_pin}")
        try:
            # Initialize SPI
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)  # Bus 0, Device 0
            self.spi.max_speed_hz = 1000000
            self.spi.mode = 0

            # Create MFRC522 instance with the configured SPI
            self.reader = MFRC522(bus=0, device=cs_pin)

            # Test communication
            version = self.reader.Read_MFRC522(self.reader.VersionReg)
            logger.info(f"{reader_name} Version register: 0x{version:02x}")

        except Exception as e:
            logger.error(f"Error initializing reader on CS pin {cs_pin}")
            logger.error(f"Error details: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            raise



    def read_id(self) -> str | None:
        """Read card ID from the reader."""
        try:
            (status, TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)

            if status == self.reader.MI_OK:
                (status, uid) = self.reader.MFRC522_Anticoll()
                if status == self.reader.MI_OK:
                    # Convert UID bytes to string
                    card_id = ''.join(format(x, '02x') for x in uid)
                    return card_id
            return None
        except Exception as e:
            logger.error(f"Error reading from {self.reader_name}: {str(e)}")
            return None

    def close(self):
        """Clean up resources used by the reader."""
        try:
            self.reader.Close_MFRC522()
        except Exception as e:
            logger.error(f"Error closing reader {self.reader_name}: {str(e)}")

# Initialize readers
readers = {}
for reader_name, config in READER_CONFIGS.items():
    try:
        readers[reader_name] = NFCReader(reader_name, config["cs"])
    except Exception as e:
        logger.error(f"Failed to initialize {reader_name}: {str(e)}")
        readers[reader_name] = None

class NFCState:
    def __init__(self):
        self.last_reads: dict[str, dict[str, str | None]] = {
            reader_name: {
                "id": None,
                "timestamp": None
            } for reader_name in READER_CONFIGS.keys()
        }
        self.lock = threading.Lock()
        logger.info("NFCState initialized with multiple readers")

    def update(self, reader_name: str, nfc_id: str) -> None:
        """Update the state with a new card reading."""
        with self.lock:
            if reader_name not in self.last_reads:
                logger.error(f"Invalid reader name: {reader_name}")
                return

            self.last_reads[reader_name] = {
                "id": nfc_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            logger.debug(f"Raw NFC card detected on {reader_name} - ID: {nfc_id}")

    def get_reading(self, reader_name: str | None = None) -> dict:
        """Get the current state of one or all readers."""
        with self.lock:
            if reader_name is not None:
                if reader_name not in self.last_reads:
                    logger.error(f"Invalid reader name: {reader_name}")
                    return {}
                return dict(self.last_reads[reader_name])
            else:
                return dict(self.last_reads)

def read_nfc_continuously(reader_name: str, reader: NFCReader, nfc_state: NFCState) -> None:
    """Continuous reading function for a specific reader."""
    logger.info(f"NFC Reader {reader_name} starting...")

    while True:
        try:
            card_id = reader.read_id()
            if card_id:
                logger.info(f"Card detected on {reader_name} - ID: {card_id}")
                nfc_state.update(reader_name, card_id)
                time.sleep(0.5)  # Delay after successful read
            else:
                time.sleep(0.1)  # Short delay between polling attempts

        except Exception as e:
            logger.error(f"Error reading NFC on {reader_name}: {str(e)}")
            time.sleep(1)  # Longer delay after error

def test_reader(reader: NFCReader) -> bool:
    """Test if a reader is working correctly."""
    try:
        # Try to read a card
        card_id = reader.read_id()
        if card_id is not None:
            logger.info(f"Test successful on {reader.reader_name} - Read ID: {card_id}")
            return True
        logger.info(f"Test completed on {reader.reader_name} - No card detected")
        return True  # Return True even if no card detected, as the reader is working
    except Exception as e:
        logger.error(f"Test failed on {reader.reader_name}: {str(e)}")
        return False

def main():
    # Create NFCState instance
    nfc_state = NFCState()

    print("Checking SPI kernel module...")
    check_spi_kernel_module()
    print("Checking SPI setup...")
    check_spi_setup()

    # Test all readers first
    working_readers = {name: reader for name, reader in readers.items()
                       if reader is not None and test_reader(reader)}

    if not working_readers:
        logger.error("No working readers found!")
        return

    logger.info(f"Starting continuous reading with {len(working_readers)} working readers")

    # Create and start threads for each working reader
    threads = []
    for reader_name, reader in working_readers.items():
        thread = threading.Thread(
            target=read_nfc_continuously,
            args=(reader_name, reader, nfc_state),
            daemon=True
        )
        threads.append(thread)
        thread.start()

    # Wait for threads and handle shutdown
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        logger.info("Shutting down readers...")
        # Clean up readers
        for reader in working_readers.values():
            reader.close()

if __name__ == "__main__":
    main()