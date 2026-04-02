"""Tests for Combat Polish system.

Test-First Development for Combat Polish (Days 16-17)
"""
import math
from engine.game.combat_polish import (
    DamageNumber, DamageNumberManager,
    ScreenShake, ScreenShakeManager,
    HitEffect, HitEffectManager,
    CombatPolishManager
)
from core.vec import Vec2, Vec3
from core.color import Color


class TestDamageNumber:
    """Test floating damage numbers."""
    
    def test_creation(self):
        """Test damage number creation."""
        num = DamageNumber(
            value=50,
            position=Vec3(100, 200, 0)
        )
        
        assert num.value == 50
        assert num.position.x == 100
        assert num.lifetime == 1.5
    
    def test_update_moves_up(self):
        """Test that damage number moves up."""
        num = DamageNumber(
            value=25,
            position=Vec3(100, 200, 0),
            velocity=Vec2(0, 100)
        )
        
        initial_y = num.position.y
        num.update(0.1)
        
        assert num.position.y > initial_y
    
    def test_lifetime_decreases(self):
        """Test lifetime decreases over time."""
        num = DamageNumber(value=10, position=Vec3(0, 0, 0))
        
        initial_life = num.lifetime
        num.update(0.1)
        
        assert num.lifetime < initial_life
    
    def test_expires(self):
        """Test damage number expires."""
        num = DamageNumber(value=10, position=Vec3(0, 0, 0))
        
        # Fast forward past lifetime
        result = num.update(2.0)
        
        assert result is False
    
    def test_alpha_fades(self):
        """Test alpha fades with lifetime."""
        num = DamageNumber(value=10, position=Vec3(0, 0, 0))
        
        initial_alpha = num.get_alpha()
        num.update(0.5)
        later_alpha = num.get_alpha()
        
        assert later_alpha < initial_alpha
    
    def test_critical_display(self):
        """Test critical hit display text."""
        normal = DamageNumber(value=25, position=Vec3(0, 0, 0), critical=False)
        critical = DamageNumber(value=50, position=Vec3(0, 0, 0), critical=True)
        
        assert normal.get_display_text() == "25"
        assert critical.get_display_text() == "50!"


class TestDamageNumberManager:
    """Test damage number manager."""
    
    def test_spawn_damage(self):
        """Test spawning damage number."""
        manager = DamageNumberManager()
        
        num = manager.spawn(100, Vec3(50, 50, 0))
        
        assert num.value == 100
        assert manager.get_active_count() == 1
    
    def test_spawn_critical(self):
        """Test spawning critical hit."""
        manager = DamageNumberManager()
        
        num = manager.spawn(200, Vec3(0, 0, 0), critical=True)
        
        assert num.critical is True
        assert num.scale == 1.5
    
    def test_spawn_heal(self):
        """Test spawning heal number."""
        manager = DamageNumberManager()
        
        num = manager.spawn(50, Vec3(0, 0, 0), heal=True)
        
        assert num.color == manager.heal_color
        assert num.value == 50
    
    def test_update_removes_expired(self):
        """Test update removes expired numbers."""
        manager = DamageNumberManager()
        manager.spawn(10, Vec3(0, 0, 0))
        
        # Fast forward
        manager.update(2.0)
        
        assert manager.get_active_count() == 0
    
    def test_velocity_spread(self):
        """Test spawn applies random velocity spread."""
        manager = DamageNumberManager()
        
        num1 = manager.spawn(10, Vec3(0, 0, 0))
        num2 = manager.spawn(10, Vec3(0, 0, 0))
        
        # Different random spreads
        assert num1.velocity.x != num2.velocity.x


class TestScreenShake:
    """Test screen shake effect."""
    
    def test_creation(self):
        """Test shake creation."""
        shake = ScreenShake(intensity=10.0, duration=0.5, max_duration=0.5)
        
        assert shake.intensity == 10.0
        assert shake.duration == 0.5
    
    def test_update_returns_offset(self):
        """Test update returns offset vector."""
        shake = ScreenShake(intensity=10.0, duration=0.3, max_duration=0.3)
        
        offset = shake.update(0.1)
        
        assert offset is not None
        assert isinstance(offset, Vec2)
    
    def test_intensity_decreases(self):
        """Test intensity decreases over time."""
        shake = ScreenShake(intensity=20.0, duration=0.5, max_duration=0.5)
        
        # First offset at start
        offset1 = shake.update(0.01)
        mag1 = math.sqrt(offset1.x**2 + offset1.y**2)
        
        # Update to near end
        shake.duration = 0.1
        offset2 = shake.update(0.01)
        mag2 = math.sqrt(offset2.x**2 + offset2.y**2)
        
        assert mag2 < mag1
    
    def test_expires(self):
        """Test shake expires after duration."""
        shake = ScreenShake(intensity=10.0, duration=0.1, max_duration=0.1)
        
        offset = shake.update(0.2)
        
        assert offset is None
        assert shake.is_active() is False


