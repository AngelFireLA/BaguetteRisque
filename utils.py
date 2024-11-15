import pygame
pygame.init()
class Button:
    def __init__(self, text, x=0, y=0, color=(75, 174, 78),
                 highlight_color=(138, 192, 72), click_color=(255, 140, 0), text_color=(255, 255, 255),
                 font_size=50, size=1, corner=False):
        self.text = text
        self.x = x
        self.y = y

        self.font_size = font_size

        self.normal_color = color
        self.highlight_color = highlight_color
        self.click_color = click_color

        self.image_normal = pygame.Surface((200 * size, 100 * size))
        self.image_normal.fill(color)

        self.image_highlighted = pygame.Surface((200 * size, 100 * size))
        self.image_highlighted.fill(highlight_color)

        self.image_clicked = pygame.Surface((200 * size, 100 * size))
        self.image_clicked.fill(click_color)
        self.image = self.image_normal
        self.rect = self.image.get_rect()
        if not corner:
            self.rect.center = (x, y)
        else:
            self.rect.topleft = (x, y)

        self.font = pygame.font.Font(None, self.font_size)
        self.text_surface = self.font.render(self.text, 1, text_color)

        W = self.text_surface.get_width()
        H = self.text_surface.get_height()
        self.image_normal.blit(self.text_surface, ((200 * size - W) // 2, (100 * size - H) // 2))
        self.image_highlighted.blit(self.text_surface, ((200 * size - W) // 2, (100 * size - H) // 2))
        self.image_clicked.blit(self.text_surface, ((200 * size - W) // 2, (100 * size - H) // 2))

        self.click_start = 0
        self.click_duration = 200


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if event.button == 1:
                self.image = self.image_clicked
                self.click_start = pygame.time.get_ticks()
                return True
        if event.type == pygame.MOUSEBUTTONUP and self.rect.collidepoint(event.pos):
            if pygame.time.get_ticks() - self.click_start > self.click_duration:
                self.image = self.image_highlighted
        return False

    def draw(self, surface):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.image != self.image_clicked or (
                    self.image == self.image_clicked and pygame.time.get_ticks() - self.click_start > self.click_duration):
                self.image = self.image_highlighted
        else:
            self.image = self.image_normal

        bordered_image = self.image.copy()

        image_rect = bordered_image.get_rect()

        pygame.draw.rect(bordered_image, (0, 0, 0), image_rect, 2)

        surface.blit(bordered_image, self.rect)


color_dict = {"black": [0, 0, 0], "red": [255, 0, 0], "green": [0, 255, 0], "blue": [0, 0, 255],
              "yellow": [255, 255, 0], "magenta": [255, 0, 255], "cyan": [0, 255, 255], "white": [255, 255, 255],
              "gray": [128, 128, 128], "light gray": [192, 192, 192], "dark gray": [64, 64, 64],
              "light red": [255, 64, 64], "light green": [64, 255, 64]}




def place_text(screen, x, y, text, size, color=None, border=False, corner=False):
    font = pygame.font.Font(pygame.font.get_default_font(), size)
    lines = text.split('\n')

    # Define border and inner color
    border_color = (0, 0, 0)  # Black color for border
    inner_color = color if color else (255, 255, 255)  # White color for inner text

    for i, line in enumerate(lines):
        # Render the text line
        line_surface = font.render(line, True, inner_color)

        # Determine position based on `corner` parameter
        if corner:
            # If `corner` is True, align text to the top-left corner based on `x` and `y`
            if corner == "opposite":
                line_rect = line_surface.get_rect(topright=(x, y + i * size))
            else:
                line_rect = line_surface.get_rect(topleft=(x, y + i * size))
        else:
            # If `corner` is False, center the text as usual
            line_rect = line_surface.get_rect(center=(x, y + i * size))

        if border:
            # Render text with border color for outline
            for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                border_line_surface = font.render(line, True, border_color)
                border_line_rect = border_line_surface.get_rect(topleft=(line_rect.x + dx, line_rect.y + dy))
                screen.blit(border_line_surface, border_line_rect)

        # Render the actual text
        screen.blit(line_surface, line_rect)
