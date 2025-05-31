"""
Utility functions and helpers for the Snake Game.
"""

import json
import os
from typing import Dict, Any, List, Tuple
from dataclasses import asdict
from game import GameConfig, Position


class GameStats:
    """Tracks and manages game statistics."""
    
    def __init__(self):
        self.games_played = 0
        self.total_score = 0
        self.highest_score = 0
        self.total_food_eaten = 0
        self.average_game_length = 0.0
        self.game_lengths = []
    
    def record_game(self, score: int, food_eaten: int, game_length: float) -> None:
        """Record statistics from a completed game."""
        self.games_played += 1
        self.total_score += score
        self.total_food_eaten += food_eaten
        self.game_lengths.append(game_length)
        
        if score > self.highest_score:
            self.highest_score = score
        
        self.average_game_length = sum(self.game_lengths) / len(self.game_lengths)
    
    def get_stats_dict(self) -> Dict[str, Any]:
        """Get statistics as a dictionary."""
        return {
            "games_played": self.games_played,
            "total_score": self.total_score,
            "highest_score": self.highest_score,
            "total_food_eaten": self.total_food_eaten,
            "average_score": self.total_score / max(1, self.games_played),
            "average_game_length": self.average_game_length
        }
    
    def save_to_file(self, filename: str) -> None:
        """Save statistics to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.get_stats_dict(), f, indent=2)
    
    def load_from_file(self, filename: str) -> None:
        """Load statistics from a JSON file."""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                self.games_played = data.get("games_played", 0)
                self.total_score = data.get("total_score", 0)
                self.highest_score = data.get("highest_score", 0)
                self.total_food_eaten = data.get("total_food_eaten", 0)


class ConfigManager:
    """Manages game configuration loading and saving."""
    
    @staticmethod
    def save_config(config: GameConfig, filename: str) -> None:
        """Save game configuration to a JSON file."""
        config_dict = asdict(config)
        with open(filename, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @staticmethod
    def load_config(filename: str) -> GameConfig:
        """Load game configuration from a JSON file."""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                config_dict = json.load(f)
                return GameConfig(**config_dict)
        return GameConfig()


class PathFinder:
    """Utility class for pathfinding algorithms (for AI snake)."""
    
    @staticmethod
    def manhattan_distance(pos1: Position, pos2: Position) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)
    
    @staticmethod
    def get_neighbors(pos: Position, grid_width: int, grid_height: int) -> List[Position]:
        """Get valid neighboring positions."""
        neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in directions:
            new_pos = Position(pos.x + dx, pos.y + dy)
            if 0 <= new_pos.x < grid_width and 0 <= new_pos.y < grid_height:
                neighbors.append(new_pos)
        
        return neighbors
    
    @staticmethod
    def find_path_to_food(snake_head: Position, food_pos: Position, 
                         snake_body: List[Position], grid_width: int, 
                         grid_height: int) -> List[Position]:
        """Find a simple path from snake head to food using BFS."""
        from collections import deque
        
        queue = deque([(snake_head, [snake_head])])
        visited = {snake_head}
        
        while queue:
            current_pos, path = queue.popleft()
            
            if current_pos == food_pos:
                return path[1:]  # Return path without starting position
            
            for neighbor in PathFinder.get_neighbors(current_pos, grid_width, grid_height):
                if neighbor not in visited and neighbor not in snake_body:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # No path found


class ColorUtils:
    """Utility functions for color manipulation."""
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string."""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex string to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def interpolate_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                         factor: float) -> Tuple[int, int, int]:
        """Interpolate between two colors."""
        factor = max(0, min(1, factor))
        return tuple(
            int(color1[i] + (color2[i] - color1[i]) * factor)
            for i in range(3)
        )


class GameValidator:
    """Validates game state and configuration."""
    
    @staticmethod
    def validate_config(config: GameConfig) -> List[str]:
        """Validate game configuration and return list of errors."""
        errors = []
        
        if config.window_width <= 0:
            errors.append("Window width must be positive")
        
        if config.window_height <= 0:
            errors.append("Window height must be positive")
        
        if config.grid_size <= 0:
            errors.append("Grid size must be positive")
        
        if config.fps <= 0:
            errors.append("FPS must be positive")
        
        if config.window_width % config.grid_size != 0:
            errors.append("Window width must be divisible by grid size")
        
        if config.window_height % config.grid_size != 0:
            errors.append("Window height must be divisible by grid size")
        
        return errors
    
    @staticmethod
    def validate_position(pos: Position, grid_width: int, grid_height: int) -> bool:
        """Validate if position is within grid bounds."""
        return 0 <= pos.x < grid_width and 0 <= pos.y < grid_height


def calculate_difficulty_multiplier(score: int) -> float:
    """Calculate difficulty multiplier based on current score."""
    base_multiplier = 1.0
    score_threshold = 100
    increment = 0.1
    
    return base_multiplier + (score // score_threshold) * increment


def format_time(seconds: float) -> str:
    """Format time in seconds to MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def generate_random_color() -> Tuple[int, int, int]:
    """Generate a random RGB color."""
    import random
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between min and max."""
    return max(min_value, min(max_value, value))