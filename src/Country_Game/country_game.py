import json
import os
from pathlib import Path
import pygame
import random

# Settings
width, height = 800, 600
gray = (230, 230, 230)
green = (0, 200, 0)
red = (200, 0, 0)
black = (0, 0, 0)
font_size = 40
assets_dir = Path("Assets")
flag_dir = assets_dir / "flags_images"
path_file = assets_dir / "Capitals_and_Categories.json"
num_options = 4
num_questions = 10
max_lives = 3

background_img_path = assets_dir / "worldmap.png"
background_img = pygame.image.load(str(background_img_path))
background_img = pygame.transform.scale(background_img, (width, height))

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("World Quiz Game")
font = pygame.font.SysFont(None, font_size)

# Load data
with open(path_file, "r", encoding="utf-8") as f:
    all_data = json.load(f)

# Load heart images (lives)
heart_img_path = assets_dir / "heart.png"
heart_img = pygame.image.load(str(heart_img_path))
heart_img = pygame.transform.scale(heart_img, (32, 32))

# Create a gray version for lost lives:
heart_gray = heart_img.copy()
arr = pygame.surfarray.pixels3d(heart_gray)
arr[:] = (arr * 0.3).astype("uint8")  # darken
del arr

# Game state variables
game_mode = None
difficulty = None
state = "menu"
difficulty_dropdown_open = False


# Helper functions
def draw_text(text, pos, color=black, center=False):
    """Draw text on the screen."""
    label = font.render(text, True, color)
    if center:
        rect = label.get_rect(center=pos)
    else:
        rect = label.get_rect(topleft=pos)
    screen.blit(label, rect)


def draw_button(
    text, rect, selected=False, hover=False, with_arrow=False, open_state=False
):
    """Draw a button with text, hover, selection and optional dropdown arrow."""
    base_color = (200, 0, 0)
    hover_color = (72, 118, 255)
    selected_color = (65, 105, 225)
    shadow_color = (50, 50, 50)

    color = selected_color if selected else (hover_color if hover else base_color)

    # Draw shadow
    shadow_rect = pygame.Rect(rect[0] + 3, rect[1] + 3, rect[2], rect[3])
    pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=12)

    # Draw main button and label
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=12)

    button_font = pygame.font.SysFont("arial", 24, bold=True)
    label = button_font.render(text, True, (255, 255, 255))
    label_rect = label.get_rect()

    arrow_offset = 25 if with_arrow else 0
    label_rect.center = (
        rect[0] + rect[2] // 2 - arrow_offset // 2,
        rect[1] + rect[3] // 2,
    )
    screen.blit(label, label_rect)

    # Draw dropdown arrow
    if with_arrow:
        cx = rect[0] + rect[2] - 25
        cy = rect[1] + rect[3] // 2
        if open_state:
            points = [(cx - 8, cy + 5), (cx + 8, cy + 5), (cx, cy - 5)]
        else:
            points = [(cx - 8, cy - 5), (cx + 8, cy - 5), (cx, cy + 5)]
        pygame.draw.polygon(screen, (255, 255, 255), points)


def draw_lives(lives):
    """Draw heart icons representing player lives."""
    for i in range(max_lives):
        x = width - (i + 1) * 40
        y = 10
        if i < lives:
            screen.blit(heart_img, (x, y))
        else:
            screen.blit(heart_gray, (x, y))


def load_flag(country_code):
    """Load and return the flag image for a given country code."""
    path = os.path.join(flag_dir, f"{country_code.upper()}.png")
    return pygame.image.load(path)


def get_options(correct_name, all_names, n=4):
    """Return a shuffled list of multiple choice options including the correct answer."""
    options = [correct_name]
    distractors = list(set(all_names) - {correct_name})
    options += random.sample(distractors, n - 1)
    random.shuffle(options)
    return options


# Quiz state
current_question = 0
feedback_color = [gray] * num_options
questions = []
question_text = ""
options = []
correct_index = 0
waiting_answer = True
showing_feedback = False
feedback_start_time = 0
feedback_duration = 1500

lives = max_lives
final_score = 0


def load_question(index):
    """Load the current question based on game mode and index."""
    global question_text
    q = questions[index]
    if game_mode == "Flag Quiz":
        code = q["country_code"]
        correct = q["country_name"]
        opts = get_options(correct, all_country_names, num_options)
        correct_idx = opts.index(correct)
        question_text = "Which country is this flag?"
        return code, correct, opts, correct_idx
    elif game_mode == "Capital Quiz":
        code = q["country_code"]
        country = q["country_name"]
        correct = q["capital"]
        opts = get_options(correct, all_capitals, num_options)
        correct_idx = opts.index(correct)
        question_text = f"What is the capital of {country}?"
        return code, correct, opts, correct_idx


# Main loop
clock = pygame.time.Clock()
running = True
block_first_click = False

