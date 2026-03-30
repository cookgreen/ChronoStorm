import pygame
from game.world.map import IsometricMap

class World:
    def __init__(self, rows, cols, tile_shp, offset_x=0, offset_y=100):
        self.map = IsometricMap(rows, cols, tile_shp, offset_x, offset_y)
        self.units = []
        self.buildings = []
        self.hovered_grid = (-1, -1)

    def add_unit(self, unit):
        self.units.append(unit)

    def add_building(self, building):
        self.buildings.append(building)

    def update(self, mouse_pos, is_ui_hovered):
        if is_ui_hovered:
            self.hovered_grid = (-1, -1)
        else:
            self.hovered_grid = self.map.screen_to_grid(mouse_pos[0], mouse_pos[1])
            

    def draw(self, surface):
        # 1. 画底层绿线网格
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
        
        all_entities = []
        all_entities.extend(self.buildings)
        all_entities.extend(self.units)
            
        # 根据 grid_x + grid_y 排序
        all_entities.sort(key=lambda e: e.grid_x + e.grid_y)

        # 3. 按排序后的顺序逐个渲染
        for entity in all_entities:
            entity.draw(surface, self.map)