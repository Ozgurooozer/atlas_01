"""
Tests for Demo Game: Puzzle.

This test suite validates the puzzle game implementation including:
- Grid board creation
- Gem selection and swapping
- Match detection (3+ in a row)
- Gravity and falling gems
- Undo/Redo system
- Save/Load game state
- Score tracking

Uses HeadlessGPU and HeadlessWindow for testing.
"""

from hal.headless import MemoryFilesystem


class TestPuzzleGridCreation:
    """Test suite for puzzle grid creation."""

    def test_puzzle_game_exists(self):
        """Puzzle game class should exist."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        assert game is not None

    def test_puzzle_game_has_grid(self):
        """Puzzle game should have a grid after initialization."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()
        assert game.grid is not None

    def test_grid_has_correct_dimensions(self):
        """Grid should be 8x8 by default."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()
        assert game.grid.width == 8
        assert game.grid.height == 8

    def test_grid_is_populated_with_gems(self):
        """Grid should be populated with gems."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()
        # All cells should have gems
        for y in range(game.grid.height):
            for x in range(game.grid.width):
                gem = game.grid.get_gem(x, y)
                assert gem is not None

    def test_gems_have_colors(self):
        """Gems should have colors."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()
        gem = game.grid.get_gem(0, 0)
        assert gem.color is not None
        assert gem.color in gem.VALID_COLORS


class TestPuzzleSelection:
    """Test suite for gem selection."""

    def test_can_select_gem(self):
        """Should be able to select a gem by clicking."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        # Click on cell (0, 0)
        game.click_cell(0, 0)

        assert game.selected_position == (0, 0)

    def test_can_deselect_gem(self):
        """Should be able to deselect by clicking same cell."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        game.click_cell(0, 0)
        game.click_cell(0, 0)  # Click same cell again

        assert game.selected_position is None

    def test_can_select_different_gem(self):
        """Should be able to select a different gem."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        game.click_cell(0, 0)
        game.click_cell(1, 1)  # Non-adjacent, just selects new

        assert game.selected_position == (1, 1)


class TestPuzzleSwapping:
    """Test suite for gem swapping."""

    def test_can_swap_adjacent_gems(self):
        """Should be able to swap adjacent gems."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        # Select first gem
        game.click_cell(0, 0)
        first_gem = game.grid.get_gem(0, 0)
        first_color = first_gem.color

        # Get adjacent gem's color
        adjacent_gem = game.grid.get_gem(1, 0)
        adjacent_color = adjacent_gem.color

        # Swap with adjacent
        game.click_cell(1, 0)

        # Check if swapped
        assert game.grid.get_gem(0, 0).color == adjacent_color
        assert game.grid.get_gem(1, 0).color == first_color

    def test_cannot_swap_non_adjacent_gems(self):
        """Should not swap non-adjacent gems."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        game.click_cell(0, 0)
        game.click_cell(2, 0)  # Non-adjacent

        # Should just select new position instead
        assert game.selected_position == (2, 0)

    def test_swap_counts_as_move(self):
        """Swapping should increment move counter."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        initial_moves = game.moves

        game.click_cell(0, 0)
        game.click_cell(1, 0)

        assert game.moves == initial_moves + 1


class TestPuzzleMatching:
    """Test suite for match detection."""

    def test_detect_horizontal_match_three(self):
        """Should detect 3 gems in a row horizontally."""
        from demo.puzzle import PuzzleGame, Gem

        game = PuzzleGame()
        game.initialize()

        # Set up a guaranteed horizontal match
        # Force colors for testing
        test_color = "red"
        for x in range(3):
            game.grid.set_gem(x, 0, Gem(test_color))

        matches = game.grid.find_matches()
        assert len(matches) >= 1
        # Should find 3 gems in the match
        total_matched = sum(len(m) for m in matches)
        assert total_matched >= 3

    def test_detect_vertical_match_three(self):
        """Should detect 3 gems in a column vertically."""
        from demo.puzzle import PuzzleGame, Gem

        game = PuzzleGame()
        game.initialize()

        # Set up a guaranteed vertical match
        test_color = "blue"
        for y in range(3):
            game.grid.set_gem(0, y, Gem(test_color))

        matches = game.grid.find_matches()
        assert len(matches) >= 1
        total_matched = sum(len(m) for m in matches)
        assert total_matched >= 3

    def test_remove_matched_gems(self):
        """Matched gems should be removed and replaced by gravity."""
        from demo.puzzle import PuzzleGame, Gem

        game = PuzzleGame()
        game.initialize()

        # Set up a match at the bottom
        test_color = "green"
        for x in range(3):
            game.grid.set_gem(x, 0, Gem(test_color))

        # Store original matched color
        original_color = test_color

        game.process_matches()

        # After processing, the bottom row should have new gems (not all green)
        # Since gravity fills from above, some may still be green but not all 3
        bottom_colors = [game.grid.get_gem(x, 0).color for x in range(3)]
        # At least one should be different (not all green anymore)
        assert not all(c == original_color for c in bottom_colors)

    def test_no_initial_matches(self):
        """Initial grid should have no matches."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        matches = game.grid.find_matches()
        assert len(matches) == 0


