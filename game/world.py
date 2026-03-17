import pygame

class IsometricMap:
    def __init__(self, rows, cols, tile_width=64, tile_height=32, offset_x=0, offset_y=100):
        self.rows = rows
        self.cols = cols
        self.tile_width = tile_width
        self.tile_height = tile_height
        
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        self.hovered_grid = (-1, -1)

    def grid_to_screen(self, grid_x, grid_y):
        screen_x = (grid_x - grid_y) * (self.tile_width / 2) + self.offset_x
        screen_y = (grid_x + grid_y) * (self.tile_height / 2) + self.offset_y
        return screen_x, screen_y

    def screen_to_grid(self, screen_x, screen_y):
        adj_x = screen_x - self.offset_x
        adj_y = screen_y - self.offset_y
        
        grid_x = (adj_x / (self.tile_width / 2) + adj_y / (self.tile_height / 2)) / 2
        grid_y = (adj_y / (self.tile_height / 2) - adj_x / (self.tile_width / 2)) / 2
        
        return int(grid_x), int(grid_y)

    def update(self, mouse_pos, is_ui_hovered):
        if is_ui_hovered:
            self.hovered_grid = (-1, -1)
        else:
            self.hovered_grid = self.screen_to_grid(mouse_pos[0], mouse_pos[1])

    def draw(self, surface):
        for x in range(self.cols):
            for y in range(self.rows):
                top = self.grid_to_screen(x, y)
                right = self.grid_to_screen(x + 1, y)
                bottom = self.grid_to_screen(x + 1, y + 1)
                left = self.grid_to_screen(x, y + 1)
                points = [top, right, bottom, left]
                
                if (x, y) == self.hovered_grid and 0 <= x < self.cols and 0 <= y < self.rows:
                    pygame.draw.polygon(surface, (100, 200, 100), points, 0)
                    pygame.draw.polygon(surface, (255, 255, 255), points, 2)
                else:
                    pygame.draw.polygon(surface, (0, 100, 0), points, 1)