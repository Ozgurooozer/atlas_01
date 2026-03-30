"""
Renderer Subsystem.

Provides 2D rendering using GPU device abstraction.
Uses ModernGL in production, HeadlessGPU for tests.

Layer: 2 (Engine)
Dependencies: engine.subsystem, hal.interfaces
"""

from __future__ import annotations
from abc import abstractmethod
from typing import Optional, Set, Tuple, TYPE_CHECKING

from engine.subsystem import ISubsystem
from engine.renderer.render_logger import RenderLogger

if TYPE_CHECKING:
    from engine.engine import Engine
    from engine.renderer.sprite import Sprite
    from engine.renderer.texture import Texture
    from engine.renderer.camera import Camera
    from engine.renderer.light import LightRenderer
    from engine.renderer.postprocess_stack import PostProcessStack
    from engine.renderer.render_config import RenderConfig
    from hal.interfaces import IGPUDevice, IFramebuffer


class IRenderer(ISubsystem):
    """
    Interface for rendering subsystems.

    Extends ISubsystem with rendering-specific methods.
    All renderers must implement clear() and present().
    """

    @abstractmethod
    def clear(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0) -> None:
        """
        Clear the screen with the given color.

        Args:
            r: Red component (0.0 - 1.0)
            g: Green component (0.0 - 1.0)
            b: Blue component (0.0 - 1.0)
            a: Alpha component (0.0 - 1.0)
        """
        pass

    @abstractmethod
    def present(self) -> None:
        """
        Present the rendered frame.

        Swaps buffers or presents to screen.
        """
        pass


