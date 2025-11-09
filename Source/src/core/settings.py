from PyQt6.QtCore import QSettings


class Settings:
    def __init__(self):
        self.settings = QSettings('Scriptly', 'Editor')
        self.load_defaults()
        self.load()
        
    def load_defaults(self):
        self.defaults = {
            'editor': {
                'font_family': 'Consolas',
                'font_size': 12,
                'tab_size': 4,
                'use_spaces': True,
                'auto_indent': True,
                'word_wrap': True,
                'show_line_numbers': True,
                'highlight_current_line': True,
                'auto_save': False,
                'auto_save_interval': 5,  # minutes
                'show_whitespace': False,
                'show_indentation_guides': True,
                'bracket_matching': True
            },
            'theme': {
                'name': 'modern_dark',  # Modern dark is our default and only theme
                'syntax_theme': 'modern_dark'  # Match editor theme
            },
            'file_monitor': {
                'enabled': True,
                'check_interval': 2000  # milliseconds
            },
            'interface': {
                'show_status_bar': True,
                'show_minimap': True,
                'show_file_browser': True,
                'toolbar_visible': True,
                'tab_position': 'top'
            },
            'shortcuts': {
                'new_file': 'Ctrl+N',
                'open_file': 'Ctrl+O',
                'save_file': 'Ctrl+S',
                'save_as': 'Ctrl+Shift+S',
                'find': 'Ctrl+F',
                'replace': 'Ctrl+H',
                'goto_line': 'Ctrl+G',
                'toggle_comment': 'Ctrl+/',
                'increase_font': 'Ctrl++',
                'decrease_font': 'Ctrl+-',
                'toggle_file_browser': 'Ctrl+B'
            }
        }
        
    def load(self):
        for section, values in self.defaults.items():
            if not self.settings.contains(section):
                self.settings.setValue(section, values)
                
        self.editor = self.settings.value('editor', self.defaults['editor'])
        self.theme = self.settings.value('theme', self.defaults['theme'])
        self.file_monitor = self.settings.value('file_monitor', self.defaults['file_monitor'])
        self.interface = self.settings.value('interface', self.defaults['interface'])
        self.shortcuts = self.settings.value('shortcuts', self.defaults['shortcuts'])
        
    def save(self):
        self.settings.setValue('editor', self.editor)
        self.settings.setValue('theme', self.theme)
        self.settings.setValue('file_monitor', self.file_monitor)
        self.settings.setValue('interface', self.interface)
        self.settings.setValue('shortcuts', self.shortcuts)
        self.settings.sync()

    def reset_to_defaults(self):
        """Reset stored settings to the shipped defaults and reload them."""
        # clear any persisted settings for top-level keys and replace with defaults
        for key, val in self.defaults.items():
            try:
                self.settings.setValue(key, val)
            except Exception:
                pass
        # reload into runtime attributes
        self.editor = self.defaults['editor'].copy()
        self.theme = self.defaults['theme'].copy()
        self.file_monitor = self.defaults['file_monitor'].copy()
        self.interface = self.defaults['interface'].copy()
        self.shortcuts = self.defaults['shortcuts'].copy()
        # persist
        self.save()
        
    def get_editor_font(self):
        return {
            'family': self.editor['font_family'],
            'size': self.editor['font_size']
        }
        
    def get_theme_colors(self):
        return self.theme.get('colors', {})