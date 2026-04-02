"""
Tests for World class.

World is the container for all Actors in the game.
It manages actor lifecycle and provides queries.

Layer: 3 (World)
"""

from core.object import Object
from core.guid import GUID
from world.actor import Actor
from world.component import Component
from world.world import World


class TestWorldInheritance:
    """Test that World properly inherits from Object."""

    def test_world_is_object(self):
        """World should be an instance of Object."""
        world = World()
        assert isinstance(world, Object)

    def test_world_has_guid(self):
        """World should have a GUID."""
        world = World()
        assert hasattr(world, "guid")
        assert isinstance(world.guid, GUID)

    def test_world_has_name(self):
        """World should have a name."""
        world = World(name="TestWorld")
        assert world.name == "TestWorld"


class TestWorldActors:
    """Test World actor management."""

    def test_world_has_actors_property(self):
        """World should have actors property."""
        world = World()
        assert hasattr(world, "actors")

    def test_world_actors_default_empty(self):
        """World should have empty actors by default."""
        world = World()
        assert world.actors == []

    def test_world_spawn_actor(self):
        """World can spawn an actor."""
        world = World()
        actor = Actor()
        world.spawn_actor(actor)
        assert actor in world.actors

    def test_spawn_actor_sets_world_reference(self):
        """Spawning actor sets the world reference."""
        world = World()
        actor = Actor()
        world.spawn_actor(actor)
        assert actor.world is world

    def test_spawn_actor_calls_on_created(self):
        """Spawning actor calls on_created."""
        results = []

        class TestActor(Actor):
            def on_created(self):
                results.append("created")

        world = World()
        actor = TestActor()
        world.spawn_actor(actor)

        assert "created" in results

    def test_world_destroy_actor(self):
        """World can destroy an actor."""
        world = World()
        actor = Actor()
        world.spawn_actor(actor)
        world.destroy_actor(actor)
        assert actor not in world.actors

    def test_destroy_actor_clears_world_reference(self):
        """Destroying actor clears world reference."""
        world = World()
        actor = Actor()
        world.spawn_actor(actor)
        world.destroy_actor(actor)
        assert actor.world is None

    def test_destroy_actor_calls_on_destroyed(self):
        """Destroying actor calls on_destroyed."""
        results = []

        class TestActor(Actor):
            def on_destroyed(self):
                results.append("destroyed")

        world = World()
        actor = TestActor()
        world.spawn_actor(actor)
        world.destroy_actor(actor)

        assert "destroyed" in results

    def test_destroy_actor_removes_components(self):
        """Destroying actor removes all its components."""
        world = World()
        actor = Actor()
        comp = Component()
        actor.add_component(comp)
        world.spawn_actor(actor)
        world.destroy_actor(actor)

        assert len(actor.components) == 0


class TestWorldTick:
    """Test World tick functionality."""

    def test_world_has_tick_method(self):
        """World should have tick method."""
        world = World()
        assert hasattr(world, "tick")
        assert callable(world.tick)

    def test_world_tick_propagates_to_actors(self):
        """World tick propagates to enabled actors."""
        tick_results = []

        class TestActor(Actor):
            def tick(self, delta_time: float):
                tick_results.append(delta_time)

        world = World()
        actor = TestActor()
        world.spawn_actor(actor)
        world.tick(0.016)

        assert 0.016 in tick_results

    def test_world_tick_skips_disabled_actors(self):
        """World tick should not tick disabled actors."""
        tick_results = []

        class TestActor(Actor):
            def tick(self, delta_time: float):
                tick_results.append(delta_time)

        world = World()
        actor = TestActor()
        actor.enabled = False
        world.spawn_actor(actor)
        world.tick(0.016)

        assert len(tick_results) == 0


class TestWorldQueries:
    """Test World actor query methods."""

    def test_world_get_actor_by_name(self):
        """World can get actor by name."""
        world = World()
        actor1 = Actor(name="Player")
        actor2 = Actor(name="Enemy")
        world.spawn_actor(actor1)
        world.spawn_actor(actor2)

        found = world.get_actor_by_name("Player")
        assert found is actor1

    def test_get_actor_by_name_returns_none_if_not_found(self):
        """get_actor_by_name returns None if not found."""
        world = World()
        found = world.get_actor_by_name("NonExistent")
        assert found is None

    def test_world_get_actors_by_type(self):
        """World can get actors by type."""
        class PlayerActor(Actor):
            pass

        class EnemyActor(Actor):
            pass

        world = World()
        player1 = PlayerActor()
        player2 = PlayerActor()
        enemy = EnemyActor()
        world.spawn_actor(player1)
        world.spawn_actor(player2)
        world.spawn_actor(enemy)

        players = world.get_actors_by_type(PlayerActor)
        assert len(players) == 2
        assert player1 in players
        assert player2 in players
        assert enemy not in players

    def test_get_actors_by_type_returns_empty_list_if_not_found(self):
        """get_actors_by_type returns empty list if not found."""
        class CustomActor(Actor):
            pass

        world = World()
        found = world.get_actors_by_type(CustomActor)
        assert found == []

    def test_world_get_all_actors(self):
        """World can get all actors."""
        world = World()
        actor1 = Actor()
        actor2 = Actor()
        world.spawn_actor(actor1)
        world.spawn_actor(actor2)

        all_actors = world.get_all_actors()
        assert len(all_actors) == 2


class TestWorldActorCount:
    """Test World actor count."""

    def test_world_actor_count(self):
        """World should track actor count."""
        world = World()
        assert world.actor_count == 0

        actor1 = Actor()
        actor2 = Actor()
        world.spawn_actor(actor1)
        world.spawn_actor(actor2)
        assert world.actor_count == 2

        world.destroy_actor(actor1)
        assert world.actor_count == 1


class TestWorldSerialization:
    """Test World serialization."""

    def test_world_serialize(self):
        """World should serialize basic properties."""
        world = World(name="Level1")
        data = world.serialize()

        assert data["name"] == "Level1"

    def test_world_deserialize(self):
        """World should deserialize basic properties."""
        world = World()
        data = {"name": "DeserializedWorld"}

        world.deserialize(data)
        assert world.name == "DeserializedWorld"


class TestWorldClear:
    """Test World clear functionality."""

    def test_world_has_clear_method(self):
        """World should have clear method."""
        world = World()
        assert hasattr(world, "clear")
        assert callable(world.clear)

    def test_clear_removes_all_actors(self):
        """Clear should remove all actors."""
        world = World()
        world.spawn_actor(Actor())
        world.spawn_actor(Actor())
        world.spawn_actor(Actor())

        world.clear()

        assert world.actor_count == 0


class TestWorldRepr:
    """Test World string representation."""

    def test_world_repr(self):
        """World should have useful repr."""
        world = World(name="TestWorld")
        world.spawn_actor(Actor())
        repr_str = repr(world)

        assert "World" in repr_str
        assert "TestWorld" in repr_str


class TestWorldEnabled:
    """Test World enabled state."""

    def test_world_has_enabled_property(self):
        """World should have enabled property."""
        world = World()
        assert hasattr(world, "enabled")

    def test_world_enabled_by_default(self):
        """World should be enabled by default."""
        world = World()
        assert world.enabled is True

    def test_disabled_world_skips_tick(self):
        """Disabled world should not tick actors."""
        tick_results = []

        class TestActor(Actor):
            def tick(self, delta_time: float):
                tick_results.append(delta_time)

        world = World()
        actor = TestActor()
        world.spawn_actor(actor)
        world.enabled = False
        world.tick(0.016)

        assert len(tick_results) == 0
