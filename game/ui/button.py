import pygame
from game.ui.widget import Widget

class Button(Widget):
    def __init__(self, name, x, y, width, height, text="", shp_frames=None):
        super().__init__(name, x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.is_pressed = False
        self.shp_frames = shp_frames # 引入 SHP 动画帧数组
        self.font = pygame.font.SysFont("arial", 16)
        self.on_click = None

    def handle_event(self, event, mouse_pos):
        if not self.is_visible: return False
        
        self.is_hovered = self.absolute_rect.collidepoint(mouse_pos)
        
        if self.is_hovered:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.is_pressed = True
                return True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_pressed:
                    if self.on_click: self.on_click()
                self.is_pressed = False
                return True
        else:
            self.is_pressed = False
            
        return False

    def draw(self, surface):
        if not self.is_visible: return
        
        if self.shp_frames and len(self.shp_frames) > 0:
            frame_idx = 0
            if self.is_pressed and len(self.shp_frames) > 2:
                frame_idx = 2 # 按下态
            elif self.is_hovered and len(self.shp_frames) > 1:
                frame_idx = 1 # 悬停态
                
            img = self.shp_frames[frame_idx]
            scaled_img = pygame.transform.scale(img, (self.absolute_rect.width, self.absolute_rect.height))
            surface.blit(scaled_img, self.absolute_rect.topleft)
        else:
            color = (100, 100, 120) if self.is_pressed else ((80, 80, 100) if self.is_hovered else (60, 60, 80))
            pygame.draw.rect(surface, color, self.absolute_rect)
            pygame.draw.rect(surface, (200, 200, 200), self.absolute_rect, 1)
            if self.text:
                text_surf = self.font.render(self.text, True, (255, 255, 255))
                surface.blit(text_surf, text_surf.get_rect(center=self.absolute_rect.center))
        
        super().draw(surface)