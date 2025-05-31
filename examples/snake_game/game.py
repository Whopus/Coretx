"""
Snake Game Implementation
A classic snake game using pygame with object-oriented design.
"""

import pygame
import random
import sys
from enum import Enum
from typing import List, Tuple, Optional
from dataclasses import dataclass


class Direction(Enum):
    """Enumeration for movement directions."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class GameState(Enum):
    """Enumeration for game states."""
    PLAYING = "playing"
    GAME_OVER = "game_over"
    PAUSED = "paused"


@dataclass
class Position:
    """Represents a position on the game grid."""
    x: int
    y: int
    
    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y)
    
    def __eq__(self, other: 'Position') -> bool:
        return self.x == other.x and self.y == other.y


@dataclass
class GameConfig:
    """Configuration settings for the game."""
    window_width: int = 800
    window_height: int = 600
    grid_size: int = 20
    fps: int = 10
    snake_color: Tuple[int, int, int] = (0, 255, 0)
    food_color: Tuple[int, int, int] = (255, 0, 0)
    background_color: Tuple[int, int, int] = (0, 0, 0)
    border_color: Tuple[int, int, int] = (255, 255, 255)


class Food:
    """Represents food items in the game."""
    
    def __init__(self, grid_width: int, grid_height: int):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.position = self._generate_position()
    
    def _generate_position(self) -> Position:
        """Generate a random position for the food."""
        x = random.randint(0, self.grid_width - 1)
        y = random.randint(0, self.grid_height - 1)
        return Position(x, y)
    
    def respawn(self, snake_positions: List[Position]) -> None:
        """Respawn food at a new location not occupied by snake."""
        while True:
            self.position = self._generate_position()
            if self.position not in snake_positions:
                break
    
    def draw(self, screen: pygame.Surface, config: GameConfig) -> None:
        """Draw the food on the screen."""
        rect = pygame.Rect(
            self.position.x * config.grid_size,
            self.position.y * config.grid_size,
            config.grid_size,
            config.grid_size
        )
        pygame.draw.rect(screen, config.food_color, rect)


class Snake:
    """Represents the snake player."""
    
    def __init__(self, start_position: Position, initial_length: int = 3):
        self.body = [Position(start_position.x - i, start_position.y) 
                    for i in range(initial_length)]
        self.direction = Direction.RIGHT
        self.grow_pending = 0
    
    def move(self) -> None:
        """Move the snake in the current direction."""
        # Calculate new head position
        direction_offset = Position(*self.direction.value)
        new_head = self.body[0] + direction_offset
        
        # Add new head
        self.body.insert(0, new_head)
        
        # Remove tail unless growing
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
    
    def change_direction(self, new_direction: Direction) -> None:
        """Change snake direction if valid."""
        # Prevent reversing into itself
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        
        if new_direction != opposite_directions.get(self.direction):
            self.direction = new_direction
    
    def grow(self, segments: int = 1) -> None:
        """Schedule the snake to grow."""
        self.grow_pending += segments
    
    def check_collision_with_self(self) -> bool:
        """Check if snake has collided with itself."""
        head = self.body[0]
        return head in self.body[1:]
    
    def check_collision_with_walls(self, grid_width: int, grid_height: int) -> bool:
        """Check if snake has collided with walls."""
        head = self.body[0]
        return (head.x < 0 or head.x >= grid_width or 
                head.y < 0 or head.y >= grid_height)
    
    def get_head_position(self) -> Position:
        """Get the position of the snake's head."""
        return self.body[0]
    
    def get_body_positions(self) -> List[Position]:
        """Get all body segment positions."""
        return self.body.copy()
    
    def draw(self, screen: pygame.Surface, config: GameConfig) -> None:
        """Draw the snake on the screen."""
        for segment in self.body:
            rect = pygame.Rect(
                segment.x * config.grid_size,
                segment.y * config.grid_size,
                config.grid_size,
                config.grid_size
            )
            pygame.draw.rect(screen, config.snake_color, rect)
            pygame.draw.rect(screen, config.border_color, rect, 1)


class ScoreManager:
    """Manages game scoring and statistics."""
    
    def __init__(self):
        self.score = 0
        self.high_score = 0
        self.food_eaten = 0
    
    def add_points(self, points: int) -> None:
        """Add points to the current score."""
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
    
    def food_consumed(self) -> None:
        """Record that food was consumed."""
        self.food_eaten += 1
        self.add_points(10)
    
    def reset_score(self) -> None:
        """Reset the current game score."""
        self.score = 0
        self.food_eaten = 0
    
    def get_score_text(self) -> str:
        """Get formatted score text."""
        return f"Score: {self.score} | High Score: {self.high_score}"


