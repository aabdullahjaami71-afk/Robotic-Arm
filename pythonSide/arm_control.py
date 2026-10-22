import serial
import time

PORT = '/dev/cu.usbserial-0001' #IMPORTANT: if ur not on MacOS change this to the port your ESP32 is connected to when using arduino IDE
BAUD = 9600
connection = None

def connect():
    global connection
    try:
        connection = serial.Serial(PORT, BAUD, timeout=1)
    except (serial.SerialException, OSError):
        connection = None
        return False
    time.sleep(2)  
    print("Connected to", PORT)
    return True

def send_angles(angles):
    if connection is None:
        raise RuntimeError("Not connected")
    angles = [max(0, min(180, int(a))) for a in angles]
    msg = ",".join(str(a) for a in angles) + "\n"
    connection.write(msg.encode())
    response = connection.readline().decode().strip()
    return response

def disconnect():
    if connection:
        connection.close()