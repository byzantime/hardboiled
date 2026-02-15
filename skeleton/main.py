#!/usr/bin/env python3
"""Build script for the static site."""

from hardboiled import SiteBuilder
from hardboiled import current_year

from config import Config


def build_site():
    """Build the static site."""
    Config.load_env()

    builder = SiteBuilder()
    builder.ensure_build_dirs(subdirs=["static/css"])
    builder.copy_static_assets()

    # Add global template variables
    builder.add_global("current_year", current_year())

    # Build context from config
    context = Config().to_dict()

    # Render pages
    pages = [
        "index.html",
    ]
    builder.render_pages(pages, context)

    print("Site built successfully!")


if __name__ == "__main__":
    build_site()
