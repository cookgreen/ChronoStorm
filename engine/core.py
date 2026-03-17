import pygame
import sys
from config.config_loader import game_config
from game.world import IsometricMap

class EngineCore:
    def __init__(self):
        pygame.init()
        win_cfg = game_config.settings["window"]
        self.screen = pygame.display.set_mode((win_cfg["width"], win_cfg["height"]))
        pygame.display.set_caption(win_cfg["title"])
        self.clock = pygame.time.Clock()
        self.fps = win_cfg["fps"]
        self.running = True

        # 初始化游戏地图
        # 将网格偏移到屏幕中心偏左的位置，给右侧 UI 留出空间
        map_offset_x = win_cfg["width"] // 2 - 100
        self.game_world = IsometricMap(rows=20, cols=20, offset_x=map_offset_x, offset_y=100)

        # 模拟侧边栏 UI 的碰撞盒
        self.sidebar_rect = pygame.Rect(win_cfg["width"] - 200, 0, 200, win_cfg["height"])
        
        # 用于调试的字体
        self.font = pygame.font.SysFont(None, 24)

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