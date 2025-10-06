🌀 GY-521 Ball Collecting Coins Game
🚀 Developed by Team EmbedCore
🎯 Overview

GY-521 Ball Collecting Coins is a fun and interactive motion-controlled game that connects Arduino + MPU6050 (GY-521) with Python (Pygame).
You tilt the sensor in real life to move a ball on the screen and collect coins — all in real-time!

Win the game by collecting 10 coins before time runs out ⏱️.
It’s not just a game — it’s physics, sensors, and fun all in one package!

🕹️ How to Play

Hold your MPU6050 sensor connected to your Arduino.

Tilt it:

➡️ Right tilt → Ball moves right

⬅️ Left tilt → Ball moves left

⬆️ Forward tilt → Ball moves up

⬇️ Backward tilt → Ball moves down

Collect as many yellow coins 🪙 as you can before time runs out.

Score 10 points to Win 🎉.

If time runs out before you reach 10 points, you Lose 😢.

⚙️ Features

✅ Real-time motion control using MPU6050 (GY-521)
✅ Smooth ball movement via accelerometer data
✅ Random coin spawning for dynamic gameplay
✅ Live score and timer display
✅ Winning & losing conditions
✅ Expandable to include:

🕹️ Button-based mode switching

🔊 Sound effects for coin collection & victory

🧠 Tech Stack

Hardware: Arduino Uno + MPU6050 Sensor

Communication: Serial (USB)

Software: Python + Pygame

Libraries Used:

pygame

serial

random

time

🧩 Circuit Setup
Component	Connection
MPU6050 VCC	5V
MPU6050 GND	GND
MPU6050 SCL	A5
MPU6050 SDA	A4
Optional Button	Digital Pin 7
🎧 Future Enhancements

🚀 Add sound effects for every coin and victory.
🎨 Add 3D version using Unity or OpenGL.
🌍 Enable multiplayer network play using a game server.

🏆 Team

👩‍💻 Team Name: EmbedCore
💡 Members: Passionate creators blending electronics, coding, and creativity!
