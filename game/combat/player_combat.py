"""
Player Combat Script.

Manages player combat actions: attack, dash, skill use.
Uses StateMachine for player states and connects to InputHandler actions.

Layer: 4 (Game/Combat)
Dependencies: scripting.statemachine, world components
"""
from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

from scripting.statemachine import State, StateMachine
from core.vec import Vec2
from world.actor import Actor
from world.components.hitbox_component import HitboxComponent
from world.components.hurtbox_component import HurtboxComponent
from world.components.health_component import HealthComponent
from world.components.combat_stats_component import CombatStatsComponent
from world.components.combat_state_component import CombatStateComponent
from world.transform import TransformComponent

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLAYER_STATE_IDLE = "IDLE"
PLAYER_STATE_MOVE = "MOVE"
PLAYER_STATE_ATTACK = "ATTACK"
PLAYER_STATE_DASH = "DASH"
PLAYER_STATE_HURT = "HURT"
PLAYER_STATE_DEAD = "DEAD"

ATTACK_DURATION = 0.3       # seconds the hitbox stays active
ATTACK_COOLDOWN = 0.5       # seconds before next attack can start
COMBO_WINDOW = 0.8          # seconds to chain the next combo hit
MAX_COMBO_HITS = 3          # basic 3-hit combo

DASH_DURATION = 0.2         # seconds the dash lasts
DASH_COOLDOWN = 1.0         # seconds before dash is available again
DASH_SPEED = 600.0          # pixels/second during dash
DASH_IFRAMES = 0.25         # invincibility duration on dash

HURT_DURATION = 0.35        # seconds the hurt state lasts
HURT_IFRAMES = 0.5          # invincibility after taking damage

SKILL_COOLDOWNS: Dict[str, float] = {
    "skill_0": 3.0,
    "skill_1": 5.0,
    "skill_2": 8.0,
}


# ---------------------------------------------------------------------------
# State classes
# ---------------------------------------------------------------------------

class _PlayerState(State):
    """Base player state with a back-reference to the script."""

    def __init__(self, name: str, script: "PlayerCombatScript"):
        super().__init__(name=name)
        self.script = script


class _IdleState(_PlayerState):
    """Waiting for input. Can transition to MOVE, ATTACK, DASH."""

    def tick(self, dt: float) -> None:
        # Decay combo timer while idle
        if self.script._combo_timer > 0:
            self.script._combo_timer -= dt
            if self.script._combo_timer <= 0:
                self.script._combo_count = 0


class _MoveState(_PlayerState):
    """Moving state. Can transition to ATTACK, DASH, IDLE."""

    def tick(self, dt: float) -> None:
        pass  # Movement handled by a separate movement script or controller


class _AttackState(_PlayerState):
    """Attack in progress. Activates hitbox, then transitions back."""

    def on_enter(self, context: Any = None) -> None:
        self.script._attack_timer = ATTACK_DURATION
        self.script._activate_attack_hitbox()

    def on_exit(self, context: Any = None) -> None:
        self.script._deactivate_hitbox()

    def tick(self, dt: float) -> None:
        self.script._attack_timer -= dt
        if self.script._attack_timer <= 0:
            self.script._attack_timer = 0.0
            # Set cooldown
            state_comp = self.script._get_combat_state()
            if state_comp:
                state_comp.set_cooldown("attack", ATTACK_COOLDOWN)
            # Start combo window
            self.script._combo_timer = COMBO_WINDOW
            # Go back to idle; next attack press during combo window chains
            self.script._state_machine.transition(PLAYER_STATE_IDLE)


