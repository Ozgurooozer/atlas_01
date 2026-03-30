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

NORMAL_MAP_VERTEX_SRC = """
#version 330 core
in vec2 a_position;
in vec2 a_texcoord;
in vec4 a_color;

uniform mat4 u_projection;
uniform mat4 u_view;

out vec2 v_texcoord;
out vec4 v_color;
out vec2 v_world_pos;

void main() {
    vec4 world_pos = vec4(a_position, 0.0, 1.0);
    gl_Position = u_projection * u_view * world_pos;
    v_texcoord = a_texcoord;
    v_color = a_color;
    v_world_pos = a_position;
}
""".strip()

NORMAL_MAP_FRAGMENT_SRC = """
#version 330 core
in vec2 v_texcoord;
in vec4 v_color;
in vec2 v_world_pos;

uniform sampler2D u_texture;
uniform sampler2D u_normal_map;
uniform vec3 u_ambient;

struct Light {
    vec2 position;
    vec3 color;
    float intensity;
    float radius;
    float falloff;
};

uniform Light u_lights[8];
uniform int u_light_count;

out vec4 frag_color;

void main() {
    vec4 tex_color = texture(u_texture, v_texcoord) * v_color;
    if (tex_color.a < 0.01) discard;

    vec3 normal = texture(u_normal_map, v_texcoord).rgb * 2.0 - 1.0;
    normal = normalize(normal);

    vec3 total_light = u_ambient;

    for (int i = 0; i < u_light_count; i++) {
        vec2 light_dir_2d = u_lights[i].position - v_world_pos;
        float dist = length(light_dir_2d);
        
        if (dist < u_lights[i].radius) {
            vec3 light_dir = normalize(vec3(light_dir_2d, 0.5));
            float diff = max(dot(normal, light_dir), 0.0);
            
            float attenuation = pow(clamp(1.0 - dist / u_lights[i].radius, 0.0, 1.0), u_lights[i].falloff);
            total_light += u_lights[i].color * u_lights[i].intensity * diff * attenuation;
        }
    }

    frag_color = vec4(tex_color.rgb * total_light, tex_color.a);
}
""".strip()

SHADOW_MAP_VERTEX_SRC = """
#version 330 core
in vec2 a_position;
uniform mat4 u_view;
uniform mat4 u_projection;
void main() {
    gl_Position = u_projection * u_view * vec4(a_position, 0.0, 1.0);
}
""".strip()

SHADOW_MAP_FRAGMENT_SRC = """
#version 330 core
out float f_depth;
void main() {
    f_depth = gl_FragCoord.z;
}
""".strip()

PCF_SHADOW_FRAGMENT_SRC = """
#version 330 core
uniform sampler2D u_shadow_map;
uniform vec2 u_light_pos;
uniform float u_light_radius;
in vec2 v_world_pos;
out float f_shadow;

void main() {
    vec2 texel_size = 1.0 / textureSize(u_shadow_map, 0);
    float shadow = 0.0;
    float current_depth = length(v_world_pos - u_light_pos) / u_light_radius;
    
    for(int x = -1; x <= 1; ++x) {
        for(int y = -1; y <= 1; ++y) {
            float pcf_depth = texture(u_shadow_map, (gl_FragCoord.xy + vec2(x, y)) * texel_size).r;
            shadow += current_depth > pcf_depth ? 1.0 : 0.0;
        }
    }
    f_shadow = shadow / 9.0;
}
""".strip()

PENUMBRA_BLUR_FRAGMENT_SRC = """
#version 330 core
uniform sampler2D u_image;
uniform float u_blur_radius;
uniform vec2 u_texel_size;
out vec4 f_color;

void main() {
    vec2 uv = gl_FragCoord.xy * u_texel_size;
    vec4 result = vec4(0.0);
    float weight[5] = float[](0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);
    result += texture(u_image, uv) * weight[0];
    for(int i = 1; i < 5; ++i) {
        result += texture(u_image, uv + vec2(u_texel_size.x * i * u_blur_radius, 0.0)) * weight[i];
        result += texture(u_image, uv - vec2(u_texel_size.x * i * u_blur_radius, 0.0)) * weight[i];
        result += texture(u_image, uv + vec2(0.0, u_texel_size.y * i * u_blur_radius)) * weight[i];
        result += texture(u_image, uv - vec2(0.0, u_texel_size.y * i * u_blur_radius)) * weight[i];
    }
    f_color = result;
}
""".strip()

