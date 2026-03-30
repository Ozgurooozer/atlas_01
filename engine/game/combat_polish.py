"""Combat Polish System - Hit effects, screenshake, damage numbers.

Provides game feel enhancements for combat scenarios.

Layer: 4 (Game)
Dependencies: core.vec, core.color, engine.renderer.particle3d
"""
import math
import random
from typing import List, Optional, Callable
from dataclasses import dataclass, field
from core.vec import Vec2, Vec3
from core.color import Color


@dataclass
class DamageNumber:
    """Floating damage number indicator."""
    
    value: int
    position: Vec3
    velocity: Vec2 = field(default_factory=lambda: Vec2(0, -50))
    color: Color = field(default_factory=lambda: Color(1, 1, 1))
    lifetime: float = 1.5
    max_lifetime: float = 1.5
    scale: float = 1.0
    critical: bool = False
    
    def update(self, dt: float) -> bool:
        """Update damage number. Returns False if expired."""
        # Move up
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt
        
        # Slow down
        self.velocity = Vec2(self.velocity.x * 0.95, self.velocity.y * 0.95)
        
        # Fade
        self.lifetime -= dt
        
        return self.lifetime > 0
    
    def get_alpha(self) -> float:
        """Get current alpha based on lifetime."""
        return max(0.0, self.lifetime / self.max_lifetime)
    
    def get_display_text(self) -> str:
        """Get formatted damage text."""
        if self.critical:
            return f"{self.value}!"
        return str(self.value)


class DamageNumberManager:
    """Manages floating damage numbers."""
    
    def __init__(self):
        """Initialize damage number manager."""
        self.numbers: List[DamageNumber] = []
        self.critical_color = Color(1.0, 0.3, 0.1)
        self.normal_color = Color(1.0, 1.0, 1.0)
        self.heal_color = Color(0.3, 1.0, 0.3)
    
    def spawn(self, value: int, position: Vec3, 
              critical: bool = False, heal: bool = False) -> DamageNumber:
        """Spawn new damage number.
        
        Args:
            value: Damage/heal amount
            position: World position
            critical: Is critical hit
            heal: Is healing
            
        Returns:
            Created damage number
        """
        # Random spread
        spread_x = random.uniform(-30, 30)
        spread_y = random.uniform(-20, 20)
        
        velocity = Vec2(spread_x, 80 + spread_y)  # Float up
        
        # Color based on type
        if heal:
            color = self.heal_color
        elif critical:
            color = self.critical_color
        else:
            color = self.normal_color
        
        number = DamageNumber(
            value=abs(value),
            position=position,
            velocity=velocity,
            color=color,
            scale=1.5 if critical else 1.0,
            critical=critical
        )
        
        self.numbers.append(number)
        return number
    
    def update(self, dt: float) -> None:
        """Update all damage numbers."""
        self.numbers = [n for n in self.numbers if n.update(dt)]
    
    def clear(self) -> None:
        """Clear all damage numbers."""
        self.numbers.clear()
    
    def get_active_count(self) -> int:
        """Get count of active damage numbers."""
        return len(self.numbers)


@dataclass
class ScreenShake:
    """Screen shake effect data."""
    
    intensity: float
    duration: float
    max_duration: float
    frequency: float = 20.0
    
    def update(self, dt: float) -> Optional[Vec2]:
        """Update shake and get offset. Returns None if expired."""
        self.duration -= dt
        
        if self.duration <= 0:
            return None
        
        # Calculate remaining intensity
        progress = self.duration / self.max_duration
        current_intensity = self.intensity * progress
        
        # Random shake offset
        offset_x = math.sin(self.duration * self.frequency) * current_intensity
        offset_y = math.cos(self.duration * self.frequency * 1.3) * current_intensity
        
        return Vec2(offset_x, offset_y)
    
    def is_active(self) -> bool:
        """Check if shake is still active."""
        return self.duration > 0


class ScreenShakeManager:
    """Manages screen shake effects."""
    
    def __init__(self):
        """Initialize shake manager."""
        self.shakes: List[ScreenShake] = []
        self.default_duration = 0.3
        self.default_intensity = 10.0
    
    def add_shake(self, intensity: float, duration: float) -> ScreenShake:
        """Add screen shake.
        
        Args:
            intensity: Shake magnitude in pixels
            duration: Shake duration in seconds
            
        Returns:
            Created shake effect
        """
        shake = ScreenShake(
            intensity=intensity,
            duration=duration,
            max_duration=duration
        )
        self.shakes.append(shake)
        return shake
    
    def light_hit(self) -> None:
        """Small shake for light hits."""
        self.add_shake(5.0, 0.2)
    
    def medium_hit(self) -> None:
        """Medium shake for normal hits."""
        self.add_shake(10.0, 0.3)
    
    def heavy_hit(self) -> None:
        """Heavy shake for critical hits/impacts."""
        self.add_shake(20.0, 0.5)
    
    def explosion(self) -> None:
        """Large shake for explosions."""
        self.add_shake(35.0, 0.8)
    
    def update(self, dt: float) -> Vec2:
        """Update all shakes and get combined offset."""
        total_offset = Vec2(0, 0)
        active_shakes = []
        
        # Update and filter expired shakes
        for shake in self.shakes:
            offset = shake.update(dt)
            if offset is not None:
                total_offset.x += offset.x
                total_offset.y += offset.y
                active_shakes.append(shake)
        
        self.shakes = active_shakes
        return total_offset
    
    def get_active_count(self) -> int:
        """Get number of active shakes."""
        return len(self.shakes)


