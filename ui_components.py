import pygame
from constants import UI_COLORS

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
        
    def draw(self, screen, is_active=False):
        if is_active:
            pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=8)
            pygame.draw.rect(screen, UI_COLORS['button'], self.rect, 2, border_radius=8)
            text_surface = self.font.render(self.text, True, UI_COLORS['button'])
        else:
            color = UI_COLORS['button_hover'] if self.is_hovered else UI_COLORS['button']
            pygame.draw.rect(screen, color, self.rect, border_radius=8)
            text_surface = self.font.render(self.text, True, UI_COLORS['button_text'])
            
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, font, prefix_text="Speed"):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.font = font
        self.prefix_text = prefix_text
        self.dragging = False
        
        self.handle_radius = height // 2
        self.track_rect = pygame.Rect(x + self.handle_radius, y + height//4, 
                                    width - 2*self.handle_radius, height//2)
        self.update_handle_pos()
    
    def update_handle_pos(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_x = self.track_rect.x + ratio * self.track_rect.width
        self.handle_y = self.rect.centery
    
    def draw(self, screen):
        pygame.draw.rect(screen, (226, 232, 240), self.track_rect, border_radius=5)
        pygame.draw.circle(screen, UI_COLORS['button'], (int(self.handle_x), int(self.handle_y)), self.handle_radius)
        
        if self.prefix_text == "Speed":
            val_str = f"{self.val:.1f}x"
        elif self.prefix_text in ("N Nodes", "Branches"):
            val_str = f"{int(self.val)}"
        else:
            val_str = f"{self.val:.2f}"
            
        value_text = f"{self.prefix_text}: {val_str}"
        text_surface = self.font.render(value_text, True, UI_COLORS['text'])
        screen.blit(text_surface, (self.rect.x, self.rect.y - 25))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_rect = pygame.Rect(self.handle_x - self.handle_radius, 
                                    self.handle_y - self.handle_radius,
                                    2 * self.handle_radius, 2 * self.handle_radius)
            if handle_rect.collidepoint(event.pos) or self.track_rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value_from_mouse(event.pos[0])
            return True
        return False
    
    def update_value_from_mouse(self, mouse_x):
        relative_x = max(0, min(self.track_rect.width, mouse_x - self.track_rect.x))
        ratio = relative_x / self.track_rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        self.update_handle_pos()
