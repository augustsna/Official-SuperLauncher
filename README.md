# SuperLauncher - Modern Application Launcher

A powerful, modern application launcher built with PySide6 featuring advanced icon scaling, drag-and-drop organization, and a clean grid-based interface.

## Features

- **Advanced Icon Scaling**: Multi-size icon extraction with high-quality scaling algorithms
- **DPI-Aware Rendering**: Crisp icons on all screen resolutions including high-DPI displays
- **Smart Caching**: Intelligent icon caching for improved performance
- **Drag & Drop**: Reorganize apps by dragging them, or pin new ones by dragging files/folders in from Explorer
- **Grid Layout**: Clean, organized grid-based app display similar to Windows Start Menu
- **Search & Filter**: Type to filter (`Ctrl+F`), press `Enter` to launch the first match, `Esc` to clear
- **Fast Launching**: Apps start directly through the Windows shell, using their own folder as the working directory
- **Safe Config**: Settings are written atomically to `%APPDATA%\SuperLauncher\config.json`; an unreadable config is kept as `config.corrupt.json` instead of being overwritten
- **Context Menus**: Rich context menus with app management options
- **Icon Diagnostics**: Built-in tools to troubleshoot icon issues
- **Quality Settings**: Configurable icon quality and performance options

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

## Testing and Demonstrations

### Icon Scaling Test
Test different icon extraction methods:
```bash
python test_icon_scaling.py
```

### Icon Improvements Demo
See side-by-side comparison of old vs. new methods:
```bash
python demo_icon_improvements.py
```

## Application Structure

- **Header**: Application title and search functionality
- **Body**: Grid-based app display with scrollable interface
- **Controls**: Add, run, and manage applications
- **Context Menus**: Right-click for app management options

## Icon Scaling Features

### Multi-Size Extraction
- Extracts icons at multiple resolutions (16, 24, 32, 48, 64, 128, 256)
- Automatically selects best source size for scaling
- Prevents pixelation and blurriness

### High-Quality Scaling
- Uses Qt's SmoothTransformation for best results
- Anti-aliasing and edge smoothing
- Configurable quality levels (High, Medium, Low)

### DPI-Aware Rendering
- Automatically detects high-DPI displays
- Scales icons appropriately for screen resolution
- Crisp appearance on all devices

### Smart Caching
- LRU cache for extracted icons
- Configurable cache size (50-500 icons)
- Automatic memory management

## Configuration

### Icon Quality Settings
- **Access**: More Options → Icon Quality Settings or press `Ctrl+I`
- **DPI Scaling**: Enable/disable high-DPI support
- **High-Quality Scaling**: Enable smooth scaling algorithms
- **Cache Settings**: Configure icon caching behavior

### Icon Diagnostics
- **Access**: Right-click app → Icon Diagnostics or press `Ctrl+D`
- **File Analysis**: Check file existence and type
- **Method Testing**: Test different extraction methods
- **Troubleshooting**: Get recommendations for icon issues

## Customization

The application uses CSS-like styling through PySide6's stylesheet system. You can modify the appearance by editing the styles in the respective UI methods.

## Requirements

- Python 3.7+
- PySide6 >= 6.4.0
