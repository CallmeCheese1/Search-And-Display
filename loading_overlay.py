import pygame
import math
from constants import TOTAL_WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS

#You know that really cool loading circle that appears while you run the benchmarks? Yeah. Welcome. This is that!
class LoadingOverlay:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        # Pre-create overlay surface
        self.overlay = pygame.Surface((TOTAL_WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(100) # Slightly more secondary transparency
        self.overlay.fill((30, 41, 59)) # Slate gray background matching the UI theme
        self.base_surface = None
        
    def draw(self, angle):
        # 0. Draw base dashboard if provided to maintain consistent transparency
        if self.base_surface:
            self.screen.blit(self.base_surface, (0, 0))
            
        # 1. Background Overlay
        self.screen.blit(self.overlay, (0, 0))
        
        # 2. Text Label
        text = self.font.render("Running Benchmarks...", True, (255, 255, 255))
        text_rect = text.get_rect(center=(TOTAL_WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        self.screen.blit(text, text_rect)
        
        # 3. Spinning Animation
        center_x = TOTAL_WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        radius = 40
        
        # Draw 8 dots in a circle with varying transparency
        for i in range(8):
            # This logic creates a "tail" effect
            dot_angle = math.radians(angle + i * (360 / 8))
            x = center_x + math.cos(dot_angle) * radius
            y = center_y + math.sin(dot_angle) * radius
            
            # Opacity based on index relative to leading edge
            alpha = int(255 * (i / 8.0))
            color = (255, 255, 255)
            
            # Draw circles with fade effect
            s = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, alpha), (6, 6), 6)
            self.screen.blit(s, (x - 6, y - 6))
        
        pygame.display.flip()