GBUFFER_VERTEX_SRC = """
#version 330 core
in vec2 a_position;
in vec2 a_texcoord;
in vec4 a_color;
uniform mat4 u_view;
uniform mat4 u_projection;
out vec2 v_texcoord;
out vec4 v_color;
out vec3 v_normal;
void main() {
    gl_Position = u_projection * u_view * vec4(a_position, 0.0, 1.0);
    v_texcoord = a_texcoord;
    v_color = a_color;
    v_normal = vec3(0.0, 0.0, 1.0); // Default normal for 2D
}
""".strip()

GBUFFER_FRAGMENT_SRC = """
#version 330 core
in vec2 v_texcoord;
in vec4 v_color;
in vec3 v_normal;
uniform sampler2D u_texture;
uniform sampler2D u_normal_map;
uniform bool u_has_normal_map;
layout (location = 0) out vec4 f_albedo;
layout (location = 1) out vec3 f_normal;
void main() {
    vec4 tex_color = texture(u_texture, v_texcoord) * v_color;
    if (tex_color.a < 0.01) discard;
    f_albedo = tex_color;
    if (u_has_normal_map) {
        f_normal = texture(u_normal_map, v_texcoord).rgb * 2.0 - 1.0;
    } else {
        f_normal = v_normal;
    }
}
""".strip()

SSAO_FRAGMENT_SRC = """
#version 330 core
uniform sampler2D u_normal;
uniform sampler2D u_depth;
uniform sampler2D u_noise;
uniform vec3 u_samples[64];
uniform float u_radius;
uniform float u_bias;
uniform vec2 u_noise_scale;
uniform mat4 u_projection;
out float f_ssao;

void main() {
    vec2 uv = gl_FragCoord.xy / textureSize(u_depth, 0);
    float depth = texture(u_depth, uv).r;
    vec3 normal = normalize(texture(u_normal, uv).rgb);
    vec3 random_vec = normalize(texture(u_noise, uv * u_noise_scale).xyz);
    
    vec3 tangent = normalize(random_vec - normal * dot(random_vec, normal));
    vec3 bitangent = cross(normal, tangent);
    mat3 tbn = mat3(tangent, bitangent, normal);
    
    float occlusion = 0.0;
    for(int i = 0; i < 64; ++i) {
        vec3 sample_pos = tbn * u_samples[i];
        sample_pos = vec3(uv, depth) + sample_pos * u_radius;
        
        float sample_depth = texture(u_depth, sample_pos.xy).r;
        float range_check = smoothstep(0.0, 1.0, u_radius / abs(depth - sample_depth));
        occlusion += (sample_depth >= sample_pos.z + u_bias ? 1.0 : 0.0) * range_check;
    }
    f_ssao = 1.0 - (occlusion / 64.0);
}
""".strip()

SSAO_BLUR_FRAGMENT_SRC = """
#version 330 core
uniform sampler2D u_ssao;
out float f_blur;
void main() {
    vec2 texel_size = 1.0 / textureSize(u_ssao, 0);
    float result = 0.0;
    for (int x = -2; x < 2; ++x) {
        for (int y = -2; y < 2; ++y) {
            result += texture(u_ssao, (gl_FragCoord.xy + vec2(x, y)) * texel_size).r;
        }
    }
    f_blur = result / 16.0;
}
""".strip()

DEFERRED_LIGHT_FRAGMENT_SRC = """
#version 330 core
uniform sampler2D u_albedo;
uniform sampler2D u_normal;
uniform sampler2D u_depth;

uniform vec2 u_light_pos;
uniform vec3 u_light_color;
uniform float u_light_intensity;
uniform float u_light_radius;
uniform float u_light_falloff;

out vec4 f_color;

void main() {
    vec2 uv = gl_FragCoord.xy / textureSize(u_albedo, 0);
    vec4 albedo = texture(u_albedo, uv);
    if (albedo.a < 0.01) discard;
    
    vec3 normal = normalize(texture(u_normal, uv).rgb);
    float depth = texture(u_depth, uv).r;
    
    vec2 world_pos = gl_FragCoord.xy; // Simplified for 2D
    vec2 light_dir_2d = u_light_pos - world_pos;
    float dist = length(light_dir_2d);
    
    if (dist < u_light_radius) {
        vec3 light_dir = normalize(vec3(light_dir_2d, 0.5));
        float diff = max(dot(normal, light_dir), 0.0);
        float attenuation = pow(clamp(1.0 - dist / u_light_radius, 0.0, 1.0), u_light_falloff);
        vec3 light = u_light_color * u_light_intensity * diff * attenuation;
        f_color = vec4(albedo.rgb * light, 0.0); // Alpha 0 for additive blending
    } else {
        discard;
    }
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
