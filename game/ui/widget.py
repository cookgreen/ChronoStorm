import pygame

class Widget:
    """所有 UI 控件的基类"""
    def __init__(self, name, x, y, width, height):
        self.name = name
        self.local_rect = pygame.Rect(x, y, width, height)
        self.absolute_rect = pygame.Rect(x, y, width, height) 
        self.children = []
        self.parent = None
        self.is_visible = True

    def add_child(self, child_widget):
        child_widget.parent = self
        child_widget.absolute_rect.x = self.absolute_rect.x + child_widget.local_rect.x
        child_widget.absolute_rect.y = self.absolute_rect.y + child_widget.local_rect.y
        self.children.append(child_widget)

    def handle_event(self, event, mouse_pos):
        if not self.is_visible: return False
        
        for child in reversed(self.children):
            if child.handle_event(event, mouse_pos):
                return True
                
        return False
        
    def find_widget(self, name):
        if self.name == name:
            return self
        for child in self.children:
            result = child.find_widget(name)
            if result:
                return result
        return None
        
    def set_visible(self, visible):
        self.is_visible = visible

    def draw(self, surface):
        if not self.is_visible: return
        for child in self.children:
            child.draw(surface)