"""Tests for SiteBuilder class."""

import tempfile
from pathlib import Path

import pytest

from hardboiled import SiteBuilder


@pytest.fixture
def temp_project():
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Create template directory with a test template
        template_dir = base / "src" / "templates"
        template_dir.mkdir(parents=True)
        (template_dir / "index.html").write_text("<h1>{{ title }}</h1>")
        (template_dir / "about.html").write_text("<h1>About {{ name }}</h1>")

        # Create static directory with test files
        static_dir = base / "src" / "static"
        static_dir.mkdir(parents=True)
        (static_dir / "style.css").write_text("body { color: black; }")

        css_dir = static_dir / "css"
        css_dir.mkdir()
        (css_dir / "main.css").write_text(".main { display: block; }")

        yield base


class TestSiteBuilder:
    """Tests for SiteBuilder."""

    def test_init_default_paths(self, temp_project):
        """Test SiteBuilder initializes with default paths."""
        builder = SiteBuilder(base_path=temp_project)

        assert builder.template_dir == temp_project / "src" / "templates"
        assert builder.static_dir == temp_project / "src" / "static"
        assert builder.build_dir == temp_project / "build"

    def test_init_custom_paths(self, temp_project):
        """Test SiteBuilder initializes with custom paths."""
        builder = SiteBuilder(
            template_dir="templates",
            static_dir="assets",
            build_dir="dist",
            base_path=temp_project,
        )

        assert builder.template_dir == temp_project / "templates"
        assert builder.static_dir == temp_project / "assets"
        assert builder.build_dir == temp_project / "dist"

    def test_ensure_build_dirs(self, temp_project):
        """Test ensure_build_dirs creates the build directory."""
        builder = SiteBuilder(base_path=temp_project)
        builder.ensure_build_dirs()

        assert builder.build_dir.exists()
        assert builder.build_dir.is_dir()

    def test_ensure_build_dirs_with_subdirs(self, temp_project):
        """Test ensure_build_dirs creates subdirectories."""
        builder = SiteBuilder(base_path=temp_project)
        builder.ensure_build_dirs(subdirs=["css", "js", "images"])

        assert (builder.build_dir / "css").exists()
        assert (builder.build_dir / "js").exists()
        assert (builder.build_dir / "images").exists()

    def test_copy_static_assets(self, temp_project):
        """Test copy_static_assets copies files to build directory."""
        builder = SiteBuilder(base_path=temp_project)
        builder.ensure_build_dirs()
        builder.copy_static_assets()

        assert (builder.build_dir / "style.css").exists()
        assert (builder.build_dir / "css" / "main.css").exists()

    def test_copy_static_assets_with_exclude(self, temp_project):
        """Test copy_static_assets excludes specified patterns."""
        builder = SiteBuilder(base_path=temp_project)
        builder.ensure_build_dirs()
        builder.copy_static_assets(exclude_patterns=["*.css"])

        assert not (builder.build_dir / "style.css").exists()
        assert (builder.build_dir / "css" / "main.css").exists()

    def test_render_template(self, temp_project):
        """Test render_template renders and writes a template."""
        builder = SiteBuilder(base_path=temp_project)
        builder.ensure_build_dirs()

        html = builder.render_template("index.html", {"title": "Hello World"})

        assert html == "<h1>Hello World</h1>"
        assert (builder.build_dir / "index.html").exists()
        assert (builder.build_dir / "index.html").read_text() == "<h1>Hello World</h1>"

    def test_render_template_custom_output(self, temp_project):
        """Test render_template with custom output filename."""
        builder = SiteBuilder(base_path=temp_project)
        builder.ensure_build_dirs()

        builder.render_template("index.html", {"title": "Test"}, "custom.html")

        assert (builder.build_dir / "custom.html").exists()
        assert not (builder.build_dir / "index.html").exists()

    def test_render_pages(self, temp_project):
        """Test render_pages renders multiple templates."""
        builder = SiteBuilder(base_path=temp_project)
        builder.ensure_build_dirs()

        builder.render_pages(
            ["index.html", "about.html"],
            {"title": "Test", "name": "Hardboiled"},
        )

        assert (builder.build_dir / "index.html").exists()
        assert (builder.build_dir / "about.html").exists()

    def test_render_pages_with_tuples(self, temp_project):
        """Test render_pages with (template, output) tuples."""
        builder = SiteBuilder(base_path=temp_project)
        builder.ensure_build_dirs()

        builder.render_pages(
            [("index.html", "home.html"), ("about.html", "info.html")],
            {"title": "Test", "name": "Hardboiled"},
        )

        assert (builder.build_dir / "home.html").exists()
        assert (builder.build_dir / "info.html").exists()

    def test_add_global(self, temp_project):
        """Test add_global adds a global to the Jinja environment."""
        builder = SiteBuilder(base_path=temp_project)
        builder.add_global("site_name", "Test Site")

        assert builder.env.globals["site_name"] == "Test Site"

    def test_add_filter(self, temp_project):
        """Test add_filter adds a filter to the Jinja environment."""
        builder = SiteBuilder(base_path=temp_project)
        builder.add_filter("upper", str.upper)

        assert "upper" in builder.env.filters

    def test_clean(self, temp_project):
        """Test clean removes the build directory."""
        builder = SiteBuilder(base_path=temp_project)
        builder.ensure_build_dirs()
        (builder.build_dir / "test.txt").write_text("test")

        builder.clean()

        assert not builder.build_dir.exists()

    def test_clean_nonexistent(self, temp_project):
        """Test clean does nothing if build directory doesn't exist."""
        builder = SiteBuilder(base_path=temp_project)
        builder.clean()  # Should not raise


