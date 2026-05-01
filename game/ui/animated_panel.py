import pygame
from game.ui.widget import Widget

class AnimatedPanel(Widget):
    def __init__(self, name, x, y, width, height, shp_frames=None):
        super().__init__(name, x, y, width, height)
        self.frames = shp_frames or []
        self.current_frame = 0
        self.anim_direction = 0  
        self.fps = 15  
        self.time_accumulator = 0.0
        
        self.minimap_surface = None 
        
        self.show_children_only_when_open = True

    def play(self):
        self.anim_direction = 1

    def reverse(self):
        self.anim_direction = -1

    def update(self, dt):
        if self.anim_direction != 0 and self.frames:
            self.time_accumulator += dt
            frame_duration = 1.0 / self.fps
            
            if self.time_accumulator >= frame_duration:
                self.time_accumulator -= frame_duration
                self.current_frame += self.anim_direction
                
                if self.current_frame >= len(self.frames) - 1:
                    self.current_frame = len(self.frames) - 1
                    self.anim_direction = 0
                    
                elif self.current_frame <= 0:
                    self.current_frame = 0
                    self.anim_direction = 0
                    self.minimap_surface = None 
                    
        if self.show_children_only_when_open:
            for child in self.children:
                # 只有雷达完全打开，子里面的东西才能被看见、被点击
                child.set_visible(self.is_fully_open)

        for child in self.children:
            if hasattr(child, 'update'):
                child.update(dt)

    def draw(self, surface):
        if not self.is_visible: return
        
        if self.frames:
            img = self.frames[self.current_frame]
            scaled_img = pygame.transform.scale(img, (self.absolute_rect.width, self.absolute_rect.height))
            surface.blit(scaled_img, self.absolute_rect.topleft)
            
        if self.current_frame == len(self.frames) - 1 and self.minimap_surface:
            minimap_rect = self.minimap_surface.get_rect(center=self.absolute_rect.center)
            surface.blit(self.minimap_surface, minimap_rect)
            
        super().draw(surface)