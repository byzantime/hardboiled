"""Configuration base class for static sites."""

import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    """Base configuration class with environment loading support."""

    @classmethod
    def load_env(cls, env_path: str | Path | None = None) -> bool:
        """Load environment variables from a .env file.

        Args:
            env_path: Path to .env file. Defaults to .env in cwd.

        Returns:
            True if a .env file was found and loaded, False otherwise.
        """
        if env_path is None:
            env_path = Path.cwd() / ".env"
        return load_dotenv(env_path)

    @classmethod
    def get(cls, key: str, default: str | None = None) -> str | None:
        """Get an environment variable with optional default.

        Args:
            key: Environment variable name.
            default: Default value if not found.

        Returns:
            The environment variable value or default.
        """
        return os.environ.get(key, default)

    @classmethod
    def require(cls, key: str) -> str:
        """Get a required environment variable.

        Args:
            key: Environment variable name.

        Raises:
            KeyError: If the environment variable is not set.

        Returns:
            The environment variable value.
        """
        value = os.environ.get(key)
        if value is None:
            raise KeyError(f"Required environment variable '{key}' is not set")
        return value

    def to_dict(self) -> dict:
        """Convert config class attributes to a dictionary for template context.

        Returns uppercase class attributes (excluding private/dunder attrs).

        Returns:
            Dictionary of configuration values.
        """
        return {
            key: getattr(self, key)
            for key in dir(self)
            if key.isupper() and not key.startswith("_")
        }
