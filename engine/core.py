import pygame
import sys
from config.config_loader import game_config
from game.world import IsometricMap
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

        # === 核心加载阶段 ===
        print("Loading Assets...")
        # 1. 加载调色板 (如果没有真实文件，自动生成一个随机彩色的假调色板用于测试)
        
        mix1 = MixParser("assets/ra2.mix")
        mix2 = MixParser("assets/ra2md.mix")
        mix3 = MixParser("assets/language.mix")
        mix4 = MixParser("assets/langmd.mix")
        
        mix1.extract("iso.pal", "assets/iso.pal")
        self.pal = PalParser("assets/iso.pal") 
        if not self.pal.colors:
            self.pal.colors = [(i, (i*5)%255, 100) for i in range(256)]
            self.pal.colors[0] = (0, 0, 0) # 索引0设为透明色

        # 2. 解析 SHP 序列
        # 注意：这里需要你手动放置提取出的文件，或者暂时使用代码里内置的 dummy 占位符
        self.shp_tile = ShpParser("assets/clear1.shp", self.pal.colors) # 原版草地
        self.shp_conscript = ShpParser("assets/e1.shp", self.pal.colors) # 原版动员兵 (e1)

        # 3. 初始化世界地图，注入资源
        map_offset_x = win_cfg["width"] // 2 - 100
        self.game_world = IsometricMap(
            rows=20, cols=20, 
            tile_shp=self.shp_tile, 
            unit_shp=self.shp_conscript,
            offset_x=map_offset_x, offset_y=150
        )

        self.sidebar_rect = pygame.Rect(win_cfg["width"] - 200, 0, 200, win_cfg["height"])

    # handle_events, update, draw, run 等方法保持上一版原样即可...
    # (省略以节省空间，直接使用之前 core.py 里的逻辑)

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
                        if 0 <= h_x < self.game_world.cols and 0 <= h_y < self.game_world.rows:
                            print(f"向地图下发指令，坐标: ({h_x}, {h_y})")

        return mouse_pos, is_ui_hovered

    def update(self, dt, mouse_pos, is_ui_hovered):
        """逻辑更新"""
        # 将鼠标位置和 UI 阻断状态传递给地图
        self.game_world.update(mouse_pos, is_ui_hovered)

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