class TestPuzzleGravity:
    """Test suite for gravity and falling gems."""

    def test_gems_fall_after_match(self):
        """Gems should fall to fill empty spaces."""
        from demo.puzzle import PuzzleGame, Gem

        game = PuzzleGame()
        game.initialize()

        # Create a scenario where gems need to fall
        # Set up a match at bottom, gems above should fall
        game.grid.set_gem(0, 0, Gem("red"))
        game.grid.set_gem(0, 1, Gem("red"))
        game.grid.set_gem(0, 2, Gem("red"))
        game.grid.set_gem(0, 3, Gem("blue"))  # Above the reds

        game.process_matches()
        game.apply_gravity()

        # The blue gem should have fallen
        assert game.grid.get_gem(0, 0) is not None
        assert game.grid.get_gem(0, 0).color == "blue"

    def test_new_gems_spawn_at_top(self):
        """New gems should spawn at top after gravity."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        # Clear top row
        for x in range(game.grid.width):
            game.grid.set_gem(x, game.grid.height - 1, None)

        game.apply_gravity()

        # Top row should be filled again
        for x in range(game.grid.width):
            assert game.grid.get_gem(x, game.grid.height - 1) is not None


class TestPuzzleScore:
    """Test suite for score tracking."""

    def test_score_starts_at_zero(self):
        """Score should start at 0."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        assert game.score == 0

    def test_score_increases_on_match(self):
        """Score should increase when matches are made."""
        from demo.puzzle import PuzzleGame, Gem

        game = PuzzleGame()
        game.initialize()

        # Set up a match
        for x in range(3):
            game.grid.set_gem(x, 0, Gem("red"))

        game.process_matches()

        assert game.score > 0

    def test_larger_match_gives_more_points(self):
        """Larger matches should give more points."""
        from demo.puzzle import PuzzleGame, Gem

        game = PuzzleGame()
        game.initialize()

        # 3-gem match
        for x in range(3):
            game.grid.set_gem(x, 0, Gem("red"))

        game.process_matches()
        score_3 = game.score

        # Reset and do 4-gem match
        game.score = 0
        for x in range(4):
            game.grid.set_gem(x, 1, Gem("blue"))

        game.process_matches()
        score_4 = game.score

        assert score_4 > score_3


class TestPuzzleUndoRedo:
    """Test suite for undo/redo functionality."""

    def test_can_undo_move(self):
        """Should be able to undo a move."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        # Make a move
        initial_gem_0 = game.grid.get_gem(0, 0).color
        initial_gem_1 = game.grid.get_gem(1, 0).color

        game.click_cell(0, 0)
        game.click_cell(1, 0)

        # Undo
        game.undo()

        # Gems should be back to original positions
        assert game.grid.get_gem(0, 0).color == initial_gem_0
        assert game.grid.get_gem(1, 0).color == initial_gem_1

    def test_can_redo_move(self):
        """Should be able to redo an undone move."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        # Make a move
        game.click_cell(0, 0)
        game.click_cell(1, 0)
        after_move_gem = game.grid.get_gem(0, 0).color

        # Undo
        game.undo()

        # Redo
        game.redo()

        assert game.grid.get_gem(0, 0).color == after_move_gem

    def test_undo_decrements_move_count(self):
        """Undo should decrement move count."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        initial_moves = game.moves

        game.click_cell(0, 0)
        game.click_cell(1, 0)

        game.undo()

        assert game.moves == initial_moves

    def test_multiple_undo_redo(self):
        """Should support multiple undo/redo operations."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        # Make multiple moves
        game.click_cell(0, 0)
        game.click_cell(1, 0)

        game.click_cell(2, 0)
        game.click_cell(3, 0)

        moves_after_2 = game.moves

        # Undo twice
        game.undo()
        game.undo()

        assert game.moves == moves_after_2 - 2

        # Redo twice
        game.redo()
        game.redo()

        assert game.moves == moves_after_2


