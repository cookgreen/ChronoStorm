import xml.etree.ElementTree as ET
import io
import os
import pygame
import importlib

from game.ui.panel import Panel
from game.ui.animated_panel import AnimatedPanel
from game.ui.button import Button
from game.ui.label import Label
from parsers.shp_parser import ShpParser

class UIManager:
    def __init__(self, assets, ui_palette_colors):
        self.root_widgets = []
        self.assets = assets
        self.pal_colors = ui_palette_colors
        
        display_info = pygame.display.Info()
        screen_width = display_info.current_w
        screen_height = display_info.current_h
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.widget_factory = {
            "Panel": self._create_panel,
            "AnimatedPanel": self._create_animated_panel,
            "Button": self._create_button,
            "Label": self._create_label,
        }
        
        self.active_scripts = [] 

    def _get_file_bytes(self, filename):
        return self.assets.get_file(filename)
        
    def _eval_expr(self, expr_str, parent_widget):
        """核心：安全的数学表达式解析沙盒"""
        if not expr_str:
            return 0
            
        # 构建当前控件的上下文环境
        context = {
            "SCREEN_WIDTH": self.screen_width,
            "SCREEN_HEIGHT": self.screen_height,
            "PARENT_WIDTH": parent_widget.local_rect.width if parent_widget else self.screen_width,
            "PARENT_HEIGHT": parent_widget.local_rect.height if parent_widget else self.screen_height
        }
        
        try:
            # 安全措施，防止 XML 注入恶意 Python 代码
            result = eval(str(expr_str), {"__builtins__": None}, context)
            return int(result)
        except Exception as e:
            print(f"UI表达式解析错误: '{expr_str}' -> {e}")
            return 0

    def load_from_xml(self, filepath):
        tree = ET.parse(filepath)
        root = tree.getroot()
        for elem in root:
            # 根节点的 parent 是 None
            widget = self._parse_element(elem, parent_widget=None)
            if widget:
                self.root_widgets.append(widget)
        
        script_file = root.attrib.get("script")
        if script_file:
            script_path = os.path.join(os.path.dirname(filepath), script_file)
            self._load_and_attach_script(script_path)
            
    def _load_and_attach_script(self, script_path):
        """动态加载外部 Python 脚本并实例化"""
        if not os.path.exists(script_path):
            print(f"找不到 UI 脚本文件: {script_path}")
            return
            
        try:
            module_name = os.path.basename(script_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            root_widget = self.root_widgets[0] if self.root_widgets else None
            
            if hasattr(module, 'UIScript'):
                script_instance = module.UIScript(self, root_widget)
                self.active_scripts.append(script_instance)
        except Exception as e:
            print(f"加载 UI 脚本 {script_path} 时发生崩溃: {e}")

    def _parse_element(self, elem, parent_widget):
        tag = elem.tag
        if tag in self.widget_factory:
            widget = self.widget_factory[tag](elem, parent_widget)
            
            if parent_widget:
                parent_widget.add_child(widget)
                
            for child_elem in elem:
                self._parse_element(child_elem, parent_widget=widget)
                
            return widget
        return None

    def _create_panel(self, elem, parent):
        name = elem.attrib.get("name", "unnamed")
        x = self._eval_expr(elem.attrib.get("x", "0"), parent)
        y = self._eval_expr(elem.attrib.get("y", "0"), parent)
        w = self._eval_expr(elem.attrib.get("width", "0"), parent)
        h = self._eval_expr(elem.attrib.get("height", "0"), parent)
        
        bg_image_name = elem.attrib.get("bg_image")
        bg_surface = None
        
        if bg_image_name:
            data = self._get_file_bytes(bg_image_name)
            if data and bg_image_name.lower().endswith(".pcx"):
                bg_surface = pygame.image.load(io.BytesIO(data)).convert_alpha()
            elif data and bg_image_name.lower().endswith(".shp"):
                parser = ShpParser(data, self.pal_colors)
                bg_surface = parser.frames
                
        return Panel(name, x, y, w, h, shp_frames=bg_surface)

    def _create_animated_panel(self, elem, parent):
        name = elem.attrib.get("name", "unnamed")
        x = self._eval_expr(elem.attrib.get("x", "0"), parent)
        y = self._eval_expr(elem.attrib.get("y", "0"), parent)
        w = self._eval_expr(elem.attrib.get("width", "0"), parent)
        h = self._eval_expr(elem.attrib.get("height", "0"), parent)
        
        bg_image_name = elem.attrib.get("bg_image")
        bg_surface = None
        
        if bg_image_name:
            data = self._get_file_bytes(bg_image_name)
            if data and bg_image_name.lower().endswith(".pcx"):
                bg_surface = pygame.image.load(io.BytesIO(data)).convert_alpha()
            elif data and bg_image_name.lower().endswith(".shp"):
                parser = ShpParser(data, self.pal_colors)
                bg_surface = parser.frames
                
        return AnimatedPanel(name, x, y, w, h, shp_frames=bg_surface)

    def _create_button(self, elem, parent):
        name = elem.attrib.get("name", "unnamed")
        x = self._eval_expr(elem.attrib.get("x", "0"), parent)
        y = self._eval_expr(elem.attrib.get("y", "0"), parent)
        w = self._eval_expr(elem.attrib.get("width", "0"), parent)
        h = self._eval_expr(elem.attrib.get("height", "0"), parent)
        text = elem.attrib.get("text", "")
        
        image_name = elem.attrib.get("image")
        shp_frames = None
        
        if image_name:
            data = self._get_file_bytes(image_name)
            if data and image_name.lower().endswith(".shp"):
                parser = ShpParser(data, self.pal_colors)
                shp_frames = parser.frames

        return Button(name, x, y, w, h, text, shp_frames=shp_frames)
        
    def _create_label(self, elem, parent):
        name = elem.attrib.get("name", "unnamed")
        x = self._eval_expr(elem.attrib.get("x", "0"), parent)
        y = self._eval_expr(elem.attrib.get("y", "0"), parent)
        w = self._eval_expr(elem.attrib.get("width", "0"), parent)
        h = self._eval_expr(elem.attrib.get("height", "0"), parent)
        text = elem.attrib.get("text", "")
        text_align = elem.attrib.get("text_align", "")
        font_size = int(elem.attrib.get("font_size", ""))
        
        color_str = elem.attrib.get("text_color", "255,255,255")
        color = tuple(map(int, color_str.split(',')))
        
        return Label(name, x, y, w, h, text, text_align, font_size, text_color=color)

    def handle_event(self, event, mouse_pos):
        for widget in reversed(self.root_widgets):
            if widget.handle_event(event, mouse_pos):
                return True
        return False
        
    def update(self, dt, game_state):
        """向所有挂载的脚本广播状态更新"""
        for script in self.active_scripts:
            if hasattr(script, 'update'):
                script.update(dt, game_state)

    def draw(self, surface):
        for widget in self.root_widgets:
            widget.draw(surface)