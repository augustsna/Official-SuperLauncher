# Modern PySide6 Application

A simple, modern Python GUI application built with PySide6 featuring a clean header, body, and footer layout.

## Features

- **Modern Design**: Clean, professional interface with proper spacing and typography
- **Three-Section Layout**: Header with navigation, body with content area, and footer with status
- **Responsive**: Adapts to different window sizes
- **Interactive Elements**: Buttons with hover effects and a text input area

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Application Structure

- **Header**: Contains the application title and navigation buttons (Home, About, Settings)
- **Body**: Main content area with welcome message, description, text input area, and action buttons
- **Footer**: Status indicator, copyright information, and version number

## Customization

The application uses CSS-like styling through PySide6's stylesheet system. You can modify the appearance by editing the `apply_styles()` method in `main.py`.

## Requirements

- Python 3.7+
- PySide6 >= 6.4.0
