import pygame
import serial
import time
import random
# Connect to Arduino
ser = serial.Serial("COM6", 9600)
time.sleep(2)  # wait for Arduino connection
# Game setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GY-521 Ball Collecting Coins Game")
# Colors
BLACK = (30, 30, 30)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
# Ball setup
ball_radius = 25
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
speed = 5
# Coin setup
coin_radius = 15
coin_x = random.randint(coin_radius, WIDTH - coin_radius)
coin_y = random.randint(coin_radius, HEIGHT - coin_radius)
score = 0
winning_score = 10  # win when score reaches 10
time_limit = 60     # 60 seconds to win
start_time = time.time()
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()
running = True
game_over = False
win = False
while running:
    screen.fill(BLACK)
    current_time = time.time()
    elapsed_time = current_time - start_time
    remaining_time = max(0, int(time_limit - elapsed_time))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if not game_over:
        # Read sensor data from Arduino (skip incomplete lines)
        if ser.in_waiting > 0:
            line = ser.readline().decode(errors='ignore').strip()
            parts = line.split(",")
            # Only process full data lines
            if len(parts) == 3 and all(p.strip().lstrip('-').isdigit() for p in parts):
                ax, ay, az = map(int, parts)
                # Adjust sensitivity if needed
                if ax > 2000:
                    ball_x += speed
                elif ax < -2000:
                    ball_x -= speed
                if ay > 2000:
                    ball_y -= speed  # forward tilt moves up
                elif ay < -2000:
                    ball_y += speed  # backward tilt moves down
        # Keep ball inside window
        ball_x = max(ball_radius, min(WIDTH - ball_radius, ball_x))
        ball_y = max(ball_radius, min(HEIGHT - ball_radius, ball_y))
        # Check for coin collection
        distance = ((ball_x - coin_x)**2 + (ball_y - coin_y)**2) ** 0.5
        if distance < ball_radius + coin_radius:
            score += 1
            coin_x = random.randint(coin_radius, WIDTH - coin_radius)
            coin_y = random.randint(coin_radius, HEIGHT - coin_radius)
        # Check winning condition
        if score >= winning_score:
            game_over = True
            win = True
        # Check failing condition (time out)
        if remaining_time <= 0:
            game_over = True
            win = False
    # Draw ball and coin
    pygame.draw.circle(screen, GREEN, (ball_x, ball_y), ball_radius)
    pygame.draw.circle(screen, YELLOW, (coin_x, coin_y), coin_radius)
    # Draw score and timer
    score_text = font.render(f"Score: {score}", True, WHITE)
    time_text = font.render(f"Time: {remaining_time}s", True, WHITE)
    screen.blit(score_text, (20, 20))
    screen.blit(time_text, (20, 60))
    # Draw game over message
    if game_over:
        if win:
            message = "You Win! :tada:"
            color = GREEN
        else:
            message = "Time's Up! You Lose! :cry:"
            color = RED
        msg_text = font.render(message, True, color)
        screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, HEIGHT // 2 - msg_text.get_height() // 2))
    pygame.display.flip()
    clock.tick(30)
pygame.quit()