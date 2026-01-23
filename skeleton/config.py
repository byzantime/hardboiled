"""Site configuration."""

import os

from hardboiled import Config as BaseConfig


class Config(BaseConfig):
    """Site-specific configuration."""

    SITE_NAME = os.environ.get("SITE_NAME", "My Site")
    SITE_URL = os.environ.get("SITE_URL", "https://example.com")
    SITE_DESCRIPTION = os.environ.get(
        "SITE_DESCRIPTION", "A static site built with hardboiled"
    )
