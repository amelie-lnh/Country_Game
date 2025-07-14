import pygame
import os
import json
import random
import time

# === SETUP ===
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GRAY = (230, 230, 230)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
FONT_SIZE = 32
FLAG_DIR = "flags"
DATA_FILE = "AllCountries.json"
REGION = "Europe"  # You can make this user-selectable later
NUM_ANSWERS = 4
NUM_QUESTIONS = 10

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Country Flag Quiz")
font = pygame.font.SysFont(None, FONT_SIZE)

# === LOAD DATA ===
with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

region_data = data[REGION]
random.shuffle(region_data)
questions = region_data[:NUM_QUESTIONS]

# === HELPER FUNCTIONS ===

def draw_text(text, pos, color=BLACK):
    label = font.render(text, True, color)
    screen.blit(label, pos)

def load_flag(country_code):
    path = os.path.join(FLAG_DIR, f"{country_code.lower()}.png")
    return pygame.image.load(path)

def get_options(correct_name, all_names, n=4):
    options = [correct_name]
    distractors = list(set(all_names) - {correct_name})
    options += random.sample(distractors, n - 1)
    random.shuffle(options)
    return options

# === GAME STATE ===
question_loaded = False
code = None
correct_name = None
options = []
correct_index = -1

score = 0
current = 0
show_result = False
correct_index = -1
feedback_color = [GRAY] * NUM_ANSWERS
all_country_names = [c["country_name"] for c in region_data]

# === MAIN LOOP ===
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not show_result and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for i in range(NUM_ANSWERS):
                x = 100
                y = 400 + i * 50
                w, h = 600, 40
                if x <= mx <= x + w and y <= my <= y + h:
                    show_result = True
                    if i == correct_index:
                        score += 1
                        feedback_color[i] = GREEN
                    else:
                        feedback_color[i] = RED
                        feedback_color[correct_index] = GREEN
                    pygame.display.flip()
                    pygame.time.delay(1000)
                    feedback_color = [GRAY] * NUM_ANSWERS
                    current += 1
                    show_result = False

    if current >= NUM_QUESTIONS:
        screen.fill(WHITE)
        draw_text(f"Quiz finished! Score: {score}/{NUM_QUESTIONS}", (200, 300))
        question_loaded = False


    else:
        if not question_loaded:
            q = questions[current]
            code = q["country_code"]
            correct_name = q["country_name"]
            options = get_options(correct_name, all_country_names, NUM_ANSWERS)
            correct_index = options.index(correct_name)
            question_loaded = True

        try:
            flag = load_flag(code)
            flag = pygame.transform.scale(flag, (400, 250))
            screen.blit(flag, (200, 100))

        except:
            draw_text("Flag not found", (300, 200))

        for i, option in enumerate(options):
            pygame.draw.rect(screen, feedback_color[i], (100, 400 + i * 50, 600, 40))
            draw_text(option, (110, 410 + i * 50))

        draw_text(f"Question {current + 1}/{NUM_QUESTIONS}", (10, 10))
        draw_text(f"Score: {score}", (WIDTH - 150, 10))

        try:
            flag = load_flag(code)
            flag = pygame.transform.scale(flag, (400, 250))
            screen.blit(flag, (200, 100))

        except:
            draw_text("Flag not found", (300, 200))

        for i, option in enumerate(options):
            pygame.draw.rect(screen, feedback_color[i], (100, 400 + i * 50, 600, 40))
            draw_text(option, (110, 410 + i * 50))

        draw_text(f"Question {current+1}/{NUM_QUESTIONS}", (10, 10))
        draw_text(f"Score: {score}", (WIDTH - 150, 10))

    pygame.display.flip()
    clock.tick(1)

pygame.quit()
