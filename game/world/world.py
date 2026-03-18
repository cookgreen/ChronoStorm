import pygame
from game.world.map import IsometricMap

class World:
    def __init__(self, rows, cols, tile_shp, offset_x=0, offset_y=100):
        self.map = IsometricMap(rows, cols, tile_shp, offset_x, offset_y)
        self.units = []
        self.hovered_grid = (-1, -1)

    def add_unit(self, unit):
        self.units.append(unit)

    def update(self, mouse_pos, is_ui_hovered):
        if is_ui_hovered:
            self.hovered_grid = (-1, -1)
        else:
            self.hovered_grid = self.map.screen_to_grid(mouse_pos[0], mouse_pos[1])
            

    def draw(self, surface):
        self.map.draw_terrain(surface)
        
        if 0 <= self.hovered_grid[0] < self.map.cols and 0 <= self.hovered_grid[1] < self.map.rows:
            hx, hy = self.hovered_grid
            sx, sy = self.map.grid_to_screen(hx, hy)
            pts = [
                (sx, sy - self.map.tile_height/2),
                (sx + self.map.tile_width/2, sy),
                (sx, sy + self.map.tile_height/2),
                (sx - self.map.tile_width/2, sy)
            ]
            pygame.draw.polygon(surface, (255, 255, 255), pts, 2)

        sorted_units = sorted(self.units, key=lambda u: u.grid_x + u.grid_y)
        
        for unit in sorted_units:
            unit.draw(surface, self.map)