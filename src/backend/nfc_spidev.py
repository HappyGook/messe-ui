import spidev
import RPi.GPIO as GPIO
import time

# -----------------------------
# GPIO and SPI setup
# -----------------------------
CS_PINS = [8]  # Add more pins if you want multiple readers
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in CS_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  # deselect

spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, device 0 (CS is manually controlled)
spi.max_speed_hz = 500000  # safe speed for multiple devices

# -----------------------------
# MFRC522 Register addresses
# -----------------------------
CommandReg      = 0x01
ComIEnReg       = 0x02
DivIEnReg       = 0x03
ComIrqReg       = 0x04
DivIrqReg       = 0x05
FIFODataReg     = 0x09
FIFOLevelReg    = 0x0A
BitFramingReg   = 0x0D
ModeReg         = 0x11
TxControlReg    = 0x14
TxASKReg        = 0x15
TModeReg        = 0x2A
TPrescalerReg   = 0x2B
TReloadRegH     = 0x2C
TReloadRegL     = 0x2D
CRCResultRegH   = 0x21
CRCResultRegL   = 0x22

# MFRC522 commands
PCD_IDLE        = 0x00
PCD_MEM         = 0x01
PCD_GENERATE_RANDOM_ID = 0x02
PCD_CALCCRC     = 0x03
PCD_TRANSMIT    = 0x04
PCD_RECEIVE     = 0x08
PCD_TRANSCEIVE  = 0x0C
PCD_SOFTRESET   = 0x0F

# PICC commands
PICC_REQIDL     = 0x26
PICC_ANTICOLL   = 0x93

# -----------------------------
# Low-level SPI functions
# -----------------------------
def select_reader(cs_pin):
    GPIO.output(cs_pin, GPIO.LOW)

def deselect_reader(cs_pin):
    GPIO.output(cs_pin, GPIO.HIGH)

def write_reg(cs_pin, reg, val):
    addr = ((reg << 1) & 0x7E) & 0x7F  # write = MSB 0
    select_reader(cs_pin)
    spi.xfer([addr, val])
    deselect_reader(cs_pin)

def read_reg(cs_pin, reg):
    addr = ((reg << 1) & 0x7E) | 0x80  # read = MSB 1
    select_reader(cs_pin)
    val = spi.xfer([addr, 0])[1]
    deselect_reader(cs_pin)
    return val

def set_bit_mask(cs_pin, reg, mask):
    val = read_reg(cs_pin, reg)
    write_reg(cs_pin, reg, val | mask)

def clear_bit_mask(cs_pin, reg, mask):
    val = read_reg(cs_pin, reg)
    write_reg(cs_pin, reg, val & (~mask))

def reset(cs_pin):
    write_reg(cs_pin, CommandReg, PCD_SOFTRESET)
    time.sleep(0.05)

# -----------------------------
# CRC Calculation
# -----------------------------
def calculate_crc(cs_pin, data):
    write_reg(cs_pin, CommandReg, PCD_IDLE)
    # Clear FIFO
    write_reg(cs_pin, FIFOLevelReg, 0x80)
    for d in data:
        write_reg(cs_pin, FIFODataReg, d)
    write_reg(cs_pin, CommandReg, PCD_CALCCRC)
    # Wait for CRC calculation
    for _ in range(0xFF):
        n = read_reg(cs_pin, DivIrqReg)
        if n & 0x04:
            break
    crc_l = read_reg(cs_pin, CRCResultRegL)
    crc_h = read_reg(cs_pin, CRCResultRegH)
    return [crc_l, crc_h]

# -----------------------------
# Card detection and anticollision
# -----------------------------
def request(cs_pin):
    write_reg(cs_pin, BitFramingReg, 0x07)  # 7 bits (for request)
    write_reg(cs_pin, CommandReg, PCD_TRANSCEIVE)
    write_reg(cs_pin, FIFODataReg, PICC_REQIDL)
    set_bit_mask(cs_pin, BitFramingReg, 0x80)  # Start send
    time.sleep(0.05)
    fifo_level = read_reg(cs_pin, FIFOLevelReg)
    if fifo_level > 0:
        return read_reg(cs_pin, FIFODataReg)
    return None

def anticoll(cs_pin):
    write_reg(cs_pin, BitFramingReg, 0x00)
    write_reg(cs_pin, CommandReg, PCD_TRANSCEIVE)
    write_reg(cs_pin, FIFODataReg, PICC_ANTICOLL)
    write_reg(cs_pin, FIFODataReg, 0x20)
    set_bit_mask(cs_pin, BitFramingReg, 0x80)
    time.sleep(0.05)
    uid = []
    for i in range(5):
        uid.append(read_reg(cs_pin, FIFODataReg))
    return uid

# -----------------------------
# Main loop
# -----------------------------
try:
    for cs_pin in CS_PINS:
        print(f"Resetting reader on CS {cs_pin}")
        reset(cs_pin)

    print("Place NFC card near the reader...")
    while True:
        for cs_pin in CS_PINS:
            uid = anticoll(cs_pin)
            if uid:
                print(f"Reader {cs_pin} detected UID: {[hex(i) for i in uid]}")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting...")
finally:
    spi.close()
    GPIO.cleanup()