class TestPuzzleSaveLoad:
    """Test suite for save/load functionality."""

    def test_can_save_game_state(self):
        """Should be able to save game state."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        # Make some moves
        game.click_cell(0, 0)
        game.click_cell(1, 0)

        # Save
        state = game.save_state()

        assert state is not None
        assert "grid" in state
        assert "score" in state
        assert "moves" in state

    def test_can_load_game_state(self):
        """Should be able to load game state."""
        from demo.puzzle import PuzzleGame

        game1 = PuzzleGame()
        game1.initialize()

        # Make some moves
        game1.click_cell(0, 0)
        game1.click_cell(1, 0)
        saved_score = game1.score
        saved_moves = game1.moves

        # Save state
        state = game1.save_state()

        # Create new game and load state
        game2 = PuzzleGame()
        game2.initialize()
        game2.load_state(state)

        assert game2.score == saved_score
        assert game2.moves == saved_moves

    def test_save_load_preserves_grid(self):
        """Save/load should preserve grid state."""
        from demo.puzzle import PuzzleGame

        game1 = PuzzleGame()
        game1.initialize()

        # Save grid colors
        original_colors = []
        for y in range(game1.grid.height):
            row = []
            for x in range(game1.grid.width):
                row.append(game1.grid.get_gem(x, y).color)
            original_colors.append(row)

        state = game1.save_state()

        game2 = PuzzleGame()
        game2.initialize()
        game2.load_state(state)

        # Verify grid is the same
        for y in range(game2.grid.height):
            for x in range(game2.grid.width):
                assert game2.grid.get_gem(x, y).color == original_colors[y][x]

    def test_save_to_filesystem(self):
        """Should be able to save to and load from filesystem."""
        from demo.puzzle import PuzzleGame
        from core.serializer import write_json, read_json

        game = PuzzleGame()
        game.initialize()

        game.click_cell(0, 0)
        game.click_cell(1, 0)

        filesystem = MemoryFilesystem()

        # Save
        state = game.save_state()
        write_json(filesystem, "savegame.json", state)

        # Verify file was created
        assert filesystem.file_exists("savegame.json")

        # Load
        loaded_state = read_json(filesystem, "savegame.json")

        game2 = PuzzleGame()
        game2.initialize()
        game2.load_state(loaded_state)

        assert game2.score == game.score
        assert game2.moves == game.moves


class TestPuzzleGameFlow:
    """Test suite for overall game flow."""

    def test_game_has_engine(self):
        """Game should have engine reference after initialize."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()
        assert game.engine is not None

    def test_game_has_world(self):
        """Game should have world after initialize."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()
        assert game.world is not None

    def test_game_can_tick(self):
        """Game should be able to tick."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        # Should not raise
        game.tick(0.016)

    def test_game_can_run(self):
        """Game should be able to run for a duration."""
        from demo.puzzle import PuzzleGame

        game = PuzzleGame()
        game.initialize()

        # Run for short duration
        game.run(duration=0.1, dt=0.016)

        # Game should still be valid
        assert game.grid is not None

    def test_chain_reaction_scoring(self):
        """Chain reactions should award additional points."""
        from demo.puzzle import PuzzleGame, Gem

        game = PuzzleGame()
        game.initialize()

        # Set up a potential chain reaction
        # This is a simplified test - actual chains depend on falling gems
        for x in range(3):
            game.grid.set_gem(x, 0, Gem("red"))
        for x in range(3, 6):
            game.grid.set_gem(x, 0, Gem("red"))

        game.process_matches()

        # Should have matched 6 gems total
        assert game.score >= 60  # At least 10 points per gem
