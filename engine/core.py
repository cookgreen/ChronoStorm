import pygame
import os
import sys
import ra2mix
from config.config_loader import game_config
from game.world.world import World
from game.entities.unit import Unit
from game.entities.building import Building
from game.world.map import IsometricMap
from parsers.pal_parser import PalParser
from parsers.shp_parser import ShpParser
from parsers.mix_parser import MixParser

class EngineCore:
    def __init__(self):
        pygame.init()
        win_cfg = game_config.settings["window"]
        self.screen = pygame.display.set_mode((win_cfg["width"], win_cfg["height"]))
        pygame.display.set_caption("ChronoStorm Engine")
        self.clock = pygame.time.Clock()
        self.fps = win_cfg["fps"]
        self.running = True
        
        self.font = pygame.font.SysFont("arial", 18)

        print("Loading Assets...")
        
        mix_filepath = "assets/mix/ra2.mix" 
            
        ra2mix_data = MixParser(mix_filepath)
        conquermix_data = MixParser(ra2mix_data.read_file("conquer.mix"))
        cachemix_data = MixParser(ra2mix_data.read_file("cache.mix"))
        genericmix_data = MixParser(ra2mix_data.read_file("generic.mix"))
        
        unittem_pal_bytes = cachemix_data.read_file("unittem.pal")
        isotem_pal_bytes = cachemix_data.read_file("unittem.pal")
        cons_shp_bytes = conquermix_data.read_file("cons.shp")
        ngpowr_shp_bytes = genericmix_data.read_file("ngpowr.shp")
        ngcnst_shp_bytes = genericmix_data.read_file("ngcnst.shp")
        ggcnst_shp_bytes = genericmix_data.read_file("ggcnst.shp")
        ggrefn_shp_bytes = genericmix_data.read_file("ggrefn.shp")

        self.unit_pal = PalParser(unittem_pal_bytes)
        self.conscript_shp = ShpParser(cons_shp_bytes, self.unit_pal.colors)

        self.isotem_pal = PalParser(isotem_pal_bytes)
        self.tesla_rector_shp = ShpParser(ngpowr_shp_bytes, self.isotem_pal.colors)
        self.construction_yard_shp = ShpParser(ngcnst_shp_bytes, self.isotem_pal.colors)
        self.allied_construction_yard_shp = ShpParser(ggcnst_shp_bytes, self.isotem_pal.colors)
        self.allied_refinary_shp = ShpParser(ggrefn_shp_bytes, self.isotem_pal.colors)
        
        self.game_world = World(
            rows=15, 
            cols=15, 
            tile_shp=None, 
            offset_x=400,
            offset_y=150
        )
    
        self.conscript = Unit(self.conscript_shp, grid_x=5, grid_y=5)
        self.reactor = Building(self.tesla_rector_shp, grid_x=7, grid_y=7, width_tiles=2, height_tiles=2)
        self.construction_yard = Building(self.construction_yard_shp, grid_x=6, grid_y=12, width_tiles=3, height_tiles=3)
        self.allied_construction_yard = Building(self.allied_construction_yard_shp, grid_x=9, grid_y=3, width_tiles=3, height_tiles=3)
        self.allied_refinary = Building(self.allied_refinary_shp, grid_x=12, grid_y=12, width_tiles=3, height_tiles=3)
        
        self.game_world.add_unit(self.conscript)
        self.game_world.add_building(self.reactor)
        self.game_world.add_building(self.construction_yard)
        self.game_world.add_building(self.allied_construction_yard)
        self.game_world.add_building(self.allied_refinary)

        self.sidebar_rect = pygame.Rect(win_cfg["width"] - 200, 0, 200, win_cfg["height"])

    
    def get_file_bytes(self, mix_data, filename):
        for k, v in mix_data.items():
            if k.lower() == filename.lower():
                return v
        raise FileNotFoundError(f"在 MIX 包中找不到文件: {filename}")

    def handle_events(self):
        """集中处理事件，并计算 UI 阻断"""
        mouse_pos = pygame.mouse.get_pos()
        # 核心：判断鼠标是否悬停在任意 UI 元素上
        is_ui_hovered = self.sidebar_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if is_ui_hovered:
                        print("UI 层拦截了点击事件！")
                        # TODO: 在这里触发你写的 VScrollLabel 或按钮的点击事件
                    else:
                        h_x, h_y = self.game_world.hovered_grid
                        if 0 <= h_x < self.game_world.map.cols and 0 <= h_y < self.game_world.map.rows:
                            print(f"向地图下发指令，坐标: ({h_x}, {h_y})")

        return mouse_pos, is_ui_hovered

    def update(self, dt, mouse_pos, is_ui_hovered):
        """逻辑更新"""
        # 将鼠标位置和 UI 阻断状态传递给地图
        self.game_world.update(mouse_pos, is_ui_hovered)
        
        # 让动员兵实时追踪鼠标
        if not is_ui_hovered:
            self.conscript.update(mouse_pos, self.game_world.map)

    def draw(self, mouse_pos):
        """画面渲染"""
        self.screen.fill((20, 20, 20))

        # 1. 渲染底层地图
        self.game_world.draw(self.screen)

        # 2. 渲染上层 UI
        pygame.draw.rect(self.screen, (50, 50, 60), self.sidebar_rect)
        pygame.draw.line(self.screen, (100, 100, 120), (self.sidebar_rect.x, 0), (self.sidebar_rect.x, self.sidebar_rect.height), 2)

        # 3. 渲染调试信息
        info_text = f"Mouse: {mouse_pos} | Grid: {self.game_world.hovered_grid}"
        text_surf = self.font.render(info_text, True, (255, 255, 255))
        self.screen.blit(text_surf, (10, 10))

        pygame.display.flip()

    def run(self):
        """启动游戏主循环"""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0 
            
            # 严格遵循 输入 -> 更新 -> 绘制 的流程
            mouse_pos, is_ui_hovered = self.handle_events()
            self.update(dt, mouse_pos, is_ui_hovered)
            self.draw(mouse_pos)
            
        pygame.quit()
        sys.exit()