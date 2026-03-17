import pygame

class IsometricMap:
    def __init__(self, rows, cols, tile_shp, offset_x=0, offset_y=100):
        self.rows = rows
        self.cols = cols
        self.tile_width = 60
        self.tile_height = 30
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        self.tile_image = tile_shp.frames[0] if tile_shp and tile_shp.frames else None

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

    def draw_terrain(self, surface):
        for x in range(self.cols):
            for y in range(self.rows):
                screen_x, screen_y = self.grid_to_screen(x, y)
                if self.tile_image:
                    rect = self.tile_image.get_rect(center=(screen_x, screen_y))
                    surface.blit(self.tile_image, rect)
                else:
                    # 保底线框
                    top = (screen_x, screen_y - self.tile_height/2)
                    right = (screen_x + self.tile_width/2, screen_y)
                    bottom = (screen_x, screen_y + self.tile_height/2)
                    left = (screen_x - self.tile_width/2, screen_y)
                    pygame.draw.polygon(surface, (0, 100, 0), [top, right, bottom, left], 1)