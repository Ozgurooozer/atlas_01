"""Tests for post-process stack system."""
import pytest
from core.color import Color


class TestPostProcessPass:
    """Test suite for individual post-process passes."""

    def test_bloom_extract_creation(self):
        """BrightExtract pass should initialize."""
        from engine.renderer.postprocess_stack import BrightExtract
        
        be = BrightExtract(threshold=0.8)
        
        assert be.threshold == 0.8

    def test_bloom_extract_process(self):
        """BrightExtract should extract bright pixels."""
        from engine.renderer.postprocess_stack import BrightExtract
        
        be = BrightExtract(threshold=0.5)
        
        # Bright color
        bright = Color(0.8, 0.8, 0.8)
        result_bright = be.process(bright)
        assert result_bright.r > 0
        
        # Dark color
        dark = Color(0.2, 0.2, 0.2)
        result_dark = be.process(dark)
        assert result_dark.r == 0

    def test_gaussian_blur_creation(self):
        """GaussianBlur pass should initialize."""
        from engine.renderer.postprocess_stack import GaussianBlur
        
        blur = GaussianBlur(radius=3)
        
        assert blur.radius == 3

    def test_tone_mapping_creation(self):
        """ToneMapping pass should initialize."""
        from engine.renderer.postprocess_stack import ToneMapping
        
        tm = ToneMapping(exposure=1.0)
        
        assert tm.exposure == 1.0

    def test_vignette_creation(self):
        """Vignette pass should initialize."""
        from engine.renderer.postprocess_stack import Vignette
        
        vignette = Vignette(intensity=0.5)
        
        assert vignette.intensity == 0.5


class TestPostProcessStack:
    """Test suite for post-process stack."""

    def test_stack_creation(self):
        """PostProcessStack should initialize empty."""
        from engine.renderer.postprocess_stack import PostProcessStack
        
        stack = PostProcessStack()
        
        assert len(stack.passes) == 0

    def test_add_pass(self):
        """PostProcessStack should add passes."""
        from engine.renderer.postprocess_stack import PostProcessStack, BrightExtract
        
        stack = PostProcessStack()
        be = BrightExtract()
        
        stack.add_pass(be)
        
        assert len(stack.passes) == 1

    def test_render_order(self):
        """PostProcessStack should respect pass order."""
        from engine.renderer.postprocess_stack import PostProcessStack, BrightExtract, GaussianBlur
        
        stack = PostProcessStack()
        
        be = BrightExtract()
        blur = GaussianBlur()
        
        stack.add_pass(be)
        stack.add_pass(blur)
        
        assert stack.passes[0] == be
        assert stack.passes[1] == blur

    def test_apply_pass(self):
        """PostProcessStack should apply single pass."""
        from engine.renderer.postprocess_stack import PostProcessStack, ToneMapping
        
        stack = PostProcessStack()
        tm = ToneMapping(exposure=1.0)
        stack.add_pass(tm)
        
        input_color = Color(0.5, 0.5, 0.5)
        result = stack.apply_pass(input_color, 0)
        
        assert result is not None


class TestPostProcessRenderer:
    """Test suite for post-process renderer."""

    def test_renderer_creation(self):
        """PostProcessRenderer should initialize with buffers."""
        from engine.renderer.postprocess_stack import PostProcessRenderer
        
        renderer = PostProcessRenderer(width=800, height=600)
        
        assert renderer.width == 800
        assert renderer.height == 600

    def test_ping_pong_buffers(self):
        """PostProcessRenderer should have ping-pong buffers."""
        from engine.renderer.postprocess_stack import PostProcessRenderer
        
        renderer = PostProcessRenderer(width=400, height=300)
        
        assert renderer.buffer_a is not None
        assert renderer.buffer_b is not None

    def test_composite_all(self):
        """PostProcessRenderer should composite all passes."""
        from engine.renderer.postprocess_stack import PostProcessRenderer, PostProcessStack, ToneMapping
        
        renderer = PostProcessRenderer(width=200, height=200)
        stack = PostProcessStack()
        stack.add_pass(ToneMapping())
        
        result = renderer.composite_all(stack)
        
        assert result is not None
