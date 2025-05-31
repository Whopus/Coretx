"""
AI Player for Snake Game
Implements different AI strategies for playing the snake game automatically.
"""

import random
from typing import List, Optional, Tuple
from enum import Enum
from game import Snake, Food, Direction, Position
from utils import PathFinder


class AIStrategy(Enum):
    """Different AI strategies for playing the game."""
    RANDOM = "random"
    GREEDY = "greedy"
    PATHFINDING = "pathfinding"
    HAMILTONIAN = "hamiltonian"


class AIPlayer:
    """Base class for AI players."""
    
    def __init__(self, strategy: AIStrategy = AIStrategy.GREEDY):
        self.strategy = strategy
        self.moves_made = 0
        self.successful_moves = 0
    
    def get_next_move(self, snake: Snake, food: Food, grid_width: int, grid_height: int) -> Direction:
        """Get the next move for the AI player."""
        self.moves_made += 1
        
        if self.strategy == AIStrategy.RANDOM:
            return self._random_move(snake)
        elif self.strategy == AIStrategy.GREEDY:
            return self._greedy_move(snake, food, grid_width, grid_height)
        elif self.strategy == AIStrategy.PATHFINDING:
            return self._pathfinding_move(snake, food, grid_width, grid_height)
        elif self.strategy == AIStrategy.HAMILTONIAN:
            return self._hamiltonian_move(snake, food, grid_width, grid_height)
        else:
            return self._greedy_move(snake, food, grid_width, grid_height)
    
    def _random_move(self, snake: Snake) -> Direction:
        """Make a random valid move."""
        possible_directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        
        # Remove opposite direction to prevent immediate collision
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        
        opposite = opposite_directions.get(snake.direction)
        if opposite in possible_directions:
            possible_directions.remove(opposite)
        
        return random.choice(possible_directions)
    
    def _greedy_move(self, snake: Snake, food: Food, grid_width: int, grid_height: int) -> Direction:
        """Move greedily towards food while avoiding collisions."""
        head = snake.get_head_position()
        food_pos = food.position
        
        # Calculate direction towards food
        dx = food_pos.x - head.x
        dy = food_pos.y - head.y
        
        # Prioritize directions based on distance to food
        preferred_directions = []
        
        if abs(dx) > abs(dy):
            # Horizontal movement is more important
            if dx > 0:
                preferred_directions.append(Direction.RIGHT)
            elif dx < 0:
                preferred_directions.append(Direction.LEFT)
            
            if dy > 0:
                preferred_directions.append(Direction.DOWN)
            elif dy < 0:
                preferred_directions.append(Direction.UP)
        else:
            # Vertical movement is more important
            if dy > 0:
                preferred_directions.append(Direction.DOWN)
            elif dy < 0:
                preferred_directions.append(Direction.UP)
            
            if dx > 0:
                preferred_directions.append(Direction.RIGHT)
            elif dx < 0:
                preferred_directions.append(Direction.LEFT)
        
        # Add remaining directions
        all_directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        for direction in all_directions:
            if direction not in preferred_directions:
                preferred_directions.append(direction)
        
        # Choose first safe direction
        for direction in preferred_directions:
            if self._is_safe_move(snake, direction, grid_width, grid_height):
                return direction
        
        # If no safe move found, return current direction (will likely cause game over)
        return snake.direction
    
    def _pathfinding_move(self, snake: Snake, food: Food, grid_width: int, grid_height: int) -> Direction:
        """Use pathfinding to navigate to food."""
        head = snake.get_head_position()
        snake_body = snake.get_body_positions()
        
        # Find path to food
        path = PathFinder.find_path_to_food(head, food.position, snake_body, grid_width, grid_height)
        
        if path:
            next_pos = path[0]
            return self._get_direction_to_position(head, next_pos)
        else:
            # Fallback to greedy if no path found
            return self._greedy_move(snake, food, grid_width, grid_height)
    
    def _hamiltonian_move(self, snake: Snake, food: Food, grid_width: int, grid_height: int) -> Direction:
        """Use Hamiltonian cycle strategy (simplified version)."""
        # This is a simplified version - a full Hamiltonian cycle would be more complex
        head = snake.get_head_position()
        
        # Try to follow a pattern that covers the entire grid
        if head.x % 2 == 0:
            # Even columns: go down when possible, right when at bottom
            if head.y < grid_height - 1:
                if self._is_safe_move(snake, Direction.DOWN, grid_width, grid_height):
                    return Direction.DOWN
            if head.x < grid_width - 1:
                if self._is_safe_move(snake, Direction.RIGHT, grid_width, grid_height):
                    return Direction.RIGHT
        else:
            # Odd columns: go up when possible, right when at top
            if head.y > 0:
                if self._is_safe_move(snake, Direction.UP, grid_width, grid_height):
                    return Direction.UP
            if head.x < grid_width - 1:
                if self._is_safe_move(snake, Direction.RIGHT, grid_width, grid_height):
                    return Direction.RIGHT
        
        # Fallback to greedy
        return self._greedy_move(snake, food, grid_width, grid_height)
    
    def _is_safe_move(self, snake: Snake, direction: Direction, grid_width: int, grid_height: int) -> bool:
        """Check if a move in the given direction is safe."""
        head = snake.get_head_position()
        direction_offset = Position(*direction.value)
        new_head = head + direction_offset
        
        # Check wall collision
        if (new_head.x < 0 or new_head.x >= grid_width or 
            new_head.y < 0 or new_head.y >= grid_height):
            return False
        
        # Check self collision (excluding tail which will move)
        snake_body = snake.get_body_positions()[:-1]  # Exclude tail
        if new_head in snake_body:
            return False
        
        return True
    
    def _get_direction_to_position(self, from_pos: Position, to_pos: Position) -> Direction:
        """Get direction from one position to another."""
        dx = to_pos.x - from_pos.x
        dy = to_pos.y - from_pos.y
        
        if dx > 0:
            return Direction.RIGHT
        elif dx < 0:
            return Direction.LEFT
        elif dy > 0:
            return Direction.DOWN
        elif dy < 0:
            return Direction.UP
        else:
            return Direction.RIGHT  # Default
    
    def get_performance_stats(self) -> dict:
        """Get AI performance statistics."""
        success_rate = self.successful_moves / max(1, self.moves_made)
        return {
            "moves_made": self.moves_made,
            "successful_moves": self.successful_moves,
            "success_rate": success_rate,
            "strategy": self.strategy.value
        }
    
    def reset_stats(self) -> None:
        """Reset performance statistics."""
        self.moves_made = 0
        self.successful_moves = 0


