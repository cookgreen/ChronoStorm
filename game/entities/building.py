import pygame

class Building:
    def __init__(self, shp_parser, grid_x, grid_y, width_tiles=2, height_tiles=2):
        self.shp = shp_parser
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.current_frame = 0  # 默认第 0 帧是完好状态的静态建筑
        self.pixel_offset_x = 0
        self.pixel_offset_y = 0

    def draw(self, surface, map_system):
        if not self.shp.frames: 
            return
            
        image = self.shp.frames[self.current_frame]
        
        # 获取建筑左上角锚点格子的屏幕坐标
        base_x, base_y = map_system.grid_to_screen(self.grid_x, self.grid_y)
        
        # 【核心修正】：多格建筑的渲染锚点
        # 等距视角下，2x2 建筑的视觉中心，正好在它左上角格子往下偏移一定高度的地方
        # 我们把图像的 midbottom 对齐到建筑占地的最下方
        anchor_x = base_x + self.pixel_offset_x
        anchor_y = base_y + self.pixel_offset_y + (self.height_tiles * map_system.tile_height // 2)
        
        rect = image.get_rect(midbottom=(anchor_x, anchor_y))
        surface.blit(image, rect)