class TestConfig:
    """Tests for Config class."""

    def test_load_env_missing_file(self, temp_project):
        """Test load_env returns False when .env doesn't exist."""
        from hardboiled import Config

        result = Config.load_env(temp_project / ".env")
        assert result is False

    def test_load_env_with_file(self, temp_project):
        """Test load_env loads environment variables from file."""
        from hardboiled import Config

        env_file = temp_project / ".env"
        env_file.write_text("TEST_VAR=hello\n")

        result = Config.load_env(env_file)
        import os

        assert result is True
        assert os.environ.get("TEST_VAR") == "hello"

    def test_get_with_default(self):
        """Test get returns default when variable not set."""
        from hardboiled import Config

        result = Config.get("NONEXISTENT_VAR", "default_value")
        assert result == "default_value"

    def test_require_missing(self):
        """Test require raises KeyError for missing variable."""
        from hardboiled import Config

        with pytest.raises(KeyError, match="Required environment variable"):
            Config.require("DEFINITELY_NOT_SET_VAR")

    def test_to_dict(self):
        """Test to_dict returns uppercase attributes."""
        from hardboiled import Config

        class TestConfig(Config):
            SITE_NAME = "Test"
            SITE_URL = "https://test.com"
            _private = "hidden"
            lowercase = "hidden"

        config = TestConfig()
        result = config.to_dict()

        assert "SITE_NAME" in result
        assert "SITE_URL" in result
        assert "_private" not in result
        assert "lowercase" not in result


class TestUtils:
    """Tests for utility functions."""

    def test_get_file_hash(self, temp_project):
        """Test get_file_hash returns consistent hash."""
        from hardboiled import get_file_hash

        test_file = temp_project / "test.txt"
        test_file.write_text("hello world")

        hash1 = get_file_hash(test_file)
        hash2 = get_file_hash(test_file)

        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hex length

    def test_get_file_hash_short(self, temp_project):
        """Test get_file_hash_short returns truncated hash."""
        from hardboiled import get_file_hash_short

        test_file = temp_project / "test.txt"
        test_file.write_text("hello world")

        short_hash = get_file_hash_short(test_file, length=8)

        assert len(short_hash) == 8

    def test_current_year(self):
        """Test current_year returns current year."""
        from datetime import datetime

        from hardboiled import current_year

        assert current_year() == datetime.now().year

    def test_format_date(self):
        """Test format_date formats datetime correctly."""
        from datetime import datetime

        from hardboiled import format_date

        dt = datetime(2024, 6, 15, 12, 30)
        assert format_date(dt) == "2024-06-15"
        assert format_date(dt, "%B %d, %Y") == "June 15, 2024"
