"""
Terminal display and rendering for CertQuest.
"""

import os
import sys
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from .player import Player
    from .certification_loader import CertificationConfig

# Optional: colorama for cross-platform color support
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

    # Fallback stubs
    class Fore:
        RED = ""
        GREEN = ""
        YELLOW = ""
        CYAN = ""
        MAGENTA = ""
        WHITE = ""
        RESET = ""

    class Style:
        BRIGHT = ""
        DIM = ""
        RESET_ALL = ""


class Display:
    """Handles all terminal output and formatting."""

    def __init__(self, certification: "CertificationConfig" = None, width: int = 80):
        self.width = width
        self.cert = certification

        # Build domain names from certification config
        if certification:
            self.domain_names = {
                d['id']: d.get('short_name', d.get('name', f'Domain {d["id"]}'))
                for d in certification.domains
            }
        else:
            self.domain_names = {}

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def render_hud(self, player: "Player", player_term: str = "SEEKER") -> str:
        """
        Render the Heads-Up Display showing player stats.

        Args:
            player: The player object
            player_term: What to call the player (e.g., "SEEKER", "EMPLOYEE")
        """
        # Calculate HP bar (10 segments)
        hp_pct = max(0, min(1, player.hp / player.max_hp))
        hp_filled = int(hp_pct * 10)
        hp_bar = "#" * hp_filled + "-" * (10 - hp_filled)

        # Color HP based on level
        if HAS_COLOR:
            if player.hp > 60:
                hp_color = Fore.GREEN
            elif player.hp > 30:
                hp_color = Fore.YELLOW
            else:
                hp_color = Fore.RED
            hp_display = f"{hp_color}{hp_bar}{Style.RESET_ALL}"
        else:
            hp_display = hp_bar

        # XP progress bar (20 segments)
        max_xp = player.max_xp
        xp_pct = min(1, player.xp / max_xp) if max_xp > 0 else 0
        xp_filled = int(xp_pct * 20)
        xp_bar = "=" * xp_filled + "-" * (20 - xp_filled)

        domain_name = self.domain_names.get(player.current_domain, f"Domain {player.current_domain}")

        hud = f"""
+==============================================================================+
| {player_term}: {player.name:<14} | HP: [{hp_display}] {player.hp:>3}/{player.max_hp:<3} | XP: {player.xp:>4}/{max_xp}     |
| TITLE: {player.title:<15} | DOMAIN {player.current_domain}: {domain_name:<25} |
+------------------------------------------------------------------------------+
| XP: [{xp_bar}] {int(xp_pct*100):>3}%                                    |
+==============================================================================+
"""
        return hud

    def render_narrative(self, text: str, narrator: str = "CHRONICLER") -> str:
        """
        Wrap narrative text in atmospheric formatting.
        """
        wrapped = self._wrap_text(text.strip(), self.width - 6)
        lines = wrapped.split('\n')

        output = f"\n  [{narrator}]\n"
        output += "  " + "-" * (self.width - 4) + "\n"
        for line in lines:
            output += f"  {line}\n"
        output += "  " + "-" * (self.width - 4) + "\n"

        return output

    def render_choices(self, choices: list, show_theme_hint: bool = False) -> str:
        """
        Render numbered choices for the player.

        Args:
            choices: List of choice strings
            show_theme_hint: If True, show hint about theme switching
        """
        output = "\n  What action do you take?\n\n"
        for i, choice in enumerate(choices, 1):
            if HAS_COLOR:
                output += f"    {Fore.CYAN}[{i}]{Style.RESET_ALL} {choice}\n"
            else:
                output += f"    [{i}] {choice}\n"

        if show_theme_hint:
            if HAS_COLOR:
                output += f"\n    {Fore.MAGENTA}[0]{Style.RESET_ALL} {Style.DIM}Switch story theme{Style.RESET_ALL}\n"
            else:
                output += "\n    [0] Switch story theme\n"

        output += "\n  > "
        return output

    def render_success(self, text: str, xp_gained: int, hp_healed: int = 0) -> str:
        """Render success feedback with XP gain and optional HP recovery."""
        if HAS_COLOR:
            header = f"{Fore.GREEN}{'=' * 60}{Style.RESET_ALL}"
            xp_text = f"{Fore.GREEN}+{xp_gained} XP{Style.RESET_ALL}"
            check = f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL}"
            hp_text = f"  {Fore.GREEN}+{hp_healed} HP restored{Style.RESET_ALL}" if hp_healed > 0 else ""
        else:
            header = "=" * 60
            xp_text = f"+{xp_gained} XP"
            check = "[SUCCESS]"
            hp_text = f"  +{hp_healed} HP restored" if hp_healed > 0 else ""

        wrapped = self._wrap_text(text.strip(), self.width - 6)

        return f"""
  {header}
  {check} - {xp_text}{hp_text}
  {header}

  {wrapped}

  {header}
"""

    def render_failure(self, text: str, hp_lost: int, domain_ref: str,
                       correct_num: int = None, correct_text: str = None) -> str:
        """Render failure feedback with HP loss, correct answer, and reference."""
        if HAS_COLOR:
            header = f"{Fore.RED}{'=' * 60}{Style.RESET_ALL}"
            hp_text = f"{Fore.RED}-{hp_lost} HP{Style.RESET_ALL}"
            x_mark = f"{Fore.RED}[CONSEQUENCE]{Style.RESET_ALL}"
            correct_label = f"{Fore.GREEN}[CORRECT ANSWER]{Style.RESET_ALL}"
        else:
            header = "=" * 60
            hp_text = f"-{hp_lost} HP"
            x_mark = "[CONSEQUENCE]"
            correct_label = "[CORRECT ANSWER]"

        wrapped = self._wrap_text(text.strip(), self.width - 6)

        # Build correct answer section
        correct_section = ""
        if correct_num is not None and correct_text:
            correct_section = f"\n  {correct_label}\n  [{correct_num}] {correct_text}\n"

        return f"""
  {header}
  {x_mark} - {hp_text}
  {header}

  [POST-MORTEM ANALYSIS]
  {wrapped}
{correct_section}
  [REFERENCE: {domain_ref}]

  {header}
"""

    def _wrap_text(self, text: str, width: int) -> str:
        """Simple word-wrap implementation that preserves paragraph breaks."""
        paragraphs = text.split('\n\n')
        wrapped_paragraphs = []

        for paragraph in paragraphs:
            # Normalize whitespace within paragraph
            words = paragraph.split()
            if not words:
                wrapped_paragraphs.append('')
                continue

            lines = []
            current_line = []
            current_length = 0

            for word in words:
                if current_length + len(word) + 1 <= width:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)

            if current_line:
                lines.append(' '.join(current_line))

            wrapped_paragraphs.append('\n  '.join(lines))

        return '\n\n  '.join(wrapped_paragraphs)

    def slow_print(self, text: str, delay: float = 0.02) -> None:
        """Print text character by character for dramatic effect."""
        import time
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()
