# assets/ui/debug_panel.py

import pygame
import io
from game.ui.panel import Panel
from parsers.shp_parser import ShpParser

class UIScript:
    def __init__(self, ui_manager, root_widget):
        self.ui_manager = ui_manager
        self.root = root_widget
        self.game_state = None
        
        self.btn_power_on = self.root.find_widget("BtnPowerOn")
        self.btn_power_off = self.root.find_widget("BtnPowerOff")
        
        if self.btn_power_on:
            self.btn_power_on.on_click = self.debug_power_on
        if self.btn_power_off:
            self.btn_power_off.on_click = self.debug_power_off

    def debug_power_on(self):
        if self.game_state:
            self.game_state.has_radar_building = True
            self.game_state.has_power = True

    def debug_power_off(self):
        if self.game_state:
            self.game_state.has_radar_building = False
            self.game_state.has_power = False
            
    def update(self, dt, game_state):
        if not game_state: return
        self.game_state = game_state # 实时保存引用