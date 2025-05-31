"""
Main entry point for the Snake Game.
Provides command-line interface and game mode selection.
"""

import argparse
import sys
import time
from typing import Optional
from game import SnakeGame, GameConfig
from ai_player import create_ai_player, AIStrategy
from utils import GameStats, ConfigManager


def run_human_game(config: Optional[GameConfig] = None) -> None:
    """Run the game in human player mode."""
    print("Starting Snake Game - Human Player Mode")
    print("Controls: Arrow keys or WASD to move, SPACE to pause, ESC to quit")
    
    game = SnakeGame(config)
    game.run()


def run_ai_game(difficulty: str = "medium", config: Optional[GameConfig] = None, 
                games_to_play: int = 1, show_stats: bool = True) -> None:
    """Run the game in AI player mode."""
    print(f"Starting Snake Game - AI Player Mode (Difficulty: {difficulty})")
    
    ai_player = create_ai_player(difficulty)
    stats = GameStats()
    
    for game_num in range(games_to_play):
        print(f"\nGame {game_num + 1}/{games_to_play}")
        
        # Create game instance
        game = SnakeGame(config)
        game_start_time = time.time()
        
        # Override input handling for AI
        while game.running and game.game_state.value != "game_over":
            # Get AI move
            if game.game_state.value == "playing":
                ai_direction = ai_player.get_next_move(
                    game.snake, game.food, game.grid_width, game.grid_height
                )
                game.snake.change_direction(ai_direction)
            
            # Update game
            game.update_game_logic()
            
            # Optional: render game (comment out for faster execution)
            if games_to_play == 1:  # Only render if playing single game
                game.render_game()
            
            # Small delay to make it watchable
            if games_to_play == 1:
                time.sleep(0.1)
        
        # Record game statistics
        game_time = time.time() - game_start_time
        final_score = game.score_manager.score
        food_eaten = game.score_manager.food_eaten
        
        stats.record_game(final_score, food_eaten, game_time)
        
        print(f"Game {game_num + 1} completed - Score: {final_score}, Food: {food_eaten}, Time: {game_time:.1f}s")
        
        # Clean up pygame for this game
        import pygame
        pygame.quit()
    
    # Show final statistics
    if show_stats:
        print("\n" + "="*50)
        print("AI PERFORMANCE STATISTICS")
        print("="*50)
        
        game_stats = stats.get_stats_dict()
        print(f"Games Played: {game_stats['games_played']}")
        print(f"Total Score: {game_stats['total_score']}")
        print(f"Highest Score: {game_stats['highest_score']}")
        print(f"Average Score: {game_stats['average_score']:.1f}")
        print(f"Total Food Eaten: {game_stats['total_food_eaten']}")
        print(f"Average Game Length: {game_stats['average_game_length']:.1f}s")
        
        ai_stats = ai_player.get_performance_stats()
        print(f"AI Success Rate: {ai_stats['success_rate']:.2%}")
        print(f"Strategy Used: {ai_stats['strategy']}")


def run_benchmark(config: Optional[GameConfig] = None) -> None:
    """Run benchmark comparing different AI strategies."""
    print("Running AI Strategy Benchmark...")
    
    strategies = ["easy", "medium", "hard", "expert"]
    games_per_strategy = 10
    
    results = {}
    
    for strategy in strategies:
        print(f"\nTesting {strategy} strategy...")
        ai_player = create_ai_player(strategy)
        stats = GameStats()
        
        for game_num in range(games_per_strategy):
            # Create and run game
            game = SnakeGame(config)
            game_start_time = time.time()
            
            while game.running and game.game_state.value != "game_over":
                if game.game_state.value == "playing":
                    ai_direction = ai_player.get_next_move(
                        game.snake, game.food, game.grid_width, game.grid_height
                    )
                    game.snake.change_direction(ai_direction)
                
                game.update_game_logic()
            
            # Record stats
            game_time = time.time() - game_start_time
            stats.record_game(game.score_manager.score, game.score_manager.food_eaten, game_time)
            
            import pygame
            pygame.quit()
        
        # Store results
        game_stats = stats.get_stats_dict()
        results[strategy] = {
            "average_score": game_stats['average_score'],
            "highest_score": game_stats['highest_score'],
            "average_time": game_stats['average_game_length']
        }
    
    # Display benchmark results
    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    print(f"{'Strategy':<12} {'Avg Score':<12} {'High Score':<12} {'Avg Time':<12}")
    print("-" * 60)
    
    for strategy, stats in results.items():
        print(f"{strategy:<12} {stats['average_score']:<12.1f} {stats['highest_score']:<12} {stats['average_time']:<12.1f}")


def create_config_from_args(args) -> GameConfig:
    """Create game configuration from command line arguments."""
    config = GameConfig()
    
    if args.width:
        config.window_width = args.width
    if args.height:
        config.window_height = args.height
    if args.grid_size:
        config.grid_size = args.grid_size
    if args.fps:
        config.fps = args.fps
    
    return config


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Snake Game with AI")
    
    # Game mode selection
    parser.add_argument("--mode", choices=["human", "ai", "benchmark"], 
                       default="human", help="Game mode to run")
    
    # AI configuration
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard", "expert", "adaptive"],
                       default="medium", help="AI difficulty level")
    parser.add_argument("--games", type=int, default=1, 
                       help="Number of games to play in AI mode")
    
    # Game configuration
    parser.add_argument("--width", type=int, help="Window width")
    parser.add_argument("--height", type=int, help="Window height")
    parser.add_argument("--grid-size", type=int, help="Grid cell size")
    parser.add_argument("--fps", type=int, help="Frames per second")
    
    # Configuration file
    parser.add_argument("--config", help="Load configuration from file")
    parser.add_argument("--save-config", help="Save current configuration to file")
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        config = ConfigManager.load_config(args.config)
    else:
        config = create_config_from_args(args)
    
    # Save configuration if requested
    if args.save_config:
        ConfigManager.save_config(config, args.save_config)
        print(f"Configuration saved to {args.save_config}")
        return
    
    # Run appropriate game mode
    try:
        if args.mode == "human":
            run_human_game(config)
        elif args.mode == "ai":
            run_ai_game(args.difficulty, config, args.games)
        elif args.mode == "benchmark":
            run_benchmark(config)
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Error running game: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()