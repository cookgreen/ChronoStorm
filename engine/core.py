import pygame
import os
import sys
import ra2mix
from config.config_loader import game_config
from game.world.world import World
from game.entities.unit import Unit
from game.entities.building import Building
from game.world.map import IsometricMap
from game.ui.ui_manager import UIManager
from parsers.pal_parser import PalParser
from parsers.shp_parser import ShpParser
from parsers.mix_parser import MixParser
from engine.asset_manager import AssetManager

class DummyGameState:
    def __init__(self):
        self.player_credits = 10000
        self.has_radar = True
        self.has_radar_building = False
        self.has_power = False

class EngineCore:
    def __init__(self):
        pygame.init()
        win_cfg = game_config.settings["window"]
        self.screen = pygame.display.set_mode((win_cfg["width"], win_cfg["height"]), pygame.FULLSCREEN | pygame.SRCALPHA)
        pygame.display.set_caption("ChronoStorm Engine")
        self.clock = pygame.time.Clock()
        self.fps = win_cfg["fps"]
        self.running = True
        
        self.font = pygame.font.SysFont("arial", 18)
        
        self.game_state = DummyGameState()

        print("Loading Assets...")
        
        self.assets = AssetManager()
        
        ra2_mix_filepath = "assets/mix/ra2.mix" 
        lang_mix_filepath = "assets/mix/lang.mix" 
        ra2md_mix_filepath = "assets/mix/ra2md.mix" 
        langmd_mix_filepath = "assets/mix/langmd.mix" 
        
        # 1. 挂载根目录的主干包
        self.assets.mount_from_filepath(ra2_mix_filepath, "ra2.mix")
        
        sub_mixes = ["cache.mix", "conquer.mix", "generic.mix", "isogen.mix", 
                     "isosnow.mix", "isosnow.mix", "isotemp.mix", "isourb.mix",
                     "load.mix", "local.mix", "netural.mix", "sidec01.mix", "sidec02.mix",
                     "sidenc01.mix", "sidenc02.mix", "sno.mix", "snow.mix", "tem.mix",
                     "temperat.mix", "urb.mix", "urban.mix"]
        for mix_name in sub_mixes:
            mix_bytes = self.assets.get_file(mix_name)
            if mix_bytes:
                self.assets.mount_from_bytes(mix_bytes, mix_name)
        
        sidebar_pal_bytes = self.assets.get_file("sidebar.pal")
        unittem_pal_bytes = self.assets.get_file("unittem.pal")
        isotem_pal_bytes = self.assets.get_file("unittem.pal")
        cons_shp_bytes = self.assets.get_file("cons.shp")
        ngpowr_shp_bytes = self.assets.get_file("ngpowr.shp")
        ngcnst_shp_bytes = self.assets.get_file("ngcnst.shp")
        ggcnst_shp_bytes = self.assets.get_file("ggcnst.shp")
        ggrefn_shp_bytes = self.assets.get_file("ggrefn.shp")

        self.sidebar_pal = PalParser(sidebar_pal_bytes)
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

        self.sidebar_ui = UIManager(self.assets, self.sidebar_pal.colors)
        self.sidebar_ui.load_from_xml("data/sidebar_sov.xml")

        self.debug_ui = UIManager(self.assets, self.sidebar_pal.colors)
        self.debug_ui.load_from_xml("data/debug_panel.xml")

    
    def get_file_bytes(self, mix_data, filename):
        for k, v in mix_data.items():
            if k.lower() == filename.lower():
                return v
        raise FileNotFoundError(f"在 MIX 包中找不到文件: {filename}")

    def handle_events(self):
        """集中处理事件，并计算 UI 阻断"""
        mouse_pos = pygame.mouse.get_pos()
        # 核心：判断鼠标是否悬停在任意 UI 元素上
        
        is_ui_hovered = False
        for event in pygame.event.get():
            is_ui_hovered = self.sidebar_ui.handle_event(event, mouse_pos)
            is_ui_hovered = self.debug_ui.handle_event(event, mouse_pos)
            
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if is_ui_hovered:
                        # TODO: 在这里触发 VScrollLabel 或按钮的点击事件
                        pass
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
            
        if pygame.mouse.get_pressed()[2]: # 点鼠标右键扣钱
            self.game_state.player_credits -= 10
            
        self.sidebar_ui.update(dt, self.game_state)
        self.debug_ui.update(dt, self.game_state)

    def draw(self, mouse_pos):
        """画面渲染"""
        self.screen.fill((20, 20, 20))

        # 渲染底层地图
        self.game_world.draw(self.screen)

        # 渲染调试信息
        info_text = f"Mouse: {mouse_pos} | Grid: {self.game_world.hovered_grid}"
        text_surf = self.font.render(info_text, True, (255, 255, 255))
        self.screen.blit(text_surf, (10, 10))
        
        self.sidebar_ui.draw(self.screen)
        self.debug_ui.draw(self.screen)

        pygame.display.flip()

    def run(self):
        """启动游戏主循环"""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0 
            
            mouse_pos, is_ui_hovered = self.handle_events()
            self.update(dt, mouse_pos, is_ui_hovered)
            self.draw(mouse_pos)
            
        pygame.quit()
        sys.exit()