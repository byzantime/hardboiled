"""Utility functions for static site generation."""

import hashlib
from datetime import datetime
from pathlib import Path


def get_file_hash(file_path: Path, algorithm: str = "md5") -> str:
    """Get a hash of a file's contents for cache busting.

    Args:
        file_path: Path to the file.
        algorithm: Hash algorithm (md5, sha1, sha256).

    Returns:
        Hex digest of the file hash.
    """
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def get_file_hash_short(file_path: Path, length: int = 8) -> str:
    """Get a short hash for cache busting URLs.

    Args:
        file_path: Path to the file.
        length: Number of characters to return.

    Returns:
        Truncated hex digest.
    """
    return get_file_hash(file_path)[:length]


def format_date(dt: datetime, fmt: str = "%Y-%m-%d") -> str:
    """Format a datetime object as a string.

    Args:
        dt: Datetime object.
        fmt: strftime format string.

    Returns:
        Formatted date string.
    """
    return dt.strftime(fmt)


def current_year() -> int:
    """Get the current year.

    Returns:
        Current year as integer.
    """
    return datetime.now().year
