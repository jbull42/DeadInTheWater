import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT = pygame.font.Font('fonts/Righteous-Regular.ttf', 10)

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (120, 120, 120)
BLACK = (0, 0, 0)


class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.selected = False

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            color = DARK_GRAY
        else:
            color = GRAY

        pygame.draw.rect(surface, color, self.rect)
        if self.selected:
            pygame.draw.rect(surface, (252, 94, 3), self.rect, 3)

        text_surface = FONT.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.rect.collidepoint(event.pos):
                    if self.action:
                        self.action()


