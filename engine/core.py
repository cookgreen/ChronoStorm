import pygame
import sys
from config.config_loader import game_config

class EngineCore:
    def __init__(self):
        pygame.init()
        
        win_cfg = game_config.settings["window"]
        self.screen = pygame.display.set_mode((win_cfg["width"], win_cfg["height"]))
        pygame.display.set_caption(win_cfg["title"])
        
        self.clock = pygame.time.Clock()
        self.fps = win_cfg["fps"]
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt):
        # game_world.update(dt)
        pass

    def draw(self):
        self.screen.fill((0, 0, 0))
        
        # game_world.draw(self.screen)
        # ui_manager.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0 
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()