class GameRenderer:
    """Handles all game rendering operations."""
    
    def __init__(self, config: GameConfig):
        self.config = config
        pygame.init()
        self.screen = pygame.display.set_mode((config.window_width, config.window_height))
        pygame.display.set_caption("Snake Game")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
    
    def clear_screen(self) -> None:
        """Clear the screen with background color."""
        self.screen.fill(self.config.background_color)
    
    def draw_text(self, text: str, position: Tuple[int, int], color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """Draw text on the screen."""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, position)
    
    def draw_game_over(self, score_manager: ScoreManager) -> None:
        """Draw game over screen."""
        self.clear_screen()
        
        game_over_text = "GAME OVER"
        score_text = score_manager.get_score_text()
        restart_text = "Press SPACE to restart or ESC to quit"
        
        # Center the text
        game_over_rect = self.font.get_rect(game_over_text)
        score_rect = self.font.get_rect(score_text)
        restart_rect = self.font.get_rect(restart_text)
        
        center_x = self.config.window_width // 2
        center_y = self.config.window_height // 2
        
        self.draw_text(game_over_text, (center_x - game_over_rect.width // 2, center_y - 60), (255, 0, 0))
        self.draw_text(score_text, (center_x - score_rect.width // 2, center_y))
        self.draw_text(restart_text, (center_x - restart_rect.width // 2, center_y + 60))
    
    def update_display(self) -> None:
        """Update the display and maintain FPS."""
        pygame.display.flip()
        self.clock.tick(self.config.fps)


class InputHandler:
    """Handles user input and events."""
    
    def __init__(self):
        self.key_direction_map = {
            pygame.K_UP: Direction.UP,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT,
            pygame.K_w: Direction.UP,
            pygame.K_s: Direction.DOWN,
            pygame.K_a: Direction.LEFT,
            pygame.K_d: Direction.RIGHT
        }
    
    def handle_events(self, snake: Snake, game_state: GameState) -> Tuple[GameState, bool]:
        """Handle pygame events and return new game state and quit flag."""
        quit_game = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game = True
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game = True
                
                elif event.key == pygame.K_SPACE:
                    if game_state == GameState.GAME_OVER:
                        game_state = GameState.PLAYING
                    elif game_state == GameState.PLAYING:
                        game_state = GameState.PAUSED
                    elif game_state == GameState.PAUSED:
                        game_state = GameState.PLAYING
                
                elif event.key in self.key_direction_map and game_state == GameState.PLAYING:
                    new_direction = self.key_direction_map[event.key]
                    snake.change_direction(new_direction)
        
        return game_state, quit_game


class SnakeGame:
    """Main game class that orchestrates all components."""
    
    def __init__(self, config: Optional[GameConfig] = None):
        self.config = config or GameConfig()
        self.grid_width = self.config.window_width // self.config.grid_size
        self.grid_height = self.config.window_height // self.config.grid_size
        
        # Initialize game components
        self.renderer = GameRenderer(self.config)
        self.input_handler = InputHandler()
        self.score_manager = ScoreManager()
        
        # Initialize game objects
        self.reset_game()
        
        self.game_state = GameState.PLAYING
        self.running = True
    
    def reset_game(self) -> None:
        """Reset the game to initial state."""
        start_pos = Position(self.grid_width // 2, self.grid_height // 2)
        self.snake = Snake(start_pos)
        self.food = Food(self.grid_width, self.grid_height)
        self.food.respawn(self.snake.get_body_positions())
        self.score_manager.reset_score()
    
    def update_game_logic(self) -> None:
        """Update game logic for one frame."""
        if self.game_state != GameState.PLAYING:
            return
        
        # Move snake
        self.snake.move()
        
        # Check collisions
        if (self.snake.check_collision_with_walls(self.grid_width, self.grid_height) or
            self.snake.check_collision_with_self()):
            self.game_state = GameState.GAME_OVER
            return
        
        # Check food consumption
        if self.snake.get_head_position() == self.food.position:
            self.snake.grow()
            self.score_manager.food_consumed()
            self.food.respawn(self.snake.get_body_positions())
    
    def render_game(self) -> None:
        """Render the current game state."""
        if self.game_state == GameState.GAME_OVER:
            self.renderer.draw_game_over(self.score_manager)
        else:
            self.renderer.clear_screen()
            
            # Draw game objects
            self.food.draw(self.renderer.screen, self.config)
            self.snake.draw(self.renderer.screen, self.config)
            
            # Draw UI
            score_text = self.score_manager.get_score_text()
            self.renderer.draw_text(score_text, (10, 10))
            
            if self.game_state == GameState.PAUSED:
                pause_text = "PAUSED - Press SPACE to continue"
                text_rect = self.renderer.font.get_rect(pause_text)
                center_x = self.config.window_width // 2 - text_rect.width // 2
                self.renderer.draw_text(pause_text, (center_x, 50), (255, 255, 0))
        
        self.renderer.update_display()
    
    def handle_input(self) -> None:
        """Handle user input."""
        new_state, quit_flag = self.input_handler.handle_events(self.snake, self.game_state)
        
        if quit_flag:
            self.running = False
        
        if new_state == GameState.PLAYING and self.game_state == GameState.GAME_OVER:
            self.reset_game()
        
        self.game_state = new_state
    
    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update_game_logic()
            self.render_game()
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the snake game."""
    # Create custom configuration if needed
    config = GameConfig(
        window_width=800,
        window_height=600,
        grid_size=20,
        fps=12,
        snake_color=(0, 255, 0),
        food_color=(255, 0, 0)
    )
    
    # Create and run the game
    game = SnakeGame(config)
    game.run()


if __name__ == "__main__":
    main()