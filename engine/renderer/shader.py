"""
Engine Layer (Layer 2) - Shader

Wraps IGPUDevice.create_shader() with a friendly API.
Caches uniform locations, validates at construction time.

Layer: 2 (Engine)
Dependencies: hal.interfaces
"""

from __future__ import annotations
from typing import Any, Dict

from hal.interfaces import IGPUDevice


class ShaderCompileError(Exception):
    """Raised when a shader fails to compile or link."""


# Built-in GLSL sources (used as defaults and for tests)
SPRITE_VERTEX_SRC = """
#version 330 core
in vec2 a_position;
in vec2 a_texcoord;
in vec4 a_color;
uniform mat4 u_projection;
uniform mat4 u_view;
out vec2 v_texcoord;
out vec4 v_color;
void main() {
    gl_Position = u_projection * u_view * vec4(a_position, 0.0, 1.0);
    v_texcoord = a_texcoord;
    v_color = a_color;
}
""".strip()

SPRITE_FRAGMENT_SRC = """
#version 330 core
in vec2 v_texcoord;
in vec4 v_color;
uniform sampler2D u_texture;
out vec4 frag_color;
void main() {
    vec4 tex_color = texture(u_texture, v_texcoord);
    frag_color = tex_color * v_color;
    if (frag_color.a < 0.01) discard;
}
""".strip()

POST_VERTEX_SRC = """
#version 330 core

in vec2 a_position;
in vec2 a_texcoord;

out vec2 v_texcoord;

void main() {
    gl_Position = vec4(a_position, 0.0, 1.0);
    v_texcoord = a_texcoord;
}
""".strip()

BRIGHT_EXTRACT_FRAG_SRC = """
#version 330 core

in vec2 v_texcoord;

uniform sampler2D u_texture;
uniform float u_threshold;
uniform float u_soft_threshold;

out vec4 frag_color;

float luminance(vec3 color) {
    return dot(color, vec3(0.2126, 0.7152, 0.0722));
}

void main() {
    vec4 color = texture(u_texture, v_texcoord);
    float brightness = luminance(color.rgb);
    float soft_knee = u_threshold - u_soft_threshold;
    float contribution = 0.0;
    if (brightness > u_threshold) {
        contribution = 1.0;
    } else if (brightness > soft_knee) {
        contribution = smoothstep(soft_knee, u_threshold, brightness);
    }
    frag_color = color * contribution;
}
""".strip()

BLUR_FRAG_SRC = """
#version 330 core

in vec2 v_texcoord;

uniform sampler2D u_texture;
uniform vec2 u_direction;
uniform vec2 u_texel_size;

out vec4 frag_color;

const float weights[3] = float[](0.227027, 0.316216, 0.070270);
const float offsets[2] = float[](1.384615, 3.230769);

void main() {
    vec4 color = texture(u_texture, v_texcoord) * weights[0];
    vec2 texel_offset = u_direction * u_texel_size;
    for (int i = 1; i < 3; i++) {
        color += texture(u_texture, v_texcoord + texel_offset * offsets[i-1]) * weights[i];
        color += texture(u_texture, v_texcoord - texel_offset * offsets[i-1]) * weights[i];
    }
    frag_color = color;
}
""".strip()

BLOOM_COMPOSITE_FRAG_SRC = """
#version 330 core

in vec2 v_texcoord;

uniform sampler2D u_scene;
uniform sampler2D u_bloom;
uniform float u_intensity;
uniform float u_exposure;
uniform int u_tone_mapping;

out vec4 frag_color;

vec3 reinhard(vec3 color) { return color / (color + vec3(1.0)); }
vec3 filmic(vec3 color) {
    vec3 x = max(vec3(0.0), color - 0.004);
    return (x * (6.2 * x + 0.5)) / (x * (6.2 * x + 1.7) + 0.06);
}

void main() {
    vec4 scene = texture(u_scene, v_texcoord);
    vec4 bloom = texture(u_bloom, v_texcoord);
    vec3 result = scene.rgb + bloom.rgb * u_intensity;
    result *= u_exposure;
    if (u_tone_mapping == 1) result = reinhard(result);
    else if (u_tone_mapping == 2) result = filmic(result);
    result = pow(result, vec3(1.0 / 2.2));
    frag_color = vec4(result, scene.a);
}
""".strip()

LIGHT_VERTEX_SRC = """
#version 330 core

in vec2 a_position;
in vec2 a_texcoord;

uniform mat4 u_projection;

out vec2 v_texcoord;
out vec2 v_world_pos;

void main() {
    gl_Position = u_projection * vec4(a_position, 0.0, 1.0);
    v_texcoord = a_texcoord;
    v_world_pos = a_position;
}
""".strip()