class _DashState(_PlayerState):
    """Dashing with i-frames. Moves in a direction, then returns to IDLE."""

    def on_enter(self, context: Any = None) -> None:
        self.script._dash_timer = DASH_DURATION
        direction: Vec2 = context if isinstance(context, Vec2) else Vec2.RIGHT
        self.script._dash_direction = direction.normalized() if direction.length() > 0 else Vec2.RIGHT
        # Grant i-frames
        health = self.script._get_health()
        if health:
            health.set_invincible(DASH_IFRAMES)

    def on_exit(self, context: Any = None) -> None:
        # Set dash cooldown
        state_comp = self.script._get_combat_state()
        if state_comp:
            state_comp.set_cooldown("dash", DASH_COOLDOWN)

    def tick(self, dt: float) -> None:
        self.script._dash_timer -= dt
        # Apply dash movement
        transform = self.script._get_transform()
        if transform:
            dx = self.script._dash_direction.x * DASH_SPEED * dt
            dy = self.script._dash_direction.y * DASH_SPEED * dt
            transform.translate(dx, dy)

        if self.script._dash_timer <= 0:
            self.script._dash_timer = 0.0
            self.script._state_machine.transition(PLAYER_STATE_IDLE)


class _HurtState(_PlayerState):
    """Taking damage. Brief stun, then return to IDLE."""

    def on_enter(self, context: Any = None) -> None:
        self.script._hurt_timer = HURT_DURATION
        # Grant i-frames
        health = self.script._get_health()
        if health:
            health.set_invincible(HURT_IFRAMES)

    def tick(self, dt: float) -> None:
        self.script._hurt_timer -= dt
        if self.script._hurt_timer <= 0:
            self.script._hurt_timer = 0.0
            health = self.script._get_health()
            if health and not health.is_dead:
                self.script._state_machine.transition(PLAYER_STATE_IDLE)
            elif health and health.is_dead:
                self.script._state_machine.transition(PLAYER_STATE_DEAD)


class _DeadState(_PlayerState):
    """Player is dead. No transitions out."""

    def on_enter(self, context: Any = None) -> None:
        # Deactivate hitbox if active
        self.script._deactivate_hitbox()
        # Disable hurtbox
        hurtbox = self.script._get_hurtbox()
        if hurtbox:
            hurtbox.disable()


# ---------------------------------------------------------------------------
# PlayerCombatScript
# ---------------------------------------------------------------------------