while running:
    screen.blit(background_img, (0, 0))    # Draw background
    mx, my = pygame.mouse.get_pos()             # Get mouse position

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Exit the game

        # Menu handling
        if state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            # Select game mode
            if 200 <= mx <= 400 and 120 <= my <= 170:
                game_mode = "Flag Quiz"
            if 420 <= mx <= 620 and 120 <= my <= 170:
                game_mode = "Capital Quiz"

            # Open/close difficulty dropdown
            if 300 <= mx <= 500 and 220 <= my <= 260:
                difficulty_dropdown_open = not difficulty_dropdown_open

            # Select difficulty from dropdown
            if difficulty_dropdown_open:
                diffs = ["Easy", "Medium", "Hard"]
                for i, diff in enumerate(diffs):
                    if 300 <= mx <= 500 and 260 + i * 40 <= my <= 300 + i * 40:
                        difficulty = diff
                        difficulty_dropdown_open = False

            # Start game button
            if 300 <= mx <= 500 and 500 <= my <= 550:
                if game_mode and difficulty:
                    region_data = all_data[difficulty]
                    random.shuffle(region_data)
                    questions = region_data[:num_questions]

                    if game_mode == "Flag Quiz":
                        all_country_names = [c["country_name"] for c in region_data]
                        all_capitals = []
                    elif game_mode == "Capital Quiz":
                        all_capitals = [c["capital"] for c in region_data]
                        all_country_names = []

                    current_question = 0
                    feedback_color = [gray] * num_options
                    code, correct_name, options, correct_index = load_question(
                        current_question
                    )
                    waiting_answer = True
                    showing_feedback = False
                    lives = max_lives
                    final_score = 0
                    state = "quiz"
                    block_first_click = True

        # Quiz interactions
        if state == "quiz" and event.type == pygame.MOUSEBUTTONDOWN:
            if block_first_click:
                block_first_click = False
            elif waiting_answer:
                for i in range(num_options):
                    x = 100
                    y = 400 + i * 50
                    w, h = 600, 40
                    if x <= mx <= x + w and y <= my <= y + h:
                        waiting_answer = False
                        showing_feedback = True
                        feedback_start_time = pygame.time.get_ticks()

                        # Update score and feedback color
                        if i == correct_index:
                            final_score += 1
                            feedback_color[i] = green
                        else:
                            lives -= 1
                            feedback_color[i] = red
                            feedback_color[correct_index] = green

    # Drawing
    if state == "menu":
        draw_text("World Quiz Game", (width // 2, 40), black, center=True)

        # Draw game mode buttons
        hover = 200 <= mx <= 400 and 120 <= my <= 170
        draw_button(
            "Flag Quiz",
            (200, 120, 200, 50),
            selected=(game_mode == "Flag Quiz"),
            hover=hover,
        )

        hover = 420 <= mx <= 620 and 120 <= my <= 170
        draw_button(
            "Capital Quiz",
            (420, 120, 200, 50),
            selected=(game_mode == "Capital Quiz"),
            hover=hover,
        )

        # Draw difficulty dropdown button
        hover = 300 <= mx <= 500 and 220 <= my <= 260
        draw_button(
            difficulty if difficulty else "Select Difficulty",
            (300, 220, 200, 40),
            with_arrow=True,
            open_state=difficulty_dropdown_open,
            hover=hover,
        )

        # Draw difficulty options if dropdown is open
        if difficulty_dropdown_open:
            diffs = ["Easy", "Medium", "Hard"]
            for i, diff in enumerate(diffs):
                hover = 300 <= mx <= 500 and 260 + i * 40 <= my <= 300 + i * 40
                draw_button(
                    diff,
                    (300, 260 + i * 40, 200, 40),
                    selected=(difficulty == diff),
                    hover=hover,
                )

        # Draw start button
        hover = 300 <= mx <= 500 and 500 <= my <= 550
        draw_button("START", (300, 500, 200, 50), hover=hover)

    # Move to next question
    elif state == "quiz":
        if showing_feedback:
            now = pygame.time.get_ticks()
            if now - feedback_start_time >= feedback_duration:
                current_question += 1
                feedback_color = [gray] * num_options
                showing_feedback = False
                if current_question < num_questions and lives > 0:
                    code, correct_name, options, correct_index = load_question(
                        current_question
                    )
                    waiting_answer = True

        # Check for game over conditions
        if lives <= 0:
            state = "game_over"
        elif current_question >= num_questions:
            state = "game_over"
        else:
            if game_mode == "Flag Quiz":
                try:
                    flag = load_flag(code)
                    flag = pygame.transform.scale(flag, (400, 250))
                    screen.blit(flag, (200, 100))
                except FileNotFoundError:
                    draw_text("Flag not found", (300, 200))
            elif game_mode == "Capital Quiz":
                draw_text(question_text, (width // 2, 150), black, center=True)

            for i, option in enumerate(options):
                pygame.draw.rect(
                    screen, feedback_color[i], (100, 400 + i * 50, 600, 40)
                )
                draw_text(option, (110, 410 + i * 50))

            # Draw question and lives
            draw_text(f"Question {current_question + 1}/{num_questions}", (10, 10))
            draw_lives(lives)

    elif state == "game_over":
        # Draw game over screen
        draw_text("Game Over!", (width // 2, height // 2 - 60), black, center=True)
        draw_text(
            f"Final Score: {final_score}/{num_questions}",
            (width // 2, height // 2),
            black,
            center=True,
        )

        # Draw play again button
        play_rect = pygame.Rect(width // 2 - 100, height // 2 + 60, 200, 60)
        hover = play_rect.collidepoint(mx, my)
        draw_button("Play Again", play_rect, hover=hover)

        # Restart game if clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            if play_rect.collidepoint(mx, my):
                state = "menu"
                game_mode = None
                difficulty = None

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
