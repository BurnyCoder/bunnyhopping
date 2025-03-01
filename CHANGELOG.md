# Changelog

## v1.0.1 - Bug Fixes

### Fixed
- Fixed the `Game` class to not inherit from `Ursina` but instead initialize it as an instance
- Fixed distance calculation in `create_collectibles` method using vector subtraction and length
- Fixed `app.run()` call to use `self.app.run()` instead
- Added missing imports for random and math modules in game_objects.py

### Improved
- Updated the README with more detailed information about gameplay
- Added documentation about running the game via the launcher script 