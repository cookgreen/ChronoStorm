import pygame
import math

class Unit:
    def __init__(self, shp_parser, grid_x, grid_y):
        self.shp = shp_parser
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.current_frame = 0 # 未来用来控制 8 方向和动画
        
        # 预留：像素级偏移（用于在网格间平滑移动）
        self.pixel_offset_x = 0
        self.pixel_offset_y = 0
        
    def update(self, mouse_pos, map_system):
        """逻辑更新：计算鼠标夹角，切换 8 方向朝向"""
        if not self.shp.frames:
            return

        # 1. 获取动员兵在屏幕上的实际中心坐标
        base_x, base_y = map_system.grid_to_screen(self.grid_x, self.grid_y)
        center_x = base_x + self.pixel_offset_x
        center_y = base_y + self.pixel_offset_y

        # 2. 计算鼠标相对单位的差值
        dx = mouse_pos[0] - center_x
        
        # 【关键视差修正】：由于是 2:1 的等距视角，Y轴视觉上被压扁了
        # 我们需要把 Y 轴拉伸回真实的圆，才能算出现实的夹角
        dy = (mouse_pos[1] - center_y) * 2 

        # 3. 使用 atan2 计算弧度，并转换为角度 (-180 到 180)
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        # 4. 角度转换与 8 方向映射
        # RA2 的第 0 帧通常是面向正南(South) 或 正北(North)
        # 我们先将角度规范化到 0-360 度，并顺时针旋转 90 度让 0 度朝上
        normalized_angle = (angle_deg + 90) % 360
        
        # 将 360 度切分成 8 块披萨 (每块 45 度)
        # 加上 22.5 度是为了让 0 度恰好处于“北”这个扇形的中心点
        sector = int((normalized_angle + 22.5) // 45) % 8

        # 5. Westwood 的祖传映射表
        # 如果你发现鼠标指向上，他却往下看，只需要在这里加个固定的偏移量即可，例如: (sector + 4) % 8

        self.current_frame = (8 - sector) % 8

    def draw(self, surface, map_system):
        if not self.shp.frames: 
            return # 如果没解析出图片就跳过
            
        image = self.shp.frames[self.current_frame]
        
        # 找地图系统换算坐标
        base_x, base_y = map_system.grid_to_screen(self.grid_x, self.grid_y)
        screen_x = base_x + self.pixel_offset_x
        screen_y = base_y + self.pixel_offset_y
        
        # 动员兵要脚踩在菱形的中心，所以锚点设为 midbottom 加上半个地砖的高度
        rect = image.get_rect(midbottom=(screen_x, screen_y + map_system.tile_height // 2))
        surface.blit(image, rect)