@dataclass
class HitEffect:
    """Visual hit effect data."""
    
    position: Vec3
    effect_type: str
    lifetime: float
    max_lifetime: float
    scale: float = 1.0
    rotation: float = 0.0
    color: Color = field(default_factory=lambda: Color(1, 0, 0))
    
    def update(self, dt: float) -> bool:
        """Update effect. Returns False if expired."""
        self.lifetime -= dt
        return self.lifetime > 0
    
    def get_progress(self) -> float:
        """Get completion progress (0-1)."""
        return 1.0 - (self.lifetime / self.max_lifetime)


class HitEffectManager:
    """Manages hit visual effects."""
    
    def __init__(self):
        """Initialize hit effect manager."""
        self.effects: List[HitEffect] = []
        self.effect_colors = {
            'slash': Color(1.0, 0.8, 0.3),
            'impact': Color(1.0, 0.5, 0.1),
            'critical': Color(1.0, 0.1, 0.1),
            'magic': Color(0.4, 0.4, 1.0),
            'poison': Color(0.2, 0.8, 0.2),
            'ice': Color(0.5, 0.8, 1.0),
        }
    
    def spawn(self, position: Vec3, effect_type: str = 'impact',
              scale: float = 1.0) -> HitEffect:
        """Spawn hit effect.
        
        Args:
            position: World position
            effect_type: Effect type name
            scale: Size scale
            
        Returns:
            Created effect
        """
        color = self.effect_colors.get(effect_type, Color(1, 1, 1))
        
        effect = HitEffect(
            position=position,
            effect_type=effect_type,
            lifetime=0.4,
            max_lifetime=0.4,
            scale=scale,
            rotation=random.uniform(0, 360),
            color=color
        )
        
        self.effects.append(effect)
        return effect
    
    def spawn_critical(self, position: Vec3) -> HitEffect:
        """Spawn critical hit effect."""
        return self.spawn(position, 'critical', scale=1.5)
    
    def update(self, dt: float) -> None:
        """Update all effects."""
        self.effects = [e for e in self.effects if e.update(dt)]
    
    def clear(self) -> None:
        """Clear all effects."""
        self.effects.clear()
    
    def get_active_count(self) -> int:
        """Get count of active effects."""
        return len(self.effects)


class CombatPolishManager:
    """Central manager for all combat polish effects."""
    
    def __init__(self):
        """Initialize combat polish manager."""
        self.damage_numbers = DamageNumberManager()
        self.screen_shake = ScreenShakeManager()
        self.hit_effects = HitEffectManager()
        
        # Callbacks
        self.on_hit: Optional[Callable] = None
        self.on_critical: Optional[Callable] = None
    
    def process_hit(self, damage: int, position: Vec3,
                   critical: bool = False) -> None:
        """Process complete hit with all effects.
        
        Args:
            damage: Damage amount
            position: Hit position
            critical: Is critical hit
        """
        # Damage number
        self.damage_numbers.spawn(damage, position, critical=critical)
        
        # Screen shake
        if critical:
            self.screen_shake.heavy_hit()
        elif damage > 50:
            self.screen_shake.medium_hit()
        else:
            self.screen_shake.light_hit()
        
        # Hit effect
        if critical:
            self.hit_effects.spawn_critical(position)
        else:
            self.hit_effects.spawn(position, 'impact')
        
        # Trigger callback
        if critical and self.on_critical:
            self.on_critical(damage, position)
        elif self.on_hit:
            self.on_hit(damage, position)
    
    def process_heal(self, amount: int, position: Vec3) -> None:
        """Process heal with effects."""
        self.damage_numbers.spawn(amount, position, heal=True)
    
    def update(self, dt: float) -> Vec2:
        """Update all polish effects.
        
        Returns:
            Screen shake offset
        """
        self.damage_numbers.update(dt)
        self.hit_effects.update(dt)
        return self.screen_shake.update(dt)
    
    def clear(self) -> None:
        """Clear all effects."""
        self.damage_numbers.clear()
        self.hit_effects.clear()
        self.shakes = []