class AdvancedAI(AIPlayer):
    """Advanced AI with learning capabilities and multiple strategies."""
    
    def __init__(self):
        super().__init__(AIStrategy.PATHFINDING)
        self.strategy_performance = {
            AIStrategy.GREEDY: {"score": 0, "games": 0},
            AIStrategy.PATHFINDING: {"score": 0, "games": 0},
            AIStrategy.HAMILTONIAN: {"score": 0, "games": 0}
        }
        self.current_strategy = AIStrategy.PATHFINDING
        self.adaptation_threshold = 5  # Games before considering strategy change
    
    def get_next_move(self, snake: Snake, food: Food, grid_width: int, grid_height: int) -> Direction:
        """Get next move using adaptive strategy selection."""
        # Use current strategy
        old_strategy = self.strategy
        self.strategy = self.current_strategy
        move = super().get_next_move(snake, food, grid_width, grid_height)
        self.strategy = old_strategy
        
        return move
    
    def record_game_result(self, strategy: AIStrategy, score: int) -> None:
        """Record the result of a game for strategy evaluation."""
        if strategy in self.strategy_performance:
            self.strategy_performance[strategy]["score"] += score
            self.strategy_performance[strategy]["games"] += 1
            
            # Adapt strategy if enough games played
            if self.strategy_performance[strategy]["games"] >= self.adaptation_threshold:
                self._adapt_strategy()
    
    def _adapt_strategy(self) -> None:
        """Adapt strategy based on performance."""
        best_strategy = self.current_strategy
        best_avg_score = 0
        
        for strategy, stats in self.strategy_performance.items():
            if stats["games"] > 0:
                avg_score = stats["score"] / stats["games"]
                if avg_score > best_avg_score:
                    best_avg_score = avg_score
                    best_strategy = strategy
        
        self.current_strategy = best_strategy
    
    def get_strategy_stats(self) -> dict:
        """Get statistics for all strategies."""
        stats = {}
        for strategy, data in self.strategy_performance.items():
            avg_score = data["score"] / max(1, data["games"])
            stats[strategy.value] = {
                "games_played": data["games"],
                "total_score": data["score"],
                "average_score": avg_score
            }
        return stats


def create_ai_player(difficulty: str = "medium") -> AIPlayer:
    """Factory function to create AI players of different difficulties."""
    difficulty_map = {
        "easy": AIStrategy.RANDOM,
        "medium": AIStrategy.GREEDY,
        "hard": AIStrategy.PATHFINDING,
        "expert": AIStrategy.HAMILTONIAN
    }
    
    strategy = difficulty_map.get(difficulty.lower(), AIStrategy.GREEDY)
    
    if difficulty.lower() == "adaptive":
        return AdvancedAI()
    else:
        return AIPlayer(strategy)