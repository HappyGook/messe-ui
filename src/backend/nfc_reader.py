#!/usr/bin/env python
# import libraries
import gpiozero
from joyit-mfrc522 import SimpleMFRC522
import time
import threading

# initialize object for rfid module
reader = SimpleMFRC522()

#class to store NFC
class NFCState:
    def __init__(self):
        self.last_read = {
            "id": None
        }
        self.lock = threading.Lock()

    def update(self, nfc_id):
        with self.lock:
            self.last_read = {
                "id": nfc_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"[NFC] New card detected: {nfc_id} at {self.last_read['timestamp']}")

    def get_reading(self):
        with self.lock:
            return dict(self.last_read)

nfc_state = NFCState()

# Function to continuously read NFC tags
def read_nfc():
    print("[NFC] Reader started. Waiting for tags...")
    try:
        while True:
            id = reader.read_id_no_block()
            if id:
                nfc_state.update(id)
                # delay to prevent too frequent readings of the same card
                time.sleep(0.5)
            else:
                # delay when no card is present to prevent CPU overload
                time.sleep(0.1)

    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\n[NFC] Reader stopped.")