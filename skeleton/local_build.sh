#!/bin/bash
set -e

# Install Python dependencies
uv sync

# Install Node dependencies
npm install

# Build the site
uv run python main.py

# Build CSS
npm run css

echo "Build complete! Open build/index.html to view the site."
