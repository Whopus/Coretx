# Snake Game

A modern implementation of the classic Snake game with AI players and advanced features.

## Features

- **Classic Gameplay**: Traditional snake game mechanics with smooth controls
- **AI Players**: Multiple AI strategies with different difficulty levels
- **Configurable**: Customizable game settings and window size
- **Statistics**: Game performance tracking and analysis
- **Benchmark Mode**: Compare different AI strategies
- **Modular Design**: Clean, object-oriented architecture

## Game Components

### Core Classes

- `SnakeGame`: Main game controller and game loop
- `Snake`: Player snake with movement and collision detection
- `Food`: Food items with random placement
- `GameRenderer`: Handles all rendering operations
- `InputHandler`: Processes user input and events
- `ScoreManager`: Tracks scoring and statistics

### AI System

- `AIPlayer`: Base AI player with multiple strategies
- `AdvancedAI`: Adaptive AI that learns from performance
- `PathFinder`: Pathfinding algorithms for navigation

### Utilities

- `GameStats`: Performance tracking and statistics
- `ConfigManager`: Configuration loading and saving
- `ColorUtils`: Color manipulation utilities
- `GameValidator`: Game state validation

## Installation

```bash
pip install pygame
```

## Usage

### Human Player Mode

```bash
python main.py --mode human
```

Controls:
- Arrow keys or WASD: Move snake
- SPACE: Pause/unpause game
- ESC: Quit game

### AI Player Mode

```bash
# Single AI game
python main.py --mode ai --difficulty medium

# Multiple AI games
python main.py --mode ai --difficulty hard --games 10

# Available difficulties: easy, medium, hard, expert, adaptive
```

### Benchmark Mode

```bash
python main.py --mode benchmark
```

### Custom Configuration

```bash
# Custom window size and settings
python main.py --width 1000 --height 800 --grid-size 25 --fps 15

# Save configuration
python main.py --save-config my_config.json --width 800 --height 600

# Load configuration
python main.py --config my_config.json
```

## AI Strategies

1. **Random**: Makes random valid moves
2. **Greedy**: Moves directly toward food while avoiding collisions
3. **Pathfinding**: Uses BFS to find optimal path to food
4. **Hamiltonian**: Follows a pattern that covers the entire grid
5. **Adaptive**: Learns and adapts strategy based on performance

## Architecture

The game follows a modular, object-oriented design:

```
snake_game/
├── game.py          # Core game classes and logic
├── ai_player.py     # AI player implementations
├── utils.py         # Utility functions and helpers
├── main.py          # Entry point and CLI
└── README.md        # This file
```

### Key Design Patterns

- **Strategy Pattern**: Different AI strategies
- **Observer Pattern**: Event handling system
- **Factory Pattern**: AI player creation
- **Command Pattern**: Input handling

## Game States

- `PLAYING`: Normal gameplay
- `PAUSED`: Game paused by player
- `GAME_OVER`: Game ended due to collision

## Configuration Options

- Window dimensions (width, height)
- Grid cell size
- Frame rate (FPS)
- Colors (snake, food, background)
- AI behavior parameters

## Performance

The game is optimized for smooth gameplay:

- Efficient collision detection
- Optimized rendering pipeline
- Memory-conscious data structures
- Configurable performance settings

## Examples

### Basic Game

```python
from game import SnakeGame, GameConfig

config = GameConfig(window_width=800, window_height=600)
game = SnakeGame(config)
game.run()
```

### AI Player

```python
from ai_player import create_ai_player
from game import SnakeGame

ai = create_ai_player("hard")
game = SnakeGame()

# In game loop:
direction = ai.get_next_move(snake, food, grid_width, grid_height)
snake.change_direction(direction)
```

### Statistics Tracking

```python
from utils import GameStats

stats = GameStats()
stats.record_game(score=150, food_eaten=15, game_length=45.2)
print(stats.get_stats_dict())
```

## Contributing

The codebase is designed for easy extension:

1. Add new AI strategies by extending `AIPlayer`
2. Implement new game modes in `main.py`
3. Add utility functions in `utils.py`
4. Extend configuration options in `GameConfig`

## License

This project is open source and available under the MIT License.