class PlayerCombatScript:
    """
    Player combat controller script.

    Manages player combat actions (attack, dash, skills) using a state
    machine. Designed to be used with :class:`ScriptComponent`::

        script = PlayerCombatScript(actor, blackboard)
        component = ScriptComponent(script=script)
        player_actor.add_component(component)

    The script follows the ``ScriptComponent``-compatible lifecycle:

    * ``on_start()`` – called once when attached (via ``ScriptComponent``).
    * ``on_tick(dt)`` – called every frame.
    * ``on_destroy()`` – called on detach.

    Combo system:
        Up to 3 consecutive attacks.  Each must be triggered within the
        ``COMBO_WINDOW`` (0.8 s) of the previous hit landing, otherwise
        the counter resets.

    Dash:
        A short burst of speed with invincibility frames.  Subject to
        ``DASH_COOLDOWN`` (1.0 s).

    Skills:
        Three skill slots with independent cooldowns.
    """

    def __init__(
        self,
        actor: Optional[Actor] = None,
        blackboard: Optional[Dict[str, Any]] = None,
    ) -> None:
        # Set by ScriptComponent or passed in constructor
        self.actor: Optional[Actor] = actor
        self.blackboard: Dict[str, Any] = blackboard if blackboard is not None else {}

        # State machine (built lazily in on_start)
        self._state_machine: Optional[StateMachine] = None

        # Combo tracking
        self._combo_count: int = 0
        self._combo_timer: float = 0.0

        # Attack timing
        self._attack_timer: float = 0.0

        # Dash
        self._dash_timer: float = 0.0
        self._dash_direction: Vec2 = Vec2.RIGHT

        # Hurt
        self._hurt_timer: float = 0.0

        # Kill callback reference (set by RunController or similar)
        self._on_kill_callback: Optional[Any] = None

    # -- Public API ----------------------------------------------------------

    @property
    def state_name(self) -> str:
        """Return the name of the current player state."""
        if self._state_machine is None:
            return PLAYER_STATE_IDLE
        return self._state_machine.current_state.name

    @property
    def combo_count(self) -> int:
        """Current combo hit count (0 .. MAX_COMBO_HITS)."""
        return self._combo_count

    @property
    def is_attacking(self) -> bool:
        return self.state_name == PLAYER_STATE_ATTACK

    @property
    def is_dashing(self) -> bool:
        return self.state_name == PLAYER_STATE_DASH

    @property
    def is_hurt(self) -> bool:
        return self.state_name == PLAYER_STATE_HURT

    @property
    def is_dead(self) -> bool:
        return self.state_name == PLAYER_STATE_DEAD

    @property
    def can_attack(self) -> bool:
        """True when the player may start an attack."""
        if self.actor is None:
            return False
        if self.state_name not in (PLAYER_STATE_IDLE, PLAYER_STATE_MOVE):
            return False
        # Combo chains bypass the normal attack cooldown
        if self._combo_timer > 0 and self._combo_count < MAX_COMBO_HITS:
            return True
        state_comp = self._get_combat_state()
        if state_comp and state_comp.is_on_cooldown("attack"):
            return False
        return True

    @property
    def can_dash(self) -> bool:
        """True when the player may start a dash."""
        if self.actor is None:
            return False
        if self.state_name not in (PLAYER_STATE_IDLE, PLAYER_STATE_MOVE):
            return False
        state_comp = self._get_combat_state()
        if state_comp and state_comp.is_on_cooldown("dash"):
            return False
        return True

    def attack(self) -> bool:
        """
        Trigger a basic attack.

        If a combo is in progress (within ``COMBO_WINDOW``) the next
        combo hit is delivered; otherwise the combo resets.

        Returns:
            ``True`` if the attack was initiated.
        """
        # Combo chains bypass the normal cooldown
        is_combo_chain = (
            self._combo_timer > 0
            and self._combo_count < MAX_COMBO_HITS
            and self.state_name in (PLAYER_STATE_IDLE, PLAYER_STATE_MOVE)
            and self.actor is not None
        )

        if not self.can_attack and not is_combo_chain:
            return False

        if self.state_name not in (PLAYER_STATE_IDLE, PLAYER_STATE_MOVE):
            return False
        if self.actor is None:
            return False

        # Advance combo
        if is_combo_chain:
            self._combo_count += 1
            # Clear attack cooldown so the combo chain is not blocked
            state_comp = self._get_combat_state()
            if state_comp:
                state_comp.set_cooldown("attack", 0.0)
        else:
            self._combo_count = 1

        self._combo_timer = 0.0
        if self._state_machine:
            self._state_machine.transition(PLAYER_STATE_ATTACK)
        return True

    def dash(self, direction: Vec2) -> bool:
        """
        Trigger a dash in the given direction.

        Args:
            direction: Dash direction vector.

        Returns:
            ``True`` if the dash was initiated.
        """
        if not self.can_dash:
            return False

        if self._state_machine:
            self._state_machine.transition(PLAYER_STATE_DASH, context=direction)
        return True

    def use_skill(self, index: int) -> bool:
        """
        Activate a skill by slot index (0, 1, 2).

        Args:
            index: Skill slot index.

        Returns:
            ``True`` if the skill was activated.
        """
        if self.state_name not in (PLAYER_STATE_IDLE, PLAYER_STATE_MOVE):
            return False

        key = f"skill_{index}"
        if key not in SKILL_COOLDOWNS:
            return False

        state_comp = self._get_combat_state()
        if state_comp and state_comp.is_on_cooldown(key):
            return False

        # Set cooldown
        if state_comp:
            state_comp.set_cooldown(key, SKILL_COOLDOWNS[key])

        # Skills are fire-and-forget; the actual effect is defined
        # externally (e.g. projectile spawn) via the blackboard or
        # an event.  We just manage the cooldown here.
        return True

    def take_hit(self, damage_data: Any) -> float:
        """
        Receive damage from an external source.

        Args:
            damage_data: A :class:`DamageData` instance or a numeric
                         damage amount.

        Returns:
            Actual damage dealt (0 if invincible / dead).
        """
        health = self._get_health()
        if health is None:
            return 0.0

        if health.is_dead:
            return 0.0

        amount = getattr(damage_data, "amount", damage_data) if not isinstance(damage_data, (int, float)) else float(damage_data)
        amount = float(amount)

        # Check invincibility
        if health.is_invincible:
            return 0.0

        # Apply damage
        actual = health.take_damage(amount)

        if actual > 0:
            # Enter hurt state (unless already dashing with i-frames, which
            # would have blocked damage above)
            if health.is_dead:
                if self._state_machine:
                    self._state_machine.transition(PLAYER_STATE_DEAD)
            else:
                if self._state_machine and self.state_name != PLAYER_STATE_DEAD:
                    self._state_machine.transition(PLAYER_STATE_HURT)
                # Reset combo on hit
                self._combo_count = 0
                self._combo_timer = 0.0

        return actual

    def report_kill(self, target: Any) -> None:
        """
        Report that the player killed a target.

        Args:
            target: The killed actor/entity.
        """
        if self._on_kill_callback:
            self._on_kill_callback(target)

    # -- Lifecycle (called by ScriptComponent) --------------------------------

    def on_start(self) -> None:
        """Initialize the state machine when the script is first attached."""
        if self._state_machine is not None:
            return  # Already initialised

        idle = _IdleState(PLAYER_STATE_IDLE, self)
        move = _MoveState(PLAYER_STATE_MOVE, self)
        attack = _AttackState(PLAYER_STATE_ATTACK, self)
        dash = _DashState(PLAYER_STATE_DASH, self)
        hurt = _HurtState(PLAYER_STATE_HURT, self)
        dead = _DeadState(PLAYER_STATE_DEAD, self)

        self._state_machine = StateMachine(initial_state=idle)
        for s in (move, attack, dash, hurt, dead):
            self._state_machine.add_state(s)

    def on_tick(self, dt: float) -> None:
        """Tick the state machine and combat state component."""
        if self._state_machine is None:
            return

        # Tick state machine FIRST so that any cooldowns it sets
        # can be decremented by the combat-state tick in the same frame.
        self._state_machine.tick(dt)

        # Tick combat state component (cooldowns, knockback, stun, etc.)
        state_comp = self._get_combat_state()
        if state_comp:
            state_comp.on_tick(dt)

        # Tick health component (invincibility timer)
        health = self._get_health()
        if health:
            health.on_tick(dt)

    def on_destroy(self) -> None:
        """Clean up when the script is detached."""
        self._deactivate_hitbox()

    def on_attach(self, actor: Actor) -> None:
        """Called when the script is attached to an actor."""
        self.actor = actor

    def on_detach(self) -> None:
        """Called when the script is detached from an actor."""
        self._deactivate_hitbox()
        self.actor = None

    # -- Internal helpers ----------------------------------------------------

    def _get_combat_state(self) -> Optional[CombatStateComponent]:
        if self.actor is None:
            return None
        return self.actor.get_component(CombatStateComponent)

    def _get_health(self) -> Optional[HealthComponent]:
        if self.actor is None:
            return None
        return self.actor.get_component(HealthComponent)

    def _get_hitbox(self) -> Optional[HitboxComponent]:
        if self.actor is None:
            return None
        return self.actor.get_component(HitboxComponent)

    def _get_hurtbox(self) -> Optional[HurtboxComponent]:
        if self.actor is None:
            return None
        return self.actor.get_component(HurtboxComponent)

    def _get_combat_stats(self) -> Optional[CombatStatsComponent]:
        if self.actor is None:
            return None
        return self.actor.get_component(CombatStatsComponent)

    def _get_transform(self) -> Optional[TransformComponent]:
        if self.actor is None:
            return None
        return self.actor.get_component(TransformComponent)

    def _activate_attack_hitbox(self) -> None:
        """Activate the hitbox with damage based on current combo step."""
        hitbox = self._get_hitbox()
        stats = self._get_combat_stats()
        if hitbox is None:
            return

        # Each combo hit does more damage (100%, 120%, 160%)
        multiplier = [1.0, 1.2, 1.6]
        mult = multiplier[min(self._combo_count - 1, len(multiplier) - 1)]

        if stats:
            hitbox.base_damage = stats.attack * mult
        hitbox.activate()

    def _deactivate_hitbox(self) -> None:
        hitbox = self._get_hitbox()
        if hitbox:
            hitbox.deactivate()

    def __repr__(self) -> str:
        return (
            f"PlayerCombatScript(state={self.state_name}, "
            f"combo={self._combo_count})"
        )
