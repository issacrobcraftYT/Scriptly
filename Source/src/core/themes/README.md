# Creating Themes for Scriptly

This guide will help you create custom themes for Scriptly. A theme consists of two files:
1. A `.qss` file containing the Qt stylesheet (similar to CSS)
2. A `.json` file containing color definitions and metadata

## Theme File Structure

### theme_name.qss
This file contains the Qt stylesheet that defines how the UI elements look. The file should be named `theme_name.qss` where `theme_name` is the name of your theme in lowercase with underscores for spaces.

### theme_name.json
This file contains metadata about your theme and color definitions used by the terminal. The file should have the same name as your .qss file but with a .json extension.

## Creating a Theme

1. Start by copying the `modern_light.qss` and `modern_light.json` files as templates
2. Rename them to your theme name (e.g., `my_cool_theme.qss` and `my_cool_theme.json`)
3. Edit the .json file to update the metadata and colors
4. Edit the .qss file to customize the appearance

## Installing Themes

To install a custom theme:

1. Open Scriptly
2. Go to Settings (Ctrl+,)
3. Click on the "Theme" tab
4. Click "Import Theme" and select your .qss file
5. If you have a companion .json file, it will be imported automatically

You can also manually place the theme files in one of these directories:
- Built-in themes: `src/core/themes/`
- User themes: `~/.scriptly/themes/` (recommended for custom themes)

## Theme JSON Structure

```json
{
    "name": "My Cool Theme",
    "version": "1.0.0",
    "author": "Your Name",
    "colors": {
        "background": "#ffffff",
        "foreground": "#333333",
        "selection": "#90caf9",
        "cursor": "#333333",
        "black": "#000000",
        "red": "#e53935",
        "green": "#43a047",
        "yellow": "#fdd835",
        "blue": "#1e88e5",
        "magenta": "#8e24aa",
        "cyan": "#00acc1",
        "white": "#ffffff",
        "brightBlack": "#757575",
        "brightRed": "#ef5350",
        "brightGreen": "#66bb6a",
        "brightYellow": "#ffee58",
        "brightBlue": "#42a5f5",
        "brightMagenta": "#ab47bc",
        "brightCyan": "#26c6da",
        "brightWhite": "#ffffff"
    }
}
```

## QSS Styling Tips

The .qss file uses Qt Style Sheets, which are similar to CSS. Here are some key elements you can style:

```css
/* Main Window */
QMainWindow, QDialog {
    background-color: #your-color;
    color: #your-color;
}

/* Menus */
QMenuBar {
    background-color: #your-color;
}

/* Tabs */
QTabBar::tab {
    background-color: #your-color;
}

/* Editor */
QPlainTextEdit, QTextEdit {
    background-color: #your-color;
    color: #your-color;
}

/* File Browser */
QTreeView {
    background-color: #your-color;
}

/* See modern_light.qss for more examples */
```

## Testing Your Theme

1. After importing your theme, select it from the theme dropdown in Settings
2. The changes will apply immediately
3. Test your theme with different features:
   - Editor with different file types
   - Terminal
   - File browser
   - Menus and dialogs
4. Make adjustments as needed and reimport

## Contributing Themes

If you've created a great theme, consider sharing it with the community! You can:
1. Fork the Scriptly repository
2. Add your theme to the `src/core/themes/` directory
3. Submit a pull request

## Need Help?

If you need help creating a theme or run into issues, please:
1. Check existing themes for examples
2. Read the Qt Style Sheets documentation
3. Open an issue on GitHub with questions