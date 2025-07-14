"""Main file - run the game from here!"""
import pygame

SCREEN_WIDTH = 900
SCREEN_HEIGHT = SCREEN_WIDTH

def main():
    """Main function to run the game from."""
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Flag / Map Game')

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((128, 0, 128)) # background color of interface

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()