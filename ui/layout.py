"""UI Layout System - Widget positioning.

Provides layout managers for organizing UI elements.

Layer: 6 (UI)
Dependencies: ui.panel, ui.label, ui.button
"""
from typing import List, Any
from abc import ABC, abstractmethod


class Layout(ABC):
    """Abstract base class for layouts.
    
    Layouts arrange child widgets within a container.
    """
    
    def __init__(self, spacing: float = 0, padding: float = 0):
        """Initialize layout.
        
        Args:
            spacing: Space between widgets
            padding: Space around container edges
        """
        self.spacing = spacing
        self.padding = padding
    
    def set_spacing(self, spacing: float) -> None:
        """Set spacing between widgets.
        
        Args:
            spacing: New spacing value
        """
        self.spacing = spacing
    
    def set_padding(self, padding: float) -> None:
        """Set padding around container.
        
        Args:
            padding: New padding value
        """
        self.padding = padding
    
    @abstractmethod
    def arrange(self, container: Any) -> None:
        """Arrange children in container.
        
        Args:
            container: Container widget with children
        """
        raise NotImplementedError("Subclasses must implement arrange()")


class HorizontalLayout(Layout):
    """Horizontal row layout.
    
    Arranges children left to right in a row.
    """
    
    def arrange(self, container: Any) -> None:
        """Arrange children horizontally.
        
        Args:
            container: Container widget
        """
        if not hasattr(container, 'children'):
            return
        
        x = self.padding
        y = self.padding
        
        for child in container.children:
            if hasattr(child, 'x') and hasattr(child, 'y'):
                child.x = x
                child.y = y
                
                # Advance x by child width + spacing
                child_width = getattr(child, 'width', 0)
                x += child_width + self.spacing


class VerticalLayout(Layout):
    """Vertical column layout.
    
    Arranges children top to bottom in a column.
    """
    
    def arrange(self, container: Any) -> None:
        """Arrange children vertically.
        
        Args:
            container: Container widget
        """
        if not hasattr(container, 'children'):
            return
        
        x = self.padding
        y = self.padding
        
        for child in container.children:
            if hasattr(child, 'x') and hasattr(child, 'y'):
                child.x = x
                child.y = y
                
                # Advance y by child height + spacing
                child_height = getattr(child, 'height', 0)
                y += child_height + self.spacing


class GridLayout(Layout):
    """Grid layout.
    
    Arranges children in a grid with rows and columns.
    """
    
    def __init__(self, columns: int = 2, rows: int = 2,
                 spacing: float = 0, padding: float = 0,
                 cell_width: float = 0, cell_height: float = 0):
        """Initialize grid layout.
        
        Args:
            columns: Number of columns
            rows: Number of rows
            spacing: Space between cells
            padding: Space around grid
            cell_width: Fixed cell width (0 = auto)
            cell_height: Fixed cell height (0 = auto)
        """
        super().__init__(spacing, padding)
        self.columns = columns
        self.rows = rows
        self.cell_width = cell_width
        self.cell_height = cell_height
    
    def arrange(self, container: Any) -> None:
        """Arrange children in grid.
        
        Args:
            container: Container widget
        """
        if not hasattr(container, 'children'):
            return
        
        children = container.children
        container_width = getattr(container, 'width', 100)
        container_height = getattr(container, 'height', 100)
        
        # Calculate cell size if not fixed
        cell_w = self.cell_width
        cell_h = self.cell_height
        
        if cell_w == 0 and self.columns > 0:
            available_width = container_width - (2 * self.padding) - ((self.columns - 1) * self.spacing)
            cell_w = available_width / self.columns
        
        if cell_h == 0 and self.rows > 0:
            available_height = container_height - (2 * self.padding) - ((self.rows - 1) * self.spacing)
            cell_h = available_height / self.rows
        
        # Position children
        for i, child in enumerate(children):
            if not (hasattr(child, 'x') and hasattr(child, 'y')):
                continue
            
            col = i % self.columns
            row = i // self.columns
            
            x = self.padding + (col * (cell_w + self.spacing))
            y = self.padding + (row * (cell_h + self.spacing))
            
            child.x = x
            child.y = y
            
            # Optionally set size
            if hasattr(child, 'width') and cell_w > 0:
                child.width = cell_w
            if hasattr(child, 'height') and cell_h > 0:
                child.height = cell_h
