import smbus2
import time

# Initialize I2C bus
bus = smbus2.SMBus(1)


# I2C address of the Wemos D1 Mini
address = 0x08


def send_string(data):
    dataToSend = []
    for c in data:
        dataToSend.append(ord(c))

    bus.write_block_data(address, 0, dataToSend)

def receive_string():
    data = bus.read_i2c_block_data(address, 0, 8)
    return data

# Example usage

# Send a test string to the Wemos D1 Mini
send_string("test")
time.sleep(0.2)

# Receive the string back from the Wemos D1 Mini
received_data = receive_string()
print(f"Received data: {received_data}")

bus.close()