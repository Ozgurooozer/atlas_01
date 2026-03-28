"""Tests for Asset Browser panel."""

import pytest
from editor.main import Editor, EditorPanel


class TestAssetBrowser:
    """Test suite for Asset Browser panel."""

    def test_asset_browser_is_panel(self):
        """AssetBrowser should inherit from EditorPanel."""
        from editor.asset_browser import AssetBrowser
        assert issubclass(AssetBrowser, EditorPanel)

    def test_asset_browser_creation(self):
        """AssetBrowser should be created with default settings."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert browser is not None
        assert browser.name == "Asset Browser"

    def test_asset_browser_has_render_method(self):
        """AssetBrowser should have render method."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'render')
        assert callable(browser.render)

    def test_asset_browser_with_editor(self):
        """AssetBrowser should accept editor reference."""
        from editor.asset_browser import AssetBrowser

        editor = Editor()
        browser = AssetBrowser(editor=editor)
        assert browser.editor is editor

    def test_asset_browser_has_root_path(self):
        """AssetBrowser should have root path."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'root_path')

    def test_asset_browser_set_root_path(self):
        """AssetBrowser should accept root path."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        browser.root_path = "/assets"
        assert browser.root_path == "/assets"

    def test_asset_browser_has_current_path(self):
        """AssetBrowser should track current path."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'current_path')

    def test_asset_browser_current_path_defaults_to_root(self):
        """AssetBrowser current path should default to root."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        browser.root_path = "/assets"
        assert browser.current_path == "/assets"

    def test_asset_browser_has_items(self):
        """AssetBrowser should have items list."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'items')

    def test_asset_browser_items_empty_by_default(self):
        """AssetBrowser items should be empty by default."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert browser.items == []

    def test_asset_browser_refresh(self):
        """AssetBrowser should have refresh method."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'refresh')
        assert callable(browser.refresh)


class TestAssetBrowserNavigation:
    """Test suite for Asset Browser navigation."""

    def test_asset_browser_navigate_to(self):
        """AssetBrowser should navigate to path."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        browser.root_path = "/assets"
        browser.navigate_to("/assets/textures")
        assert browser.current_path == "/assets/textures"

    def test_asset_browser_navigate_up(self):
        """AssetBrowser should navigate to parent."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        browser.root_path = "/assets"
        browser.navigate_to("/assets/textures")
        browser.navigate_up()
        assert browser.current_path == "/assets"

    def test_asset_browser_cant_navigate_above_root(self):
        """AssetBrowser should not navigate above root."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        browser.root_path = "/assets"
        browser.navigate_up()
        assert browser.current_path == "/assets"

    def test_asset_browser_navigate_home(self):
        """AssetBrowser should navigate to root."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        browser.root_path = "/assets"
        browser.navigate_to("/assets/textures/characters")
        browser.navigate_home()
        assert browser.current_path == "/assets"


class TestAssetBrowserSelection:
    """Test suite for Asset Browser selection."""

    def test_asset_browser_has_selected_item(self):
        """AssetBrowser should track selected item."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'selected_item')

    def test_asset_browser_selected_item_none_by_default(self):
        """AssetBrowser selected item should be None by default."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert browser.selected_item is None

    def test_asset_browser_select_item(self):
        """AssetBrowser should allow selecting item."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        item = {'name': 'test.png', 'type': 'file', 'path': '/assets/test.png'}
        browser.select_item(item)
        assert browser.selected_item == item

    def test_asset_browser_clear_selection(self):
        """AssetBrowser should allow clearing selection."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        item = {'name': 'test.png', 'type': 'file', 'path': '/assets/test.png'}
        browser.select_item(item)
        browser.clear_selection()
        assert browser.selected_item is None


class TestAssetBrowserFiltering:
    """Test suite for Asset Browser filtering."""

    def test_asset_browser_has_filter(self):
        """AssetBrowser should have filter text."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'filter_text')

    def test_asset_browser_filter_default_empty(self):
        """AssetBrowser filter should default to empty."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert browser.filter_text == ""

    def test_asset_browser_set_filter(self):
        """AssetBrowser should allow setting filter."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        browser.filter_text = ".png"
        assert browser.filter_text == ".png"

    def test_asset_browser_has_show_folders(self):
        """AssetBrowser should have show folders flag."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'show_folders')

    def test_asset_browser_show_folders_default_true(self):
        """AssetBrowser show folders should default to True."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert browser.show_folders is True


class TestAssetBrowserActions:
    """Test suite for Asset Browser actions."""

    def test_asset_browser_has_import_method(self):
        """AssetBrowser should have import method."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'import_asset')
        assert callable(browser.import_asset)

    def test_asset_browser_has_delete_method(self):
        """AssetBrowser should have delete method."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'delete_asset')
        assert callable(browser.delete_asset)

    def test_asset_browser_has_rename_method(self):
        """AssetBrowser should have rename method."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'rename_asset')
        assert callable(browser.rename_asset)

    def test_asset_browser_has_create_folder_method(self):
        """AssetBrowser should have create folder method."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'create_folder')
        assert callable(browser.create_folder)

    def test_asset_browser_has_duplicate_method(self):
        """AssetBrowser should have duplicate method."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        assert hasattr(browser, 'duplicate_asset')
        assert callable(browser.duplicate_asset)


class TestAssetBrowserItem:
    """Test suite for Asset Browser item structure."""

    def test_asset_browser_item_has_name(self):
        """AssetBrowser items should have name."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        browser._items = [{'name': 'test.png'}]
        assert browser.items[0]['name'] == 'test.png'

    def test_asset_browser_item_has_type(self):
        """AssetBrowser items should have type."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        browser._items = [{'name': 'test.png', 'type': 'file'}]
        assert browser.items[0]['type'] == 'file'

    def test_asset_browser_item_has_path(self):
        """AssetBrowser items should have path."""
        from editor.asset_browser import AssetBrowser

        browser = AssetBrowser()
        browser._items = [{'name': 'test.png', 'path': '/assets/test.png'}]
        assert browser.items[0]['path'] == '/assets/test.png'
