"""
Theme management for CertQuest.

Supports dynamic themes loaded from certification config.
Each certification can define its own set of themes (1 or more).
"""

from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .certification_loader import CertificationConfig


# Default themes used when certification doesn't specify any
DEFAULT_THEMES = {
    "fantasy": {
        "display_name": "Medieval Fantasy",
        "short_name": "Fantasy",
        "description": "Explore an ancient realm where knowledge is guarded by scribes and magic protects the secrets..."
    },
    "corporate": {
        "display_name": "Corporate Office",
        "short_name": "Corporate",
        "description": "Navigate challenges in the corporate world, where policies meet reality and coffee fuels compliance..."
    }
}


class ThemeManager:
    """
    Manages story themes dynamically loaded from certification config.

    Supports any number of themes (1 or more) defined in the certification's
    presentation.themes section. Falls back to default fantasy/corporate
    themes if none specified.

    Attributes:
        themes: Dict of theme_key -> theme_info
        theme_keys: List of available theme keys in order
        current_index: Index of currently selected theme
    """

    def __init__(self, certification: "CertificationConfig" = None):
        """
        Initialize theme manager from certification config.

        Args:
            certification: Loaded certification config. If None, uses defaults.
        """
        self.themes: Dict[str, Dict] = {}
        self.theme_keys: List[str] = []
        self.current_index: int = 0

        if certification:
            self._load_themes_from_config(certification)
        else:
            self._load_default_themes()

    def _load_themes_from_config(self, certification: "CertificationConfig") -> None:
        """Load themes from certification's presentation config."""
        presentation = certification.presentation
        config_themes = presentation.get('themes', {})

        if not config_themes:
            # No themes defined, use defaults
            self._load_default_themes()
            return

        # Load themes in the order they appear in config
        for theme_key, theme_data in config_themes.items():
            self.themes[theme_key] = {
                "display_name": theme_data.get('display_name', theme_data.get('game_title', theme_key.title())),
                "short_name": theme_data.get('short_name', theme_key.title()),
                "description": theme_data.get('description', ''),
                "game_title": theme_data.get('game_title', ''),
                "player_term": theme_data.get('player_term', 'Player'),
                "narrator": theme_data.get('narrator', 'NARRATOR'),
                "victory_message": theme_data.get('victory_message', 'Congratulations!')
            }
            self.theme_keys.append(theme_key)

        # If only one theme or no themes loaded, ensure we have at least one
        if not self.theme_keys:
            self._load_default_themes()

    def _load_default_themes(self) -> None:
        """Load the default fantasy/corporate themes."""
        self.themes = dict(DEFAULT_THEMES)
        self.theme_keys = list(DEFAULT_THEMES.keys())

    @property
    def current_theme_key(self) -> str:
        """Get the current theme's key string."""
        if not self.theme_keys:
            return "fantasy"
        return self.theme_keys[self.current_index]

    @property
    def current_theme(self) -> Dict:
        """Get the current theme's full info dict."""
        return self.themes.get(self.current_theme_key, {})

    @property
    def theme_count(self) -> int:
        """Get the number of available themes."""
        return len(self.theme_keys)

    def set_theme_by_key(self, theme_key: str) -> bool:
        """
        Set the current theme by its key.

        Args:
            theme_key: The theme key (e.g., 'fantasy', 'corporate')

        Returns:
            True if theme was found and set, False otherwise
        """
        if theme_key in self.theme_keys:
            self.current_index = self.theme_keys.index(theme_key)
            return True
        return False

    def set_theme_by_index(self, index: int) -> bool:
        """
        Set the current theme by index.

        Args:
            index: 0-based index into theme_keys

        Returns:
            True if valid index, False otherwise
        """
        if 0 <= index < len(self.theme_keys):
            self.current_index = index
            return True
        return False

    def toggle_theme(self) -> str:
        """
        Cycle to the next theme.

        Returns:
            The new current theme key
        """
        if self.theme_keys:
            self.current_index = (self.current_index + 1) % len(self.theme_keys)
        return self.current_theme_key

    def get_theme_key(self) -> str:
        """Get the current theme key (for accessing theme-specific content)."""
        return self.current_theme_key

    def get_display_name(self) -> str:
        """Get the display name of the current theme."""
        return self.current_theme.get('display_name', self.current_theme_key.title())

    def get_short_name(self) -> str:
        """Get the short name of the current theme."""
        return self.current_theme.get('short_name', self.current_theme_key.title())

    def get_player_term(self) -> str:
        """Get the player term for the current theme."""
        return self.current_theme.get('player_term', 'Player')

    def get_narrator(self) -> str:
        """Get the narrator name for the current theme."""
        return self.current_theme.get('narrator', 'NARRATOR')

    def get_all_themes(self) -> List[Dict]:
        """
        Return list of all available themes with their info.

        Returns:
            List of dicts with 'key', 'display_name', 'description'
        """
        result = []
        for key in self.theme_keys:
            theme = self.themes[key]
            result.append({
                'key': key,
                'display_name': theme.get('display_name', key.title()),
                'short_name': theme.get('short_name', key.title()),
                'description': theme.get('description', ''),
                'game_title': theme.get('game_title', '')
            })
        return result

    def has_multiple_themes(self) -> bool:
        """Check if there are multiple themes available."""
        return len(self.theme_keys) > 1
