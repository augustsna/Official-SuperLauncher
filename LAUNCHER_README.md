# SuperLauncher - Application Launcher

A powerful, modern application launcher built with PySide6 that integrates seamlessly with your existing template app structure.

## Features

### 🚀 Core Functionality
- **Pin Applications**: Add frequently used applications, documents, and files
- **Smart Search**: Filter your pinned items with real-time search
- **Icon Extraction**: Automatically extracts proper icons from Windows executables
- **Context Menus**: Right-click for additional options (run as admin, open location, etc.)
- **System Tray**: Minimize to system tray for quick access

### 🎯 Advanced Features
- **Multiple Launch Methods**: Run normally, as administrator, or open file location
- **Persistent Storage**: Saves your pinned items between sessions
- **Keyboard Shortcuts**: 
  - `Ctrl+F`: Focus search
  - `Ctrl+N`: Add new items
  - `Ctrl+R`: Run selected item
  - `Ctrl+W`: Close window
- **Smart Icon Fallbacks**: Gracefully handles missing icons with intelligent defaults

### 🎨 Modern UI
- **Responsive Design**: Adapts to different window sizes
- **Professional Styling**: Modern button styles with hover effects
- **Splitter Layout**: Efficient use of screen space
- **Custom Styling**: Integrated with your existing template app styles

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Optional Dependencies** (for enhanced icon extraction):
   ```bash
   pip install pywin32 pillow
   ```

## Usage

### Basic Operation

1. **Launch the Application**:
   ```bash
   python main.py
   ```

2. **Add Applications**:
   - Click "Add Apps" button
   - Navigate to and select applications
   - Applications are automatically pinned with proper icons

3. **Search and Launch**:
   - Use the search bar to filter your pinned items
   - Double-click any item to launch it
   - Use keyboard shortcuts for quick access

### Advanced Features

#### Context Menu (Right-click)
- **Run**: Launch normally
- **Run as administrator**: Launch with elevated privileges
- **Open location**: Open the folder containing the item
- **Rename**: Customize the display name
- **Unpin**: Remove from launcher

#### System Tray
- **Minimize to tray**: Click the X button to minimize to system tray
- **Quick access**: Click tray icon to show/hide the launcher
- **Tray menu**: Right-click tray icon for options

### Configuration

The launcher automatically creates a configuration file in:
```
%APPDATA%\SuperLauncher\config.json
```

You can also customize the main app settings in `launcher_config.json`.

## Architecture

### Key Classes

- **`LauncherWindow`**: Main window extending `MainWindowBase`
- **`IconExtractor`**: Handles icon extraction with multiple fallback methods
- **`ConfigStore`**: Manages persistent storage of pinned items
- **`AppList`**: Displays and manages the list of pinned applications
- **`TrayApp`**: System tray integration

### Integration with Template App

The launcher seamlessly integrates with your existing template app structure:
- Extends `MainWindowBase` for consistent styling and behavior
- Uses existing configuration and styling systems
- Maintains the same project structure and conventions

## Customization

### Styling
The launcher uses your existing template app styles and adds custom styling for buttons and controls. You can modify the styling in the `_build_launcher_ui` method.

### Configuration
Modify `launcher_config.json` to customize:
- Window title and size
- Default start directory for adding items
- Icon size preferences
- Feature toggles

### Adding Features
The modular design makes it easy to add new features:
- New context menu options
- Additional keyboard shortcuts
- Custom launch methods
- Enhanced filtering options

## Troubleshooting

### Common Issues

1. **Icons not displaying**:
   - Install `pywin32` and `pillow` for enhanced icon extraction
   - The app will fall back to system icons if advanced extraction fails

2. **Applications not launching**:
   - Check file paths are valid
   - Ensure applications exist at the specified locations
   - Try running as administrator if permission issues occur

3. **Configuration not saving**:
   - Check write permissions in `%APPDATA%` directory
   - Verify the config file path is accessible

### Performance Tips

- Keep the number of pinned items reasonable (under 100 for best performance)
- Use descriptive names for easier searching
- Group related applications with similar naming conventions

## Development

### Adding New Features

1. **Extend `LauncherWindow`** class for new functionality
2. **Modify `ConfigStore`** for additional data persistence
3. **Update `AppList`** for new display features
4. **Enhance `IconExtractor`** for additional icon sources

### Testing

The launcher includes comprehensive error handling and fallbacks. Test with:
- Various file types (exe, lnk, documents, etc.)
- Different permission levels
- Missing or corrupted files
- Network and removable drives

## License

This launcher functionality is integrated into your existing project structure and follows the same licensing terms.

## Support

For issues or feature requests, refer to your project's main documentation and support channels.
