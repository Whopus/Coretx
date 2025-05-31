# Coretx Examples

This directory contains example codebases for testing and demonstrating Coretx capabilities.

## Snake Game Example

The `snake_game/` directory contains a complete Python Snake Game implementation that serves as an excellent test case for Coretx analysis.

### Features
- **Complete Game Implementation**: 4 Python files with 2,706 lines of code
- **Object-Oriented Design**: 18 classes, 11 functions, 63 methods
- **AI Player System**: Multiple AI strategies (Random, Greedy, Pathfinding, Hamiltonian)
- **Modular Architecture**: Clean separation of concerns

### Files
- `game.py` - Core game logic and entities (SnakeGame, Snake, Food, etc.)
- `ai_player.py` - AI player implementations with multiple strategies
- `utils.py` - Utility classes (GameStats, PathFinder, ColorUtils, etc.)
- `main.py` - Command-line interface and game modes

### Running the Game
```bash
cd examples/snake_game
python main.py --mode human    # Play manually
python main.py --mode ai       # Watch AI play
python main.py --mode benchmark # Run AI benchmark
```

### Analyzing with Coretx
```bash
# From the Coretx root directory
python demo.py                 # Full analysis demo
python -m coretx analyze examples/snake_game  # CLI analysis
```

### Analysis Results
When analyzed with Coretx, the Snake Game demonstrates:
- **Fast Analysis**: ~0.038 seconds
- **Comprehensive Extraction**: 123 entities, 120 relationships
- **Pattern Detection**: Strategy pattern, Manager pattern, inheritance
- **Quality Assessment**: Low complexity, good organization
- **Architecture Mapping**: Clear modular structure

This example showcases Coretx's ability to understand complex codebases with multiple design patterns, AI implementations, and clean architectural separation.