import pygame

class Unit:
    def __init__(self, shp_parser, grid_x, grid_y):
        self.shp = shp_parser
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.current_frame = 0 # 未来用来控制 8 方向和动画
        
        # 预留：像素级偏移（用于在网格间平滑移动）
        self.pixel_offset_x = 0
        self.pixel_offset_y = 0

    def draw(self, surface, map_system):
        if not self.shp.frames: return
        
        image = self.shp.frames[self.current_frame]
        
        # 依赖地图系统提供坐标转换
        base_x, base_y = map_system.grid_to_screen(self.grid_x, self.grid_y)
        screen_x = base_x + self.pixel_offset_x
        screen_y = base_y + self.pixel_offset_y
        
        # 动员兵脚踩网格中心，需要将锚点设为 bottom/midbottom
        rect = image.get_rect(midbottom=(screen_x, screen_y + map_system.tile_height/2))
        surface.blit(image, rect)