import serial
import time

PORT = '/dev/cu.usbserial-0001'
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

SERVO_NAMES = ["Base", "Shoulder", "Elbow", "Wrist", "WristRot", "Claw"]

print("Connected. Enter angles for each servo (0-180), or 'q' to quit.")

while True:
    angles = []

    for name in SERVO_NAMES:
        user_input = input(f"{name} angle: ").strip()

        if user_input.lower() == 'q':
            ser.close()
            exit()

        if not user_input.isdigit():
            print("Please enter a whole number between 0 and 180.")
            break  # restart the whole prompt sequence on bad input

        angle = int(user_input)
        if not (0 <= angle <= 180):
            print("Angle must be between 0 and 180.")
            break

        angles.append(angle)

    if len(angles) != len(SERVO_NAMES):
        continue  # one of the inputs failed validation, retry from the top

    msg = ",".join(str(a) for a in angles) + "\n"
    ser.write(msg.encode())

    response = ser.readline().decode().strip()
    if response:
        print("ESP32:", response)

ser.close()