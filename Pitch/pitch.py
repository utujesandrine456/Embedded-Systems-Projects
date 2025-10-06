import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque


PORT = 'COM10' 
BAUD = 115200
ser = serial.Serial(PORT, BAUD, timeout=1)


pitch_buf = deque(maxlen=200)


fig, ax = plt.subplots()
(line,) = ax.plot([], [], lw=2)
ax.set_ylim(-90, 90)
ax.set_xlim(0, 200)
ax.set_title("MPU6050 Pitch Visualization (2D)")
ax.set_xlabel("Samples")
ax.set_ylabel("Pitch (°)")


def update(frame):
    raw = ser.readline().decode().strip()
    if raw:
        try:
            pitch = float(raw)
            pitch_buf.append(pitch)
        except ValueError:
            pass
    line.set_data(range(len(pitch_buf)), list(pitch_buf))
    return (line,)

ani = animation.FuncAnimation(fig, update, interval=30, blit=True)
plt.show()
