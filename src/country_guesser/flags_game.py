import pygame
import os
import json
import random

# === SETTINGS ===
WIDTH, HEIGHT = 800, 600
#BG_COLOR = (214, 234, 248)   # Light pastel blue background
GRAY = (230, 230, 230)
DARK_GRAY = (180, 180, 180)
HOVER = (200, 220, 240)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
FONT_SIZE = 60
FLAG_DIR = "flags"
DATA_FILE = "Flag_Images/all_countries.json"
NUM_OPTIONS = 4
NUM_QUESTIONS = 10

background_img = pygame.image.load("worldmap.png")  # replace with your image
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("World Quiz Game")
font = pygame.font.SysFont(None, FONT_SIZE)

# === LOAD DATA ===
with open(DATA_FILE, "r", encoding="utf-8") as f:
    all_data = json.load(f)

# === MENU STATE ===
game_mode = None
region = None
difficulty = None
state = "menu"  # "menu" or "quiz"

# Dropdown state
#continent_dropdown_open = False
difficulty_dropdown_open = False

# Difficulty timing
difficulty_times = {
    "Easy": 2000,
    "Medium": 1500,
    "Hard": 800
}

# === HELPER FUNCTIONS ===
def draw_text(text, pos, color=BLACK, center=False):
    label = font.render(text, True, color)
    if center:
        rect = label.get_rect(center=pos)
        screen.blit(label, rect)
    else:
        screen.blit(background_img, (0, 0))



