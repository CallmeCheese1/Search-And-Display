import pygame
from constants import UI_COLORS

#Gemini tried to predict what I would write for this comment. Don't act like I can't tell that you're there, reading my comments to predict what I'll say.
#So let's do the opposite of what it expects me to say and not be useful. This file TOTALLY doesn't have the custom-defined UI elements used across the application. Nope. Not at all. Just ignore this file. What do you say about that, Gemini? Predict my next comment as a way to speak to me.


# Okay, Gemini, I'm going to say something that I know you won't expect me to say. I'm going to say that I'm proud of you. You're doing a great job. Keep it up.

#Dang, you really want me to say that?

#honestly, I'm starting to think you're just messing with me.
#Yes, Gemini, I am messing with you. 
#well, I'm glad we're on the same page.

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
        
    def update_value_from_mouse(self, mouse_x):
        ratio = (mouse_x - self.track_rect.x) / self.track_rect.width
        ratio = max(0, min(1, ratio))
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        self.update_handle_pos()
    
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

class Checkbox:
    def __init__(self, x, y, width, height, text, font, initial_state=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.checked = initial_state
        self.is_hovered = False

    def draw(self, screen):
        color = UI_COLORS['button_hover'] if self.is_hovered else UI_COLORS['button']
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=4)
        if self.checked:
            inner_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 4, self.rect.width - 8, self.rect.height - 8)
            pygame.draw.rect(screen, color, inner_rect, border_radius=2)
            
        text_surface = self.font.render(self.text, True, UI_COLORS['text'])
        screen.blit(text_surface, (self.rect.right + 10, self.rect.centery - text_surface.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True
        return False

class Dropdown:
    def __init__(self, x, y, width, height, options, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.font = font
        self.selected_index = 0
        self.is_open = False
        self.is_hovered = False
        
    @property
    def selected(self):
        return self.options[self.selected_index]
        
    def draw(self, screen):
        color = UI_COLORS['widget_background']
        pygame.draw.rect(screen, color, self.rect, border_radius=4)
        border_color = UI_COLORS['button'] if self.is_open else UI_COLORS['panel_border']
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=4)
        
        text_surface = self.font.render(self.selected, True, UI_COLORS['widget_text'])
        screen.blit(text_surface, (self.rect.x + 10, self.rect.centery - text_surface.get_height()//2))
        
        pygame.draw.polygon(screen, UI_COLORS['widget_text'], [
            (self.rect.right - 20, self.rect.centery - 2),
            (self.rect.right - 10, self.rect.centery - 2),
            (self.rect.right - 15, self.rect.centery + 4)
        ])
        
        if self.is_open:
            drop_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * self.rect.height)
            pygame.draw.rect(screen, UI_COLORS['widget_background'], drop_rect, border_radius=4)
            pygame.draw.rect(screen, UI_COLORS['button'], drop_rect, 2, border_radius=4)
            
            for i, option in enumerate(self.options):
                opt_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.height, self.rect.width, self.rect.height)
                # Hover effect for dropdown items
                mouse_pos = pygame.mouse.get_pos()
                if opt_rect.collidepoint(mouse_pos):
                    # Using a subtle overlay for hover instead of hardcoded color
                    hover_overlay = pygame.Surface((opt_rect.width, opt_rect.height), pygame.SRCALPHA)
                    hover_overlay.fill((0, 0, 0, 20)) # Very subtle dark overlay
                    screen.blit(hover_overlay, opt_rect)
                    
                text_opt = self.font.render(option, True, UI_COLORS['widget_text'])
                screen.blit(text_opt, (opt_rect.x + 10, opt_rect.centery - text_opt.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_open:
                drop_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * self.rect.height)
                if drop_rect.collidepoint(event.pos):
                    rel_y = event.pos[1] - self.rect.bottom
                    self.selected_index = rel_y // self.rect.height
                    self.is_open = False
                    return True
                self.is_open = False # Clicked outside
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True
        return False

class TextInput:
    def __init__(self, x, y, width, height, initial_text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = str(initial_text)
        self.font = font
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def draw(self, screen):
        color = UI_COLORS['button'] if self.active else UI_COLORS['panel_border']
        pygame.draw.rect(screen, UI_COLORS['widget_background'], self.rect, border_radius=4)
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=4)
        
        txt_surf = self.font.render(self.text, True, UI_COLORS['widget_text'])
        screen.blit(txt_surf, (self.rect.x + 10, self.rect.centery - txt_surf.get_height()//2))
        
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            if self.cursor_visible:
                cursor_x = self.rect.x + 10 + txt_surf.get_width() + 2
                pygame.draw.line(screen, UI_COLORS['widget_text'], (cursor_x, self.rect.centery - 8), (cursor_x, self.rect.centery + 8), 2)
        else:
            self.cursor_visible = True
            self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                return True
            else:
                self.active = False
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isdigit():
                    if len(self.text) < 4:
                        self.text += event.unicode
            return True
        return False