class TestScreenShakeManager:
    """Test shake manager."""
    
    def test_add_shake(self):
        """Test adding shake."""
        manager = ScreenShakeManager()
        
        shake = manager.add_shake(15.0, 0.4)
        
        assert shake.intensity == 15.0
        assert manager.get_active_count() == 1
    
    def test_light_hit(self):
        """Test light hit preset."""
        manager = ScreenShakeManager()
        manager.light_hit()
        
        assert manager.get_active_count() == 1
    
    def test_medium_hit(self):
        """Test medium hit preset."""
        manager = ScreenShakeManager()
        manager.medium_hit()
        
        assert manager.get_active_count() == 1
    
    def test_heavy_hit(self):
        """Test heavy hit preset."""
        manager = ScreenShakeManager()
        manager.heavy_hit()
        
        shake = manager.shakes[0]
        assert shake.intensity >= 15.0
    
    def test_explosion(self):
        """Test explosion preset."""
        manager = ScreenShakeManager()
        manager.explosion()
        
        shake = manager.shakes[0]
        assert shake.intensity >= 30.0
        assert shake.max_duration >= 0.7
    
    def test_combined_offset(self):
        """Test multiple shakes combine."""
        manager = ScreenShakeManager()
        manager.light_hit()
        manager.light_hit()
        
        offset = manager.update(0.01)
        
        assert offset.x != 0 or offset.y != 0
    
    def test_update_removes_expired(self):
        """Test update removes expired shakes."""
        manager = ScreenShakeManager()
        manager.add_shake(10.0, 0.1)
        
        manager.update(0.2)
        
        assert manager.get_active_count() == 0


class TestHitEffect:
    """Test hit visual effects."""
    
    def test_creation(self):
        """Test effect creation."""
        effect = HitEffect(
            position=Vec3(100, 200, 0),
            effect_type='slash',
            lifetime=0.4,
            max_lifetime=0.4,
            color=Color(1, 0, 0)
        )
        
        assert effect.effect_type == 'slash'
        assert effect.position.x == 100
    
    def test_progress_calculation(self):
        """Test progress calculation."""
        effect = HitEffect(
            position=Vec3(0, 0, 0),
            effect_type='impact',
            lifetime=0.2,
            max_lifetime=0.4
        )
        
        progress = effect.get_progress()
        
        assert progress == 0.5  # Half done
    
    def test_expires(self):
        """Test effect expires."""
        effect = HitEffect(
            position=Vec3(0, 0, 0),
            effect_type='impact',
            lifetime=0.1,
            max_lifetime=0.4
        )
        
        result = effect.update(0.2)
        
        assert result is False


class TestHitEffectManager:
    """Test hit effect manager."""
    
    def test_spawn_effect(self):
        """Test spawning effect."""
        manager = HitEffectManager()
        
        effect = manager.spawn(Vec3(100, 100, 0), 'slash')
        
        assert effect.effect_type == 'slash'
        assert manager.get_active_count() == 1
    
    def test_spawn_critical(self):
        """Test spawning critical effect."""
        manager = HitEffectManager()
        
        effect = manager.spawn_critical(Vec3(0, 0, 0))
        
        assert effect.effect_type == 'critical'
        assert effect.scale == 1.5
    
    def test_effect_colors(self):
        """Test different effect types have colors."""
        manager = HitEffectManager()
        
        slash = manager.spawn(Vec3(0, 0, 0), 'slash')
        impact = manager.spawn(Vec3(0, 0, 0), 'impact')
        magic = manager.spawn(Vec3(0, 0, 0), 'magic')
        
        assert slash.color != impact.color
        assert magic.color == manager.effect_colors['magic']
    
    def test_update_removes_expired(self):
        """Test update removes expired effects."""
        manager = HitEffectManager()
        manager.spawn(Vec3(0, 0, 0), 'impact')
        
        manager.update(1.0)
        
        assert manager.get_active_count() == 0


class TestCombatPolishManager:
    """Test combined combat polish manager."""
    
    def test_creation(self):
        """Test manager creation."""
        manager = CombatPolishManager()
        
        assert manager.damage_numbers is not None
        assert manager.screen_shake is not None
        assert manager.hit_effects is not None
    
    def test_process_hit(self):
        """Test processing complete hit."""
        manager = CombatPolishManager()
        
        manager.process_hit(50, Vec3(100, 200, 0))
        
        assert manager.damage_numbers.get_active_count() == 1
        assert manager.hit_effects.get_active_count() == 1
    
    def test_process_critical_hit(self):
        """Test processing critical hit."""
        manager = CombatPolishManager()
        
        manager.process_hit(100, Vec3(0, 0, 0), critical=True)
        
        # Should have damage number, effect, and shake
        assert manager.damage_numbers.get_active_count() == 1
        assert manager.hit_effects.get_active_count() == 1
        assert manager.screen_shake.get_active_count() == 1
    
    def test_process_heal(self):
        """Test processing heal."""
        manager = CombatPolishManager()
        
        manager.process_heal(30, Vec3(50, 50, 0))
        
        assert manager.damage_numbers.get_active_count() == 1
    
    def test_update_returns_shake(self):
        """Test update returns screen shake offset."""
        manager = CombatPolishManager()
        manager.process_hit(100, Vec3(0, 0, 0), critical=True)
        
        offset = manager.update(0.01)
        
        assert isinstance(offset, Vec2)
