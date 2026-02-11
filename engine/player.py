"""
Player state management for CertQuest.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, TYPE_CHECKING
from enum import Enum, auto

if TYPE_CHECKING:
    from .certification_loader import CertificationConfig


class GameStatus(Enum):
    """Enumeration of possible game states."""
    PLAYING = auto()
    VICTORY = auto()
    COMPLETED = auto()  # Finished all domains


@dataclass
class Player:
    """
    Represents the player's current state in the game.

    Attributes:
        name: The player's chosen name
        hp: Health points (can go negative - tracks performance)
        max_hp: Maximum health points
        xp: Experience points (tracks progress)
        current_domain: Which domain player is in (1-N)
        scenarios_completed: List of scenario IDs already completed
        wrong_answers: Count of incorrect answers
        correct_answers: Count of correct answers
        domain_stats: Per-domain tracking of correct/wrong answers
        _domain_count: Number of domains in this certification
        _titles: Title progression thresholds from certification config
    """
    name: str
    hp: int = 100
    max_hp: int = 100
    xp: int = 0
    current_domain: int = 1
    scenarios_completed: List[str] = field(default_factory=list)
    wrong_answers: int = 0
    correct_answers: int = 0
    domain_stats: Dict[int, Dict[str, int]] = field(default_factory=dict)

    # Certification-specific settings (set via from_certification factory)
    _domain_count: int = field(default=8, repr=False)
    _titles: List[Dict] = field(default_factory=list, repr=False)
    _max_xp: int = field(default=4000, repr=False)

    def __post_init__(self):
        """Initialize domain_stats if not provided."""
        if not self.domain_stats:
            self.domain_stats = {
                i: {"correct": 0, "wrong": 0}
                for i in range(1, self._domain_count + 1)
            }

    @classmethod
    def from_certification(cls, name: str, cert_config: "CertificationConfig") -> "Player":
        """
        Factory method to create a Player from a certification config.

        Args:
            name: Player's name
            cert_config: Loaded certification configuration

        Returns:
            Configured Player instance
        """
        scoring = cert_config.scoring

        # Calculate max XP based on domains and scenarios
        scenarios_per_domain = scoring.get('scenarios_per_domain', 10)
        xp_per_correct = scoring.get('xp_per_correct', 50)
        max_xp = cert_config.domain_count * scenarios_per_domain * xp_per_correct

        return cls(
            name=name,
            hp=scoring.get('starting_hp', 100),
            max_hp=scoring.get('max_hp', 100),
            _domain_count=cert_config.domain_count,
            _titles=scoring.get('titles', []),
            _max_xp=max_xp
        )

    @property
    def domain_count(self) -> int:
        """Get the number of domains in this certification."""
        return self._domain_count

    @property
    def max_xp(self) -> int:
        """Get the maximum possible XP."""
        return self._max_xp

    @property
    def title(self) -> str:
        """Calculate current title based on XP."""
        current_title = "Novice"
        for title_def in sorted(self._titles, key=lambda t: t.get('threshold', 0)):
            if self.xp >= title_def.get('threshold', 0):
                current_title = title_def.get('fantasy', title_def.get('title', 'Unknown'))
        return current_title

    def get_title_for_theme(self, theme: str = 'fantasy') -> str:
        """Get the current title for a specific theme."""
        current_title = "Novice"
        for title_def in sorted(self._titles, key=lambda t: t.get('threshold', 0)):
            if self.xp >= title_def.get('threshold', 0):
                current_title = title_def.get(theme, title_def.get('fantasy', 'Unknown'))
        return current_title

    @property
    def status(self) -> GameStatus:
        """Determine current game status. Victory requires completing all domains."""
        if self.current_domain > self._domain_count:
            return GameStatus.VICTORY
        return GameStatus.PLAYING

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage (correct / total answers)."""
        total = self.correct_answers + self.wrong_answers
        if total == 0:
            return 0.0
        return (self.correct_answers / total) * 100

    @property
    def performance_rating(self) -> str:
        """Get performance rating based on accuracy."""
        acc = self.accuracy
        if acc >= 90:
            return "Exemplary"
        elif acc >= 80:
            return "Proficient"
        elif acc >= 70:
            return "Competent"
        elif acc >= 60:
            return "Developing"
        else:
            return "Needs Improvement"

    def take_damage(self, amount: int, domain: int = None) -> int:
        """
        Reduce HP by amount (can go negative for performance tracking).
        Tracks per-domain statistics if domain is provided.
        """
        self.hp -= amount
        self.wrong_answers += 1
        if domain and domain in self.domain_stats:
            self.domain_stats[domain]["wrong"] += 1
        return amount

    def gain_xp(self, amount: int, domain: int = None) -> bool:
        """
        Increase XP by amount.
        Returns True if title changed.
        Tracks per-domain statistics if domain is provided.
        """
        old_title = self.title
        self.xp += amount
        self.correct_answers += 1
        if domain and domain in self.domain_stats:
            self.domain_stats[domain]["correct"] += 1
        new_title = self.title
        return old_title != new_title

    def get_domain_accuracy(self, domain: int) -> float:
        """Calculate accuracy percentage for a specific domain."""
        if domain not in self.domain_stats:
            return 0.0
        stats = self.domain_stats[domain]
        total = stats["correct"] + stats["wrong"]
        if total == 0:
            return 0.0
        return (stats["correct"] / total) * 100

    def heal(self, amount: int) -> int:
        """Restore HP up to max_hp, returning actual healing."""
        actual_heal = min(self.max_hp - self.hp, amount)
        self.hp += actual_heal
        return actual_heal

    def complete_scenario(self, scenario_id: str) -> None:
        """Mark a scenario as completed."""
        if scenario_id not in self.scenarios_completed:
            self.scenarios_completed.append(scenario_id)
