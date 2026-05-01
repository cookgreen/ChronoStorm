import pygame
from game.ui.widget import Widget

class Panel(Widget):
    def __init__(self, name, x, y, width, height, bg_color=(50, 50, 50), shp_frames=None):
        super().__init__(name, x, y, width, height)
        self.bg_color = bg_color
        self.shp_frames = shp_frames

    def draw(self, surface):
        if not self.is_visible: return
        
        if self.shp_frames and len(self.shp_frames) > 0:
            img = self.shp_frames[0]
            scaled_img = pygame.transform.scale(img, (self.absolute_rect.width, self.absolute_rect.height))
            surface.blit(scaled_img, self.absolute_rect.topleft)
        else:
            pygame.draw.rect(surface, self.bg_color, self.absolute_rect)
            pygame.draw.rect(surface, (100, 100, 120), self.absolute_rect, 2)
            
        super().draw(surface)