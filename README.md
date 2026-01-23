# hardboiled

Minimal Python static site generator library.

## Installation

```bash
pip install hardboiled
```

Or with uv:

```bash
uv add hardboiled
```

## Quick Start

```python
from hardboiled import SiteBuilder, Config, current_year

# Load environment variables
Config.load_env()

# Create builder with default directories
builder = SiteBuilder()

# Set up build directory
builder.ensure_build_dirs()

# Copy static assets
builder.copy_static_assets()

# Add global template variables
builder.add_global("current_year", current_year())

# Render templates
builder.render_pages(["index.html", "about.html"], {"title": "My Site"})
```

## API Reference

### SiteBuilder

The main class for building static sites from Jinja2 templates.

```python
builder = SiteBuilder(
    template_dir="src/templates",  # Jinja2 templates location
    static_dir="src/static",       # Static assets location
    build_dir="build",             # Output directory
    base_path=Path.cwd(),          # Base path for resolving directories
)
```

#### Methods

- `ensure_build_dirs(subdirs=None)` - Create build directory and optional subdirectories
- `copy_static_assets(exclude_patterns=None)` - Copy static files to build directory
- `render_template(template_name, context=None, output_name=None)` - Render a single template
- `render_pages(pages, context=None)` - Render multiple pages with shared context
- `add_global(name, value)` - Add a global variable to Jinja2 environment
- `add_filter(name, func)` - Add a custom Jinja2 filter
- `clean()` - Remove the build directory

### Config

Base configuration class with environment loading support.

```python
from hardboiled import Config

# Load .env file
Config.load_env()

# Get environment variable with default
value = Config.get("MY_VAR", "default")

# Get required environment variable (raises KeyError if missing)
value = Config.require("REQUIRED_VAR")

# Create site-specific config
class SiteConfig(Config):
    SITE_NAME = os.environ.get("SITE_NAME", "My Site")
    SITE_URL = os.environ.get("SITE_URL", "https://example.com")

# Convert to dict for template context
context = SiteConfig().to_dict()
```

### Utility Functions

```python
from hardboiled import get_file_hash, get_file_hash_short, format_date, current_year

# Get file hash for cache busting
hash = get_file_hash(Path("style.css"))  # Full MD5 hash
short = get_file_hash_short(Path("style.css"), length=8)  # First 8 chars

# Date utilities
year = current_year()  # Current year as int
formatted = format_date(datetime.now(), "%B %d, %Y")  # "January 23, 2026"
```

## Project Skeleton

The `skeleton/` directory contains a complete project template with:

- `main.py` - Build script using hardboiled
- `config.py` - Site configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `local_build.sh` - Local build script
- `netlify.toml` - Netlify deployment configuration
- `src/templates/` - Example Jinja2 templates
- `src/static/` - Static assets

To start a new project:

```bash
cp -r skeleton/ my-new-site/
cd my-new-site
mv pyproject.toml.template pyproject.toml
# Edit pyproject.toml to set your project name
uv sync
./local_build.sh
```

## Directory Structure

The default directory structure expected by hardboiled:

```
my-site/
├── src/
│   ├── templates/     # Jinja2 templates
│   │   ├── base.html
│   │   └── index.html
│   └── static/        # Static assets (CSS, JS, images)
│       └── css/
│           └── styles.css
├── build/             # Generated output
├── main.py            # Build script
├── config.py          # Site configuration
└── pyproject.toml
```

## License

MIT
