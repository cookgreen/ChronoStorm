# assets/ui/sidebar_sov.py

import pygame
import io
from game.ui.panel import Panel
from parsers.shp_parser import ShpParser

class UIScript:
    def __init__(self, ui_manager, root_widget):
        self.ui_manager = ui_manager
        self.root = root_widget
        
        self.lbl_credit = self.root.find_widget("TextCredit")
        self.btn_repair = self.root.find_widget("BtnRepair")
        self.btn_sell = self.root.find_widget("BtnSell")
        
        self.radar_panel = self.root.find_widget("Radar")
        self.radar_active = False 
        
        if self.btn_repair:
            self.btn_repair.on_click = self.on_repair_clicked
        if self.btn_sell:
            self.btn_sell.on_click = self.on_sell_clicked
            
        self.build_dynamic_sidebar()
        
    def build_dynamic_sidebar(self):
        main_sidebar = self.root.find_widget("MainSidebar")
        
        opt_buttons = self.root.find_widget("OptButtons")
        bottom02 = self.root.find_widget("Bottom02")
        
        if not (main_sidebar and opt_buttons and bottom02):
            print("找不到关键锚点组件，放弃动态填充！")
            return

        start_y = opt_buttons.local_rect.bottom 
        end_y = bottom02.local_rect.top 
        
        # 可用总高度
        available_height = end_y - start_y
        
        unit_height = 50
        panel_count = available_height // unit_height
        remainder = available_height % unit_height

        bg_surface = None
        data = self.ui_manager.assets.get_file("side2.shp")
        if data:
            parser = ShpParser(data, self.ui_manager.pal_colors)
            shp_frames = parser.frames

        for i in range(panel_count):
            current_y = start_y + (i * unit_height)
            
            actual_height = unit_height
            if i == panel_count - 1:
                actual_height += remainder
            
            tile_panel = Panel(
                name=f"Unit_Tile_{i}", 
                x=0, 
                y=current_y, 
                width=168, 
                height=unit_height, 
                shp_frames=shp_frames
            )
            
            main_sidebar.add_child(tile_panel)

    def on_repair_clicked(self):
        print("玩家点击了维修按钮！准备切换鼠标指针状态...")
        
    def on_sell_clicked(self):
        print("玩家点击了变卖按钮！准备切换鼠标指针状态...")

    def update(self, dt, game_state):
        """引擎每帧或逻辑更新时调用，用于刷新动态数据"""
        if not game_state: return
        
        self.radar_panel.update(dt)
        
        # 1. 动态刷新金钱显示
        if self.lbl_credit:
            self.lbl_credit.text = f"${game_state.player_credits}"
            
        # 2. 动态隐藏/显示建筑 Tab 页 (举例：没有雷达时隐藏选项卡)
        # 假设游戏状态里有 has_radar 标志
        # unit_panel = self.root.find_widget("OptButtons")
        # if unit_panel:
        #     unit_panel.set_visible(game_state.has_radar)
        
        should_radar_be_active = game_state.has_radar_building and game_state.has_power
        
        if should_radar_be_active and not self.radar_active:
            self.radar_panel.play()
            self.radar_active = True
            
        elif not should_radar_be_active and self.radar_active:
            self.radar_panel.reverse()
            self.radar_active = False