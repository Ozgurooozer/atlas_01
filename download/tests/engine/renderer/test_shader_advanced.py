"""
Shader system tests.

Tests for shader wrapper with uniform caching.
Layer: 2 (Engine)
"""

from __future__ import annotations

import pytest


class TestShader:
    """Test Shader class."""

    def test_shader_creation(self):
        """Test basic shader creation."""
        from hal.headless import HeadlessGPU
        from engine.renderer.shader import Shader

        gpu = HeadlessGPU()
        
        shader = Shader.from_source(
            gpu_device=gpu,
            vertex_src="""
            #version 330 core
            in vec2 a_position;
            uniform mat4 u_projection;
            void main() {
                gl_Position = u_projection * vec4(a_position, 0.0, 1.0);
            }
            """,
            fragment_src="""
            #version 330 core
            out vec4 frag_color;
            void main() {
                frag_color = vec4(1.0, 0.0, 0.0, 1.0);
            }
            """
        )
        
        assert shader is not None
        assert shader.program is not None

    def test_uniform_setting(self):
        """Test setting uniforms."""
        from hal.headless import HeadlessGPU
        from engine.renderer.shader import Shader

        gpu = HeadlessGPU()
        
        shader = Shader.from_source(
            gpu_device=gpu,
            vertex_src="""
            #version 330 core
            in vec2 a_position;
            uniform mat4 u_projection;
            uniform float u_time;
            void main() {
                gl_Position = u_projection * vec4(a_position, 0.0, 1.0);
            }
            """,
            fragment_src="""
            #version 330 core
            uniform float u_time;
            uniform vec4 u_color;
            out vec4 frag_color;
            void main() {
                frag_color = u_color;
            }
            """
        )
        
        shader.use()
        shader.set_uniform("u_time", 1.0)
        shader.set_uniform("u_color", (1.0, 0.0, 0.0, 1.0))

    def test_invalid_uniform_ignored(self):
        """Test that invalid uniforms are silently ignored."""
        from hal.headless import HeadlessGPU
        from engine.renderer.shader import Shader

        gpu = HeadlessGPU()
        
        shader = Shader.from_source(
            gpu_device=gpu,
            vertex_src="""
            #version 330 core
            in vec2 a_position;
            void main() {
                gl_Position = vec4(a_position, 0.0, 1.0);
            }
            """,
            fragment_src="""
            #version 330 core
            out vec4 frag_color;
            void main() {
                frag_color = vec4(1.0);
            }
            """
        )
        
        shader.use()
        shader.set_uniform("nonexistent_uniform", 1.0)


class TestShaderLibrary:
    """Test ShaderLibrary class."""

    def test_add_and_get_shader(self):
        """Test adding and retrieving shaders."""
        from hal.headless import HeadlessGPU
        from engine.renderer.shader import Shader, ShaderLibrary

        gpu = HeadlessGPU()
        
        library = ShaderLibrary(gpu)
        
        shader = Shader.from_source(
            gpu_device=gpu,
            vertex_src="""
            #version 330 core
            in vec2 a_position;
            void main() {
                gl_Position = vec4(a_position, 0.0, 1.0);
            }
            """,
            fragment_src="""
            #version 330 core
            out vec4 frag_color;
            void main() {
                frag_color = vec4(1.0);
            }
            """
        )
        
        library.add("test_shader", shader)
        retrieved = library.get("test_shader")
        
        assert retrieved is shader

    def test_get_missing_shader(self):
        """Test getting non-existent shader returns None."""
        from hal.headless import HeadlessGPU
        from engine.renderer.shader import ShaderLibrary

        gpu = HeadlessGPU()
        library = ShaderLibrary(gpu)
        
        result = library.get("missing_shader")
        
        assert result is None

    def test_has_shader(self):
        """Test checking if shader exists."""
        from hal.headless import HeadlessGPU
        from engine.renderer.shader import Shader, ShaderLibrary

        gpu = HeadlessGPU()
        
        library = ShaderLibrary(gpu)
        
        shader = Shader.from_source(
            gpu_device=gpu,
            vertex_src="""
            #version 330 core
            in vec2 a_position;
            void main() {
                gl_Position = vec4(a_position, 0.0, 1.0);
            }
            """,
            fragment_src="""
            #version 330 core
            out vec4 frag_color;
            void main() {
                frag_color = vec4(1.0);
            }
            """
        )
        
        library.add("my_shader", shader)
        
        assert library.has("my_shader")
        assert not library.has("other_shader")

    def test_remove_shader(self):
        """Test removing shader from library."""
        from hal.headless import HeadlessGPU
        from engine.renderer.shader import Shader, ShaderLibrary

        gpu = HeadlessGPU()
        
        library = ShaderLibrary(gpu)
        
        shader = Shader.from_source(
            gpu_device=gpu,
            vertex_src="""
            #version 330 core
            in vec2 a_position;
            void main() {
                gl_Position = vec4(a_position, 0.0, 1.0);
            }
            """,
            fragment_src="""
            #version 330 core
            out vec4 frag_color;
            void main() {
                frag_color = vec4(1.0);
            }
            """
        )
        
        library.add("removable", shader)
        assert library.has("removable")
        
        library.remove("removable")
        assert not library.has("removable")
