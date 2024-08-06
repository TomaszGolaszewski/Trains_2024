import pygame

from global_variables import *


class FixText:
    def __init__(self, coord, text="Base Fix Text", size=20, font="arial", color=LIME):
        """Initialization of the text."""
        font_obj = pygame.font.SysFont(font, size)
        self.coord = coord #.copy()
        self.text_obj = font_obj.render(text, True, color)
        self.text_rect = self.text_obj.get_rect(center=self.coord)

    def draw(self, win):
        """Draw text on the screen."""
        win.blit(self.text_obj, self.text_rect)


class DynamicText(FixText):
    def __init__(self, coord, text="Dynamic Text", size=20, font="arial", color=LIME):
        """Initialization of the text."""
        FixText.__init__(self, coord, text, size, font, color)
        self.font_obj = pygame.font.SysFont(font, size)
        self.text = text
        self.size = size
        self.font = font
        self.color = color

    def set_text(self, text):
        """Set new text and next recalculate object attributes."""
        self.text = text
        self.text_obj = self.font_obj.render(text, True, self.color)
        self.text_rect = self.text_obj.get_rect(center=self.coord)


class BaseButton(FixText):
    def __init__(self, coord, text="Base Button", size=20, font="arial", color=LIME):
        """Initialization of the button."""
        FixText.__init__(self, coord, text, size, font, color)

    def is_inside(self, sample_coord):
        """
        Check if the coordinates are inside the button.
        return True if yes
        """
        if self.text_rect.collidepoint(sample_coord): return True
        else: return False


class AdvancedButton(BaseButton):
    def __init__(self, coord, text="Advanced Button", size=20, font="arial", color=LIME, color_hover=GRAY, color_active=LIME, option=None, width=360, height=48):
        """Initialization of the button."""
        BaseButton.__init__(self, coord, text, size, font, color)
        self.color = color
        self.color_hover = color_hover
        self.color_active = color_active
        self.option = option
        self.hover = False
        self.active = False
        self.frame_rect = pygame.Rect(0, 0, width, height)
        self.frame_rect.center = coord

    def draw(self, win):
        """Draw text on the screen."""
        BaseButton.draw(self, win)
        if self.active:
            pygame.draw.rect(win, self.color_active, self.frame_rect, 3)
        elif self.hover:
            pygame.draw.rect(win, self.color_hover, self.frame_rect, 3)

    def is_inside(self, sample_coord):
        """
        Check if the coordinates are inside the button.
        return True if yes
        """
        if self.frame_rect.collidepoint(sample_coord): return True
        else: return False

    def check_pressing(self, sample_coord):
        """
        Check if the coordinates are inside the button.
        If the button is pressed set self.active on True.
        return True if the button is pressed too
        """
        if self.frame_rect.collidepoint(sample_coord): 
            self.active = True
            return True
        else: 
            self.active = False
            return False
        
    def check_hovering(self, sample_coord):
        """
        Check if the coordinates are inside the button.
        If the cursor is hovering over the button set self.hover on True.
        return True if the button is hovered by mouse too
        """
        if self.frame_rect.collidepoint(sample_coord): 
            self.hover = True
            return True
        else: 
            self.hover = False
            return False
