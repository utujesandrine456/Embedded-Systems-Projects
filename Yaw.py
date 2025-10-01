import sys
import math
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

# ----- CONFIG -----
PORT = 'COM10'   # <- change if needed
BAUD = 115200
WINDOW = 200     # samples shown

ser = serial.Serial(PORT, BAUD, timeout=1)

pitch_buf = deque(maxlen=WINDOW)
roll_buf  = deque(maxlen=WINDOW)
yaw_buf   = deque(maxlen=WINDOW)
x_idx     = deque(maxlen=WINDOW)

fig = plt.figure(figsize=(9, 8))

# -------- Time series (Pitch, Roll, Yaw) --------
ax1 = fig.add_subplot(2, 1, 1)
(line_pitch,) = ax1.plot([], [], label="Pitch (°)")
(line_roll,)  = ax1.plot([], [], label="Roll (°)")
(line_yaw,)   = ax1.plot([], [], label="Yaw (°)")
ax1.set_xlim(0, WINDOW)
ax1.set_ylim(-180, 180)
ax1.set_xlabel("Samples")
ax1.set_ylabel("Angle (°)")
ax1.set_title("MPU6050 Pitch (Y), Roll (X), Yaw (Z)")
ax1.legend(loc="upper right")

# -------- 3D Tilt Table --------
ax2 = fig.add_subplot(2, 1, 2, projection="3d")
ax2.set_xlim(-2, 2)
ax2.set_ylim(-2, 2)
ax2.set_zlim(-1.5, 1.5)
ax2.set_box_aspect([1, 1, 0.6])
ax2.set_xticks([]); ax2.set_yticks([]); ax2.set_zticks([])
ax2.set_title("3D Pitch, Roll & Yaw-driven Table")

# Tabletop vertices
w, d, h = 4.0, 2.0, 0.2
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

# Table legs
leg_h, leg_w = 0.8, 0.15
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

# -------- Helpers --------
def rotation_matrix(pitch_deg, roll_deg, yaw_deg):
    p = math.radians(pitch_deg)
    r = math.radians(roll_deg)
    y = math.radians(yaw_deg)

    Rx = np.array([[1,0,0],
                   [0, math.cos(p), -math.sin(p)],
                   [0, math.sin(p),  math.cos(p)]])
    Ry = np.array([[math.cos(r),0,math.sin(r)],
                   [0,1,0],
                   [-math.sin(r),0,math.cos(r)]])
    Rz = np.array([[math.cos(y), -math.sin(y), 0],
                   [math.sin(y),  math.cos(y), 0],
                   [0,0,1]])
    return Rz @ Ry @ Rx

def make_box_faces(verts):
    return [[verts[i] for i in face] for face in faces_idx]

# Initialize table
table_faces = make_box_faces(tabletop)
colors = ["red", "lightblue", "gray", "gray", "gray", "gray"]
table3d = Poly3DCollection(table_faces, facecolors=colors, edgecolor="k", alpha=0.9)
ax2.add_collection3d(table3d)

legs3d = []
for leg in leg_verts:
    lf = make_box_faces(leg)
    leg_poly = Poly3DCollection(lf, facecolors="dimgray", edgecolor="k", alpha=0.9)
    legs3d.append(leg_poly)
    ax2.add_collection3d(leg_poly)

# -------- Serial Parser --------
def parse_line(line):
    try:
        parts = line.strip().split(',')
        if len(parts) != 3:
            return None, None, None
        pitch = float(parts[0])
        roll  = float(parts[1])
        yaw   = float(parts[2])
        return pitch, roll, yaw
    except:
        return None, None, None

# -------- Animation Init --------
def init():
    line_pitch.set_data([], [])
    line_roll.set_data([], [])
    line_yaw.set_data([], [])
    return (line_pitch, line_roll, line_yaw, table3d, *legs3d)

# -------- Animation Update --------
def update(frame):
    for _ in range(5):
        raw = ser.readline().decode(errors="ignore")
        if not raw:
            break
        pitch, roll, yaw = parse_line(raw)
        if pitch is None:
            continue
        pitch_buf.append(pitch)
        roll_buf.append(roll)
        yaw_buf.append(yaw)
        x_idx.append(len(x_idx) + 1 if x_idx else 1)

    xs = list(range(len(x_idx)))
    line_pitch.set_data(xs, list(pitch_buf))
    line_roll.set_data(xs, list(roll_buf))
    line_yaw.set_data(xs, list(yaw_buf))
    ax1.set_xlim(max(0, len(xs)-WINDOW), max(WINDOW, len(xs)))

    if pitch_buf and roll_buf and yaw_buf:
        R = rotation_matrix(pitch_buf[-1], roll_buf[-1], yaw_buf[-1])
        rotated_table = tabletop @ R.T
        table3d.set_verts(make_box_faces(rotated_table))
        for leg, leg_poly in zip(leg_verts, legs3d):
            rotated_leg = leg @ R.T
            leg_poly.set_verts(make_box_faces(rotated_leg))

    return (line_pitch, line_roll, line_yaw, table3d, *legs3d)

# -------- Run --------
ani = animation.FuncAnimation(fig, update, init_func=init, interval=30, blit=False, cache_frame_data=False)
plt.tight_layout()
plt.show()
