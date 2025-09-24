import spidev
import RPi.GPIO as GPIO
import time

# Define CS pins for your readers
CS_PINS = [8]  # readers' GPIOs list
GPIO.setmode(GPIO.BCM)
for pin in CS_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  # deselect

# Open SPI bus 0, device 0 (hardware CS doesn't matter if we toggle CS manually)
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 500000  # safe speed

def read_dummy(reader_pin):
    """Send dummy bytes to check communication"""
    GPIO.output(reader_pin, GPIO.LOW)  # select reader
    try:
        tx = [0x02, 0x00]  # example: MFRC522 "Read register" command format
        rx = spi.xfer(tx)
        print(f"Reader on CS {reader_pin}: Sent {tx}, Received {rx}")
    finally:
        GPIO.output(reader_pin, GPIO.HIGH)  # deselect reader

try:
    while True:
        for pin in CS_PINS:
            read_dummy(pin)
        time.sleep(1)

except KeyboardInterrupt:
    spi.close()
    GPIO.cleanup()

if __name__ == "__main__":
    read_dummy(8)