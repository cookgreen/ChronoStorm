import pygame
from game.ui.widget import Widget

class Label(Widget):
    """文本标签控件"""
    def __init__(self, name, x, y, width, height, text, text_align, font_size, text_color=(255, 255, 255)):
        super().__init__(name, x, y, width, height)
        self.text = text
        self.text_color = text_color
        self.text_align = text_align
        self.font_size = font_size
        self.font = pygame.font.SysFont("arial", font_size, bold=True)

    def draw(self, surface):
        if not self.is_visible: return
        
        if self.text:
            text_surf = self.font.render(self.text, True, self.text_color)
            
            text_rect = text_surf.get_rect(midleft=(self.absolute_rect.centerx, self.absolute_rect.centery))
            if self.text_align == "center":
                text_rect = text_surf.get_rect(center=(self.absolute_rect.centerx, self.absolute_rect.centery))
            elif self.text_align == "left":
                text_rect = text_surf.get_rect(midleft=(self.absolute_rect.left, self.absolute_rect.centery))
            elif self.text_align == "right":
                text_rect = text_surf.get_rect(midright=(self.absolute_rect.right, self.absolute_rect.centery))
            
            surface.blit(text_surf, text_rect)
            
        super().draw(surface)