class Renderer2D(IRenderer):
    """
    2D Renderer implementation.

    Provides basic 2D rendering capabilities:
    - Clear screen with background color
    - Present frame to display
    - Viewport management
    - Sprite and texture drawing

    Uses IGPUDevice abstraction for GPU operations.
    Works with HeadlessGPU for testing.

    Example:
        >>> renderer = Renderer2D()
        >>> renderer.gpu_device = HeadlessGPU()
        >>> renderer.initialize(engine)
        >>> renderer.clear(0.1, 0.1, 0.1, 1.0)
        >>> # Draw sprites here...
        >>> renderer.present()

    Attributes:
        gpu_device: The GPU device to use for rendering
        background_color: Default clear color (rgba tuple)
        viewport: Viewport rectangle (x, y, width, height)
        enabled: Whether rendering is active
        draw_count: Number of draw calls this frame
        texture_count: Number of unique textures used this frame
    """

    def __init__(self, config: "RenderConfig" = None):
        """Create a new Renderer2D.
        
        Args:
            config: Optional RenderConfig. Defaults to game_ready() preset.
        """
        from engine.renderer.render_config import RenderConfig as _RC
        self._config: _RC = config or _RC.game_ready()
        self._gpu_device: Optional["IGPUDevice"] = None
        self._background_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
        self._viewport: Tuple[int, int, int, int] = (0, 0, 800, 600)
        self._enabled: bool = True
        self._draw_count: int = 0
        self._texture_count: int = 0
        self._used_textures: Set[int] = set()
        self._camera: Optional["Camera"] = None
        self._light_renderer: Optional["LightRenderer"] = None
        self._post_process_stack: Optional["PostProcessStack"] = None
        self._scene_fbo: Optional["IFramebuffer"] = None
        self._forward_explicitly_enabled: bool = False
        # Feature freeze: SSAO ve deferred config'den okunur
        self._ssao_enabled: bool = self._config.ssao_enabled
        self._gbuffer: Optional["GBuffer"] = None
        self._ssao_pass: Optional["SSAOPass"] = None
        # Placeholder texture (lazy init)
        self._placeholder_texture: Optional["Texture"] = None

    @property
    def config(self) -> "RenderConfig":
        """Get render configuration."""
        return self._config

    @property
    def ssao_enabled(self) -> bool:
        """Get whether SSAO is enabled."""
        return self._ssao_enabled

    @ssao_enabled.setter
    def ssao_enabled(self, value: bool) -> None:
        """Set whether SSAO is enabled."""
        self._ssao_enabled = value

    @property
    def deferred_enabled(self) -> bool:
        """Get whether deferred lighting is enabled."""
        return self._light_renderer.deferred_enabled if self._light_renderer else False

    @deferred_enabled.setter
    def deferred_enabled(self, value: bool) -> None:
        """Set deferred lighting. Raises ValueError if forward is explicitly enabled."""
        if value and self._light_renderer and not self._light_renderer.deferred_enabled:
            # forward was explicitly set to True via forward_enabled setter
            if getattr(self, '_forward_explicitly_enabled', False):
                raise ValueError("Cannot enable deferred lighting while forward lighting is enabled")
        if self._light_renderer:
            self._light_renderer.deferred_enabled = value
        if value:
            self._forward_explicitly_enabled = False

    @property
    def forward_enabled(self) -> bool:
        """Get whether forward lighting is enabled (mutex with deferred)."""
        return not self.deferred_enabled

    @forward_enabled.setter
    def forward_enabled(self, value: bool) -> None:
        """Set forward lighting. Raises ValueError if deferred is already enabled."""
        if value and self.deferred_enabled:
            raise ValueError("Cannot enable forward lighting while deferred lighting is enabled")
        if self._light_renderer:
            self._light_renderer.deferred_enabled = not value
        self._forward_explicitly_enabled = value

    @property
    def name(self) -> str:
        """Get subsystem name."""
        return "renderer"

    @property
    def gpu_device(self) -> Optional["IGPUDevice"]:
        """Get the GPU device."""
        return self._gpu_device

    @gpu_device.setter
    def gpu_device(self, value: Optional["IGPUDevice"]) -> None:
        """Set the GPU device."""
        self._gpu_device = value

    @property
    def background_color(self) -> Tuple[float, float, float, float]:
        """Get the background color."""
        return self._background_color

    @background_color.setter
    def background_color(self, value: Tuple[float, float, float, float]) -> None:
        """Set the background color."""
        self._background_color = value

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """Get the viewport."""
        return self._viewport

    @viewport.setter
    def viewport(self, value: Tuple[int, int, int, int]) -> None:
        """Set the viewport."""
        self._viewport = value

    @property
    def enabled(self) -> bool:
        """Get whether rendering is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether rendering is enabled."""
        self._enabled = value

    @property
    def draw_count(self) -> int:
        """Get number of draw calls this frame."""
        return self._draw_count

    @property
    def texture_count(self) -> int:
        """Get number of unique textures used this frame."""
        return self._texture_count

    def initialize(self, engine: "Engine") -> None:
        """
        Initialize the renderer.

        Args:
            engine: Reference to the Engine instance
        """
        # Renderer is ready to use after initialization
        # GPU device should be set before or after
        pass

    def tick(self, dt: float) -> None:
        """
        Update the renderer for one frame.

        Resets draw statistics and clears the screen.

        Args:
            dt: Delta time in seconds
        """
        if not self._enabled:
            return

        # Reset frame statistics
        self._draw_count = 0
        self._texture_count = 0
        self._used_textures.clear()

        # Clear with background color at start of frame
        if self._gpu_device:
            r, g, b, a = self._background_color
            self._gpu_device.clear(r, g, b, a)

    def shutdown(self) -> None:
        """
        Clean up renderer resources.

        Clears GPU device reference.
        """
        self._gpu_device = None
        self._camera = None

    def set_camera(self, camera: Optional["Camera"]) -> None:
        """
        Set the active camera.

        Args:
            camera: The Camera to use for rendering.
        """
        self._camera = camera

    def set_light_renderer(self, lr: Optional["LightRenderer"]) -> None:
        """Set the light renderer."""
        self._light_renderer = lr

    def set_post_process_stack(self, pps: Optional["PostProcessStack"]) -> None:
        """Set the post-process stack."""
        self._post_process_stack = pps

    def begin_frame(self) -> None:
        """
        Prepare for a new frame.
        
        Binds scene FBO and clears it.
        """
        if not self._gpu_device:
            return

        # Create scene FBO if needed
        if self._scene_fbo is None:
            w, h = self._viewport[2], self._viewport[3]
            self._scene_fbo = self._gpu_device.create_framebuffer(w, h)

        if self._ssao_enabled:
            if self._gbuffer is None:
                from engine.renderer.gbuffer import GBuffer
                from engine.renderer.ssao import SSAOPass
                try:
                    w, h = self._viewport[2], self._viewport[3]
                    self._gbuffer = GBuffer(self._gpu_device, w, h)
                    self._ssao_pass = SSAOPass(self._gpu_device, w, h)
                except Exception as e:
                    RenderLogger.error("Failed to initialize SSAO, disabling", exc=e)
                    self._ssao_enabled = False
            
            if self._ssao_enabled and self._gbuffer:
                self._gbuffer.bind()
                r, g, b, a = self._background_color
                self._gpu_device.clear(r, g, b, a)
                return

        # Bind and clear scene FBO
        self._scene_fbo.bind()
        r, g, b, a = self._background_color
        self._gpu_device.clear(r, g, b, a)

    def end_frame(self) -> None:
        """
        Finalize the frame.
        
        Composites light map, applies post-processing, and blits to screen.
        """
        if not self._gpu_device or not self._scene_fbo:
            return

        if self._ssao_enabled and self._gbuffer:
            self._gbuffer.unbind()
            # SSAO Pass
            ssao_fbo = self._ssao_pass.render(self._gbuffer)
            ssao_blurred = self._ssao_pass.blur(ssao_fbo)
            # In a real implementation, we'd composite SSAO here

        # 1. Light Pass (if enabled)
        if self._light_renderer:
            self._light_renderer.begin_light_pass()
            # Lights are submitted during the frame
            self._light_renderer.end_light_pass()

        # 2. Post-processing
        final_fbo = self._scene_fbo
        if self._post_process_stack:
            final_fbo = self._post_process_stack.render(self._scene_fbo)

        # 3. Blit to screen
        final_fbo.unbind()
        self._gpu_device.flush()

    def clear(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0) -> None:
        """
        Clear the screen with the given color.

        Args:
            r: Red component (0.0 - 1.0)
            g: Green component (0.0 - 1.0)
            b: Blue component (0.0 - 1.0)
            a: Alpha component (0.0 - 1.0)
        """
        if self._gpu_device:
            self._gpu_device.clear(r, g, b, a)

    def present(self) -> None:
        """
        Present the rendered frame.

        Flushes GPU commands.
        """
        if self._gpu_device:
            self._gpu_device.flush()

    def _get_placeholder_texture(self) -> "Texture":
        """Lazy-init magenta placeholder texture."""
        if self._placeholder_texture is None:
            from engine.renderer.texture import Texture
            color = self._config.missing_texture_color
            self._placeholder_texture = Texture.from_color(32, 32, color)
            if self._gpu_device:
                self._ensure_uploaded(self._placeholder_texture)
        return self._placeholder_texture

    def _ensure_uploaded(self, texture: "Texture") -> None:
        """Texture GPU'ya yüklenmemişse yükle."""
        if not texture.is_uploaded and self._gpu_device:
            gpu_id = self._gpu_device.create_texture(
                texture.width, texture.height, texture.data
            )
            texture.mark_uploaded(gpu_id)

    def _track_texture(self, texture: "Texture") -> None:
        """Draw istatistiklerini güncelle."""
        self._draw_count += 1
        if texture.gpu_id not in self._used_textures:
            self._used_textures.add(texture.gpu_id)
            self._texture_count += 1

    def draw_sprite(self, sprite: "Sprite") -> None:
        """
        Draw a sprite.

        Handles texture upload, position, scale, rotation, and visibility.

        Args:
            sprite: The Sprite to draw.
        """
        # Skip if no GPU device
        if not self._gpu_device:
            return

        # Skip if sprite is not visible
        if not sprite.visible:
            return

        # Eksik texture → magenta placeholder (sessiz hata yok)
        if sprite.texture is None:
            RenderLogger.warn(f"Sprite has no texture, using placeholder: {sprite!r}")
            placeholder = self._get_placeholder_texture()
            if not placeholder.is_uploaded:
                return
            texture = placeholder
        else:
            texture = sprite.texture

        # Upload texture to GPU if needed
        self._ensure_uploaded(texture)

        # Calculate draw parameters
        x = sprite.position.x
        y = sprite.position.y
        width = sprite.width
        height = sprite.height

        # Convert color from 0-255 to 0.0-1.0
        r, g, b, a = sprite.color
        gpu_color = (r / 255.0, g / 255.0, b / 255.0, a / 255.0)

        # Get camera matrices if available
        view_matrix = None
        projection_matrix = None
        if self._camera:
            view_matrix = self._camera.view_matrix
            projection_matrix = self._camera.projection_matrix

        # Normal map check
        normal_map = getattr(sprite, 'normal_map', None)
        if normal_map is not None:
            self._ensure_uploaded(normal_map)
            
            # Collect lights from LightRenderer (max 8)
            lights_data = []
            ambient = (0.1, 0.1, 0.1)
            if self._light_renderer:
                ambient = (self._light_renderer.ambient_color.r * self._light_renderer.ambient_intensity,
                           self._light_renderer.ambient_color.g * self._light_renderer.ambient_intensity,
                           self._light_renderer.ambient_color.b * self._light_renderer.ambient_intensity)
                
                for light in self._light_renderer.get_visible_point_lights(max_count=8):
                    lights_data.append({
                        "position": (light.position.x, light.position.y),
                        "color": (light.color.r, light.color.g, light.color.b),
                        "intensity": light.intensity,
                        "radius": light.radius,
                        "falloff": light.falloff
                    })
            
            self._gpu_device.draw_with_normal_map(
                texture.gpu_id,
                normal_map.gpu_id,
                x,
                y,
                width,
                height,
                rotation=sprite.rotation,
                color=gpu_color,
                flip_x=sprite.flip_x,
                flip_y=sprite.flip_y,
                anchor_x=sprite.anchor_x,
                anchor_y=sprite.anchor_y,
                view_matrix=view_matrix,
                projection_matrix=projection_matrix,
                lights=lights_data,
                ambient=ambient
            )
        else:
            # Standard draw
            self._gpu_device.draw(
                texture.gpu_id,
                x,
                y,
                width,
                height,
                rotation=sprite.rotation,
                color=gpu_color,
                flip_x=sprite.flip_x,
                flip_y=sprite.flip_y,
                anchor_x=sprite.anchor_x,
                anchor_y=sprite.anchor_y,
                view_matrix=view_matrix,
                projection_matrix=projection_matrix,
            )

        self._track_texture(texture)

    def draw_texture(
        self,
        texture: "Texture",
        x: float,
        y: float,
        width: Optional[float] = None,
        height: Optional[float] = None
    ) -> None:
        """
        Draw a texture at the specified position.

        Args:
            texture: The Texture to draw.
            x: X position in screen coordinates.
            y: Y position in screen coordinates.
            width: Optional width (defaults to texture width).
            height: Optional height (defaults to texture height).
        """
        # Skip if no GPU device
        if not self._gpu_device:
            return

        # Upload texture to GPU if needed
        self._ensure_uploaded(texture)

        if width is None:
            width = float(texture.width)
        if height is None:
            height = float(texture.height)

        # Get camera matrices if available
        view_matrix = None
        projection_matrix = None
        if self._camera:
            view_matrix = self._camera.view_matrix
            projection_matrix = self._camera.projection_matrix

        self._gpu_device.draw(
            texture.gpu_id,
            x,
            y,
            width,
            height,
            view_matrix=view_matrix,
            projection_matrix=projection_matrix,
        )
        self._track_texture(texture)