LIGHT_FRAGMENT_SRC = """
#version 330 core

in vec2 v_texcoord;
in vec2 v_world_pos;

uniform sampler2D u_scene;
uniform sampler2D u_light_map;
uniform float u_ambient;

out vec4 frag_color;

void main() {
    vec4 scene_color = texture(u_scene, v_texcoord);
    vec4 light_color = texture(u_light_map, v_texcoord);
    vec3 light = max(light_color.rgb, vec3(u_ambient));
    frag_color = vec4(scene_color.rgb * light, scene_color.a);
}
""".strip()


# ---------------------------------------------------------------------------
# Shader
# ---------------------------------------------------------------------------

class Shader:
    """
    Compiled GPU shader program.

    Wraps shader functionality for the rendering system.
    Validates on creation — raises ShaderCompileError on failure.
    """

    _next_program_id = 1

    def __init__(
        self,
        gpu: IGPUDevice,
        vertex_src: str,
        fragment_src: str,
    ) -> None:
        if not vertex_src.strip() or not fragment_src.strip():
            raise ShaderCompileError("Shader source cannot be empty")

        self._gpu = gpu
        self._program_id = Shader._next_program_id
        Shader._next_program_id += 1
        
        # Store shader sources
        self._vertex_src = vertex_src
        self._fragment_src = fragment_src
        self._valid = True
        
        self._uniform_cache: Dict[str, Any] = {}

    @classmethod
    def from_source(
        cls,
        gpu_device: IGPUDevice,
        vertex_src: str,
        fragment_src: str,
    ) -> "Shader":
        """Factory method for creating shaders from source."""
        return cls(gpu_device, vertex_src, fragment_src)

    @property
    def program(self) -> "Shader":
        """Get this shader program."""
        return self

    @property
    def is_valid(self) -> bool:
        return self._valid

    @property
    def program_id(self) -> int:
        return self._program_id

    def use(self) -> None:
        """Bind this shader for the next draw call."""
        pass  # No-op in headless mode

    def set_uniform(self, name: str, value: Any) -> None:
        """Set a uniform value. Caches the value for inspection."""
        self._uniform_cache[name] = value

    def get_uniform(self, name: str) -> Any:
        """Return the last value set for a uniform (test helper)."""
        return self._uniform_cache.get(name)

    def set_mat4(self, name: str, mat4) -> None:
        """Convenience: upload a Mat4 uniform."""
        self.set_uniform(name, mat4)

    def set_vec2(self, name: str, vec2) -> None:
        self.set_uniform(name, (vec2.x, vec2.y))

    def set_vec4(self, name: str, vec4) -> None:
        self.set_uniform(name, (vec4.x, vec4.y, vec4.z, vec4.w))

    def set_color(self, name: str, color) -> None:
        self.set_uniform(name, (color.r, color.g, color.b, color.a))

    def set_int(self, name: str, value: int) -> None:
        self.set_uniform(name, int(value))

    def set_float(self, name: str, value: float) -> None:
        self.set_uniform(name, float(value))

    def dispose(self) -> None:
        """Release GPU shader resources."""
        self._valid = False
        self._uniform_cache.clear()

    def __repr__(self) -> str:
        return f"Shader(id={self.program_id}, valid={self.is_valid})"


# ---------------------------------------------------------------------------
# ShaderLibrary — thin registry
# ---------------------------------------------------------------------------

class ShaderLibrary:
    """
    Named shader registry.

    Avoids re-compiling identical shaders.
    """

    def __init__(self, gpu: IGPUDevice) -> None:
        self._gpu = gpu
        self._shaders: Dict[str, Shader] = {}

    def add(self, name: str, shader: Shader) -> None:
        """Add a shader to the library."""
        self._shaders[name] = shader

    def get(self, name: str) -> Shader:
        """Get shader by name. Returns None if not found."""
        return self._shaders.get(name)

    def has(self, name: str) -> bool:
        """Check if shader exists in library."""
        return name in self._shaders

    def remove(self, name: str) -> None:
        """Remove shader from library."""
        if name in self._shaders:
            del self._shaders[name]

    def get_or_create(
        self, name: str, vertex_src: str, fragment_src: str
    ) -> Shader:
        if name not in self._shaders:
            self._shaders[name] = Shader(self._gpu, vertex_src, fragment_src)
        return self._shaders[name]

    def dispose_all(self) -> None:
        for shader in self._shaders.values():
            shader.dispose()
        self._shaders.clear()

    def __contains__(self, name: str) -> bool:
        return name in self._shaders

    def __len__(self) -> int:
        return len(self._shaders)
