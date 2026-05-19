# Zorix Browser

A functional, lightweight web browser built with Python using PyQt5.

## Features

- Full HTTP(S) support
- HTML/CSS rendering
- JavaScript execution (basic)
- Back/Forward navigation
- URL history
- Tabbed browsing
- Bookmarks support
- Clean, intuitive UI

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python zorix_browser.py
```

## System Requirements

- Python 3.8+
- PyQt5
- requests library
- beautifulsoup4

## Architecture

- `zorix_browser.py` - Main application entry point
- `browser_engine.py` - Core browser logic and rendering
- `ui/` - User interface components
- `utils/` - Helper utilities