def draw_button(text, rect, selected=False, hover=False, with_arrow=False, open_state=False):
    # Colors
    base_color = (200, 0, 0)
    hover_color = (72, 118, 255)
    selected_color = (65, 105, 225)
    shadow_color = (50, 50, 50)

    # Background color
    color = selected_color if selected else (hover_color if hover else base_color)

    # Shadow
    shadow_rect = pygame.Rect(rect[0] + 3, rect[1] + 3, rect[2], rect[3])
    pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=12)

    # Main button
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=12)

    # Text
    button_font = pygame.font.SysFont("arial", 24, bold=True)  # bigger font
    label = button_font.render(text, True, (255, 255, 255))
    label_rect = label.get_rect()

    # Center text, leave space if arrow exists
    arrow_offset = 25 if with_arrow else 0
    label_rect.center = (rect[0] + rect[2]//2 - arrow_offset//2, rect[1] + rect[3]//2)
    screen.blit(label, label_rect)

    # Dropdown arrow
    if with_arrow:
        cx = rect[0] + rect[2] - 25
        cy = rect[1] + rect[3] // 2
        if open_state:
            points = [(cx - 8, cy + 5), (cx + 8, cy + 5), (cx, cy - 5)]  # up ▲
        else:
            points = [(cx - 8, cy - 5), (cx + 8, cy - 5), (cx, cy + 5)]  # down ▼
        pygame.draw.polygon(screen, (255, 255, 255), points)



def load_flag(country_code):
    path = os.path.join(FLAG_DIR, f"{country_code.lower()}.png")
    return pygame.image.load(path)

def get_options(correct_name, all_names, n=4):
    options = [correct_name]
    distractors = list(set(all_names) - {correct_name})
    options += random.sample(distractors, n - 1)
    random.shuffle(options)
    return options

# === QUIZ STATE (initialized later) ===
score = 0
current_question = 0
feedback_color = [GRAY] * NUM_OPTIONS
questions = []
code = ""
correct_name = ""
options = []
correct_index = 0
waiting_answer = True
showing_feedback = False
feedback_start_time = 0
FEEDBACK_DURATION = 1500

def load_question(index):
    q = questions[index]
    code = q["country_code"]
    correct_name = q["country_name"]
    opts = get_options(correct_name, all_country_names, NUM_OPTIONS)
    correct_idx = opts.index(correct_name)
    return code, correct_name, opts, correct_idx

# === MAIN LOOP ===
clock = pygame.time.Clock()
running = True
block_first_click = False  # Prevent first accidental click after starting quiz

while running:
    screen.blit(background_img, (0, 0))
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # === MENU HANDLING ===
        if state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            # Game Mode (only Flag Quiz for now)
            if 100 <= mx <= 300 and 100 <= my <= 150:
                game_mode = "Flag Quiz"

            # Continent dropdown toggle
            if 100 <= mx <= 300 and 200 <= my <= 240:
                continent_dropdown_open = not continent_dropdown_open
                difficulty_dropdown_open = False

            # Difficulty dropdown toggle
            if 450 <= mx <= 650 and 200 <= my <= 240:
                difficulty_dropdown_open = not difficulty_dropdown_open
                continent_dropdown_open = False

            # Continent selection
            if continent_dropdown_open:
                regions = list(all_data.keys())
                for i, reg in enumerate(regions):
                    if 100 <= mx <= 300 and 240 + i*40 <= my <= 280 + i*40:
                        region = reg
                        continent_dropdown_open = False

            # Difficulty selection
            if difficulty_dropdown_open:
                diffs = ["Easy", "Medium", "Hard"]
                for i, diff in enumerate(diffs):
                    if 450 <= mx <= 650 and 240 + i*40 <= my <= 280 + i*40:
                        difficulty = diff
                        FEEDBACK_DURATION = difficulty_times[diff]
                        difficulty_dropdown_open = False

            # Start button
            if 300 <= mx <= 500 and 500 <= my <= 550:
                if game_mode and region and difficulty:
                    # Initialize quiz
                    region_data = all_data[region]
                    random.shuffle(region_data)
                    questions = region_data[:NUM_QUESTIONS]
                    all_country_names = [c["country_name"] for c in region_data]
                    score = 0
                    current_question = 0
                    feedback_color = [GRAY] * NUM_OPTIONS
                    code, correct_name, options, correct_index = load_question(current_question)
                    waiting_answer = True
                    showing_feedback = False
                    state = "quiz"
                    block_first_click = True  # Block first accidental click

        # === QUIZ HANDLING ===
        if state == "quiz" and event.type == pygame.MOUSEBUTTONDOWN:
            if block_first_click:
                block_first_click = False  # Ignore first click
            elif waiting_answer:
                for i in range(NUM_OPTIONS):
                    x = 100
                    y = 400 + i * 50
                    w, h = 600, 40
                    if x <= mx <= x + w and y <= my <= y + h:
                        waiting_answer = False
                        showing_feedback = True
                        feedback_start_time = pygame.time.get_ticks()

                        if i == correct_index:
                            score += 1
                            feedback_color[i] = GREEN
                        else:
                            feedback_color[i] = RED
                            feedback_color[correct_index] = GREEN

    # === DRAWING ===
    if state == "menu":
        draw_text("World Quiz Game", (WIDTH//2, 40), BLACK, center=True)

        # Game Mode
        hover = 100 <= mx <= 300 and 100 <= my <= 150
        draw_button("Flag Quiz", (100, 100, 200, 50), selected=(game_mode == "Flag Quiz"), hover=hover)

        # Continent dropdown
        #hover = 100 <= mx <= 300 and 200 <= my <= 240
        #draw_button(region if region else "Select Continent", (100, 200, 200, 40),
                  #  with_arrow=True, open_state=continent_dropdown_open, hover=hover)
        #if continent_dropdown_open:
            #regions = list(all_data.keys())
            #for i, reg in enumerate(regions):
               # hover = 100 <= mx <= 300 and 240 + i*40 <= my <= 280 + i*40
                #draw_button(reg, (100, 240 + i*40, 200, 40), selected=(region == reg), hover=hover)

        # Difficulty dropdown
        hover = 450 <= mx <= 650 and 200 <= my <= 240
        draw_button(difficulty if difficulty else "Select Difficulty", (450, 200, 200, 40),
                    with_arrow=True, open_state=difficulty_dropdown_open, hover=hover)
        if difficulty_dropdown_open:
            diffs = ["Easy", "Medium", "Hard"]
            for i, diff in enumerate(diffs):
                hover = 450 <= mx <= 650 and 240 + i*40 <= my <= 280 + i*40
                draw_button(diff, (450, 240 + i*40, 200, 40), selected=(difficulty == diff), hover=hover)

        # Start button
        hover = 300 <= mx <= 500 and 500 <= my <= 550
        draw_button("START", (300, 500, 200, 50), hover=hover)

    elif state == "quiz":
        # Auto move to next question after feedback
        if showing_feedback:
            now = pygame.time.get_ticks()
            if now - feedback_start_time >= FEEDBACK_DURATION:
                current_question += 1
                feedback_color = [GRAY] * NUM_OPTIONS
                showing_feedback = False
                if current_question < NUM_QUESTIONS:
                    code, correct_name, options, correct_index = load_question(current_question)
                    waiting_answer = True

        # End of quiz
        # End of quiz
        if current_question >= NUM_QUESTIONS:
            screen.fill(BG_COLOR)
            draw_text(f"Quiz finished! Score: {score}/{NUM_QUESTIONS}", (WIDTH // 2, HEIGHT // 2 - 40), BLACK,
                      center=True)

            # Play Again button
            play_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 60)
            hover = play_rect.collidepoint(mx, my)
            draw_button("Play Again", play_rect, hover=hover)

            # Handle click on Play Again
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(mx, my):
                    state = "menu"
                    game_mode = None
                    region = None
                    difficulty = None
                    current_question = 0
                    score = 0
                    feedback_color = [GRAY] * NUM_OPTIONS
                    waiting_answer = True
                    showing_feedback = False
                    block_first_click = False

        else:
            try:
                flag = load_flag(code)
                flag = pygame.transform.scale(flag, (400, 250))
                screen.blit(flag, (200, 100))
            except:
                draw_text("Flag not found", (300, 200))

            for i, option in enumerate(options):
                pygame.draw.rect(screen, feedback_color[i], (100, 400 + i * 50, 600, 40))
                draw_text(option, (110, 410 + i * 50))

            draw_text(f"Question {current_question + 1}/{NUM_QUESTIONS}", (10, 10))
            draw_text(f"Score: {score}", (WIDTH - 150, 10))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
