import smbus2
import time

# Initialize I2C bus
bus = smbus2.SMBus(1)

# I2C address of the Wemos D1 Mini
address = 0x08

try:
    # Write a test byte to the Wemos D1 Mini
    bus.write_byte(address, 0x01)
    time.sleep(0.1)

    # Read the byte back from the Wemos D1 Mini
    data = bus.read_byte(address)
    print(f"Received data: {data}")

except Exception as e:
    print(f"Error: {e}")
