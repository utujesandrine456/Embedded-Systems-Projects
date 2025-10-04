import sys
import math
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

# ----- CONFIG -----
PORT = 'COM10'  # <- change if needed
BAUD = 115200
WINDOW = 200  # number of samples shown

ser = serial.Serial(PORT, BAUD, timeout=1)

pitch_buf = deque(maxlen=WINDOW)
roll_buf = deque(maxlen=WINDOW)
x_idx = deque(maxlen=WINDOW)

fig = plt.figure(figsize=(9, 7))

# Top: time-series lines
ax1 = fig.add_subplot(2, 1, 1)
(line_pitch,) = ax1.plot([], [], label="Pitch (°)")
(line_roll,) = ax1.plot([], [], label="Roll (°)")
ax1.set_xlim(0, WINDOW)
ax1.set_ylim(-90, 90)
ax1.set_xlabel("Samples")
ax1.set_ylabel("Angle (°)")
ax1.set_title("MPU6050 Pitch (Y) & Roll (X)")
ax1.legend(loc="upper right")

# Bottom: 3D tilt table
ax2 = fig.add_subplot(2, 1, 2, projection="3d")
ax2.set_xlim(-2, 2)
ax2.set_ylim(-2, 2)
ax2.set_zlim(-1.5, 1.5)
ax2.set_box_aspect([1, 1, 0.6])
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_zticks([])
ax2.set_title("3D Pitch & Roll-driven Table")

# Tabletop dimensions
w, d, h = 4.0, 2.0, 0.2  # width, depth, thickness
tabletop = np.array([
    [-w/2, -d/2, -h/2],
    [ w/2, -d/2, -h/2],
    [ w/2,  d/2, -h/2],
    [-w/2,  d/2, -h/2],
    [-w/2, -d/2,  h/2],
    [ w/2, -d/2,  h/2],
    [ w/2,  d/2,  h/2],
    [-w/2,  d/2,  h/2]
])

faces_idx = [
    [0, 1, 2, 3],  # bottom
    [4, 5, 6, 7],  # top
    [0, 1, 5, 4],
    [2, 3, 7, 6],
    [1, 2, 6, 5],
    [0, 3, 7, 4]
]

# Table legs (small vertical boxes at corners)
leg_h = 0.8
leg_w = 0.15
leg_verts = []
for x in [-w/2 + leg_w/2, w/2 - leg_w/2]:
    for y in [-d/2 + leg_w/2, d/2 - leg_w/2]:
        leg = np.array([
            [x-leg_w/2, y-leg_w/2, -h/2-leg_h],
            [x+leg_w/2, y-leg_w/2, -h/2-leg_h],
            [x+leg_w/2, y+leg_w/2, -h/2-leg_h],
            [x-leg_w/2, y+leg_w/2, -h/2-leg_h],
            [x-leg_w/2, y-leg_w/2, -h/2],
            [x+leg_w/2, y-leg_w/2, -h/2],
            [x+leg_w/2, y+leg_w/2, -h/2],
            [x-leg_w/2, y+leg_w/2, -h/2],
        ])
        leg_verts.append(leg)

def rotation_matrix(pitch_deg, roll_deg):
    """Build 3D rotation matrix for pitch (X-axis) and roll (Y-axis)."""
    p = math.radians(pitch_deg)
    r = math.radians(roll_deg)

    Rx = np.array([[1, 0, 0],
                   [0, math.cos(p), -math.sin(p)],
                   [0, math.sin(p),  math.cos(p)]])
    Ry = np.array([[math.cos(r), 0, math.sin(r)],
                   [0, 1, 0],
                   [-math.sin(r), 0, math.cos(r)]])
    return Ry @ Rx

# Draw function for box from vertices
def make_box_faces(verts):
    return [[verts[i] for i in face] for face in faces_idx]

# Initialize table
table_faces = make_box_faces(tabletop)
colors = ["red", "lightblue", "gray", "gray", "gray", "gray"]  # bottom red, top blue
table3d = Poly3DCollection(table_faces, facecolors=colors, edgecolor="k", alpha=0.9)
ax2.add_collection3d(table3d)

legs3d = []
for leg in leg_verts:
    lf = make_box_faces(leg)
    leg_poly = Poly3DCollection(lf, facecolors="dimgray", edgecolor="k", alpha=0.9)
    legs3d.append(leg_poly)
    ax2.add_collection3d(leg_poly)

def parse_line(line):
    try:
        parts = line.strip().split(',')
        if len(parts) != 2:
            return None, None
        pitch = float(parts[0])
        roll = float(parts[1])
        return pitch, roll
    except:
        return None, None

def init():
    line_pitch.set_data([], [])
    line_roll.set_data([], [])
    return (line_pitch, line_roll, table3d, *legs3d)

def update(frame):
    for _ in range(5):
        raw = ser.readline().decode(errors="ignore")
        if not raw:
            break
        pitch, roll = parse_line(raw)
        if pitch is None:
            continue
        pitch_buf.append(pitch)
        roll_buf.append(roll)
        x_idx.append(len(x_idx) + 1 if x_idx else 1)

    xs = list(range(len(x_idx)))
    line_pitch.set_data(xs, list(pitch_buf))
    line_roll.set_data(xs, list(roll_buf))
    ax1.set_xlim(max(0, len(xs)-WINDOW), max(WINDOW, len(xs)))

    if pitch_buf and roll_buf:
        R = rotation_matrix(pitch_buf[-1], roll_buf[-1])

        # Rotate tabletop
        rotated_table = tabletop @ R.T
        table3d.set_verts(make_box_faces(rotated_table))

        # Rotate legs
        for leg, leg_poly in zip(leg_verts, legs3d):
            rotated_leg = leg @ R.T
            leg_poly.set_verts(make_box_faces(rotated_leg))

    return (line_pitch, line_roll, table3d, *legs3d)

ani = animation.FuncAnimation(fig, update, init_func=init, interval=30, blit=False)
plt.tight_layout()
plt.show()






