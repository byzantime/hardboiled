"""SiteBuilder class for static site generation."""

import shutil
from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader


class SiteBuilder:
    """Builds static sites from Jinja2 templates."""

    def __init__(
        self,
        template_dir: str = "src/templates",
        static_dir: str = "src/static",
        build_dir: str = "build",
        base_path: Path | None = None,
    ):
        """Initialize the site builder.

        Args:
            template_dir: Directory containing Jinja2 templates.
            static_dir: Directory containing static assets.
            build_dir: Output directory for built site.
            base_path: Base path for resolving directories. Defaults to cwd.
        """
        self.base_path = base_path or Path.cwd()
        self.template_dir = self.base_path / template_dir
        self.static_dir = self.base_path / static_dir
        self.build_dir = self.base_path / build_dir

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
        )

    def ensure_build_dirs(self, subdirs: list[str] | None = None) -> None:
        """Create build directory and any required subdirectories.

        Args:
            subdirs: Optional list of subdirectories to create within build_dir.
        """
        self.build_dir.mkdir(parents=True, exist_ok=True)

        if subdirs:
            for subdir in subdirs:
                (self.build_dir / subdir).mkdir(parents=True, exist_ok=True)

    def copy_static_assets(self, exclude_patterns: list[str] | None = None) -> None:
        """Copy static assets to build directory.

        Args:
            exclude_patterns: Optional list of glob patterns to exclude.
        """
        if not self.static_dir.exists():
            return

        exclude_patterns = exclude_patterns or []

        static_dest = self.build_dir / "static"
        static_dest.mkdir(parents=True, exist_ok=True)

        for item in self.static_dir.iterdir():
            dest = static_dest / item.name

            # Check if item matches any exclude pattern
            should_exclude = any(item.match(pattern) for pattern in exclude_patterns)
            if should_exclude:
                continue

            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    def render_template(
        self,
        template_name: str,
        context: dict | None = None,
        output_name: str | None = None,
    ) -> str:
        """Render a template and write to build directory.

        Args:
            template_name: Name of template file to render.
            context: Template context variables.
            output_name: Output filename. Defaults to template_name.

        Returns:
            The rendered HTML content.
        """
        context = context or {}
        output_name = output_name or template_name

        template = self.env.get_template(template_name)
        html = template.render(**context)

        output_path = self.build_dir / output_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)

        return html

    def render_pages(
        self,
        pages: list[str] | list[tuple[str, str]],
        context: dict | None = None,
    ) -> None:
        """Render multiple pages with the same context.

        Args:
            pages: List of template names, or list of (template, output) tuples.
            context: Template context variables shared by all pages.
        """
        context = context or {}

        for page in pages:
            if isinstance(page, tuple):
                template_name, output_name = page
            else:
                template_name = page
                output_name = page

            self.render_template(template_name, context, output_name)

    def add_global(self, name: str, value: object) -> None:
        """Add a global variable to the Jinja2 environment.

        Args:
            name: Variable name accessible in templates.
            value: The value (can be a function, object, or primitive).
        """
        self.env.globals[name] = value

    def add_filter(self, name: str, func: object) -> None:
        """Add a custom filter to the Jinja2 environment.

        Args:
            name: Filter name to use in templates.
            func: The filter function.
        """
        self.env.filters[name] = func

    def clean(self) -> None:
        """Remove the build directory and all its contents."""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
