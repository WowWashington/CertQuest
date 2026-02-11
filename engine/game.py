"""
Core game loop and orchestration for CertQuest.
Certification-agnostic game engine that loads content dynamically.
"""

import random
from typing import Dict, List, Optional
from .player import Player, GameStatus
from .display import Display
from .input_handler import InputHandler
from .theme_manager import ThemeManager, StoryTheme
from .certification_loader import CertificationConfig


class Scenario:
    """
    Represents a single scenario/encounter in the game.

    A scenario presents a situation and choices, with consequences
    based on certification knowledge. Supports multiple themes for presenting
    the same concepts in different narrative styles.
    """

    def __init__(self, data: Dict):
        self.id: str = data.get('id', 'unknown')
        self.domain: int = data.get('domain', 1)
        self.xp_reward: int = data.get('xp_reward', 50)
        self.hp_penalty: int = data.get('hp_penalty', 20)
        self.correct_index: int = data.get('correct_index', 0)  # 0-based
        self.failure_text: str = data.get('failure_text', '')  # Generic fallback
        self.domain_reference: str = data.get('domain_reference', '')

        # Theme-aware content
        self.themes: Dict = data.get('themes', {})

    def get_themed_content(self, theme: StoryTheme) -> Dict:
        """
        Return theme-specific content, with fallback to fantasy.

        Returns dict with: title, narrative, choices, success_text, failure_texts
        """
        theme_key = theme.value
        if theme_key in self.themes:
            return self.themes[theme_key]
        # Fallback to fantasy theme
        return self.themes.get('fantasy', {
            'title': 'SCENARIO',
            'narrative': '',
            'choices': [],
            'success_text': '',
            'failure_texts': {}
        })

    def get_failure_text(self, theme: StoryTheme, chosen_index: int) -> str:
        """Get the failure text for a specific wrong choice."""
        content = self.get_themed_content(theme)
        failure_texts = content.get('failure_texts', {})

        # Try theme-specific failure text first (handle both int and str keys from YAML)
        if chosen_index in failure_texts:
            return failure_texts[chosen_index]
        if str(chosen_index) in failure_texts:
            return failure_texts[str(chosen_index)]

        # Try legacy choice format (failure_reason in choice dict)
        choices = content.get('choices', [])
        if chosen_index < len(choices):
            choice = choices[chosen_index]
            if isinstance(choice, dict) and choice.get('failure_reason'):
                return choice['failure_reason']

        # Fall back to generic failure text
        return self.failure_text


class Game:
    """
    Main game controller that orchestrates the gameplay loop.
    Certification-agnostic - all content loaded from CertificationConfig.
    """

    def __init__(self, certification: CertificationConfig):
        self.cert = certification
        self.display = Display(certification)
        self.input = InputHandler()
        self.theme_manager = ThemeManager()
        self.player: Optional[Player] = None
        self.scenarios: Dict[int, List[Scenario]] = {}  # domain -> all scenarios
        self.selected_scenarios: Dict[int, List[Scenario]] = {}  # domain -> selected for this playthrough
        self.current_scenario: Optional[Scenario] = None
        self._load_scenarios()

    @property
    def scenarios_per_domain(self) -> int:
        """How many scenarios to randomly select per domain."""
        return self.cert.scoring.get('scenarios_per_domain', 10)

    @property
    def domain_count(self) -> int:
        """Number of domains in this certification."""
        return self.cert.domain_count

    def _load_scenarios(self) -> None:
        """Load all scenario data from the certification config."""
        # Initialize empty lists for each domain
        for domain in range(1, self.domain_count + 1):
            self.scenarios[domain] = []

        # Load scenarios from certification config
        for domain_num, scenario_list in self.cert.scenarios.items():
            for scenario_data in scenario_list:
                scenario = Scenario(scenario_data)
                if domain_num in self.scenarios:
                    self.scenarios[domain_num].append(scenario)

    def run(self) -> None:
        """Main entry point - run the complete game."""
        self.display.clear_screen()
        self._show_title()

        # Theme selection
        self._select_theme()

        # Introduction
        self._show_introduction()

        # Get player name
        name = self._get_player_name()
        if name is None:
            return

        # Create player from certification config
        self.player = Player.from_certification(name, self.cert)

        # Domain selection (optional - start at a specific domain)
        self._select_starting_domain()

        # Main game loop
        self._game_loop()

    def _show_title(self) -> None:
        """Display the certification title."""
        title = f"""
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                           ║
    ║                              CERTQUEST                                    ║
    ║                     {self.cert.name:^30}                           ║
    ║                                                                           ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
        """
        print(title)
        if self.cert.full_name:
            print(f"    {self.cert.full_name}")
        if self.cert.organization:
            print(f"    By {self.cert.organization}")
        print()

    def _select_starting_domain(self) -> None:
        """Allow player to choose which domain to start from."""
        self.display.clear_screen()

        # Build domain names from certification config
        domain_names = {d['id']: d['name'] for d in self.cert.domains}

        if self.theme_manager.current_theme == StoryTheme.CORPORATE:
            print("\n  " + "=" * 60)
            print("  TRAINING MODULE SELECTION")
            print("  " + "=" * 60)
            print("\n  Which department would you like to start your training in?\n")
        else:
            print("\n  " + "=" * 60)
            print("  DOMAIN SELECTION")
            print("  " + "=" * 60)
            print("\n  Which domain would you like to begin your trials?\n")

        for num, name in domain_names.items():
            print(f"    [{num}] Domain {num}: {name}")

        print(f"\n    [ENTER] Start from the beginning (Domain 1)")
        print()

        while True:
            choice = self.input.get_text(f"  Select starting domain (1-{self.domain_count} or ENTER): ")
            if choice is None:
                return

            choice = choice.strip()

            # Default to domain 1 if just pressing enter
            if choice == '':
                self.player.current_domain = 1
                break

            # Validate numeric input
            if choice.isdigit():
                domain = int(choice)
                if 1 <= domain <= self.domain_count:
                    self.player.current_domain = domain
                    if domain > 1:
                        # Award XP credit for skipped domains
                        xp_per_domain = self.scenarios_per_domain * self.cert.scoring.get('xp_per_correct', 50)
                        skipped_domains = domain - 1
                        skipped_xp = skipped_domains * xp_per_domain
                        self.player.xp = skipped_xp

                        if self.theme_manager.current_theme == StoryTheme.CORPORATE:
                            print(f"\n  Starting at Level {domain}: {domain_names.get(domain, '')}")
                            print(f"  (Previous {skipped_domains} module(s) marked as reviewed: +{skipped_xp} XP)")
                        else:
                            print(f"\n  Beginning at Domain {domain}: {domain_names.get(domain, '')}")
                            print(f"  (Earlier {skipped_domains} domain(s) acknowledged as mastered: +{skipped_xp} XP)")
                        self.input.wait_for_enter("\n  Press ENTER to continue...")
                    break

            print(f"  Please enter a number 1-{self.domain_count}, or press ENTER for Domain 1.")

        # Show educational introduction for the starting domain
        self._show_domain_introduction(self.player.current_domain)

    def _select_theme(self) -> None:
        """Let the player choose their preferred story theme."""
        # Get theme info from certification config if available
        presentation = self.cert.presentation
        fantasy_info = presentation.get('themes', {}).get('fantasy', {})
        corporate_info = presentation.get('themes', {}).get('corporate', {})

        fantasy_title = fantasy_info.get('game_title', 'Medieval Fantasy')
        corporate_title = corporate_info.get('game_title', 'Corporate Office')

        print("\n  Choose your story style:\n")
        print(f"    [1] Medieval Fantasy - {fantasy_title}")
        print("        Explore an ancient realm where knowledge is guarded...")
        print()
        print(f"    [2] Corporate Office - {corporate_title}")
        print("        Navigate office politics, meetings, and compliance...")
        print()
        print("    (You can switch themes anytime during scenarios by pressing 0)")
        print()

        while True:
            choice = self.input.get_text("  Select theme (1 or 2): ")
            if choice is None:
                return
            choice = choice.strip()
            if choice == '1':
                self.theme_manager.set_theme(StoryTheme.FANTASY)
                break
            elif choice == '2':
                self.theme_manager.set_theme(StoryTheme.CORPORATE)
                break
            print("  Please enter 1 or 2.")

        self.display.clear_screen()
        self._show_theme_title()

    def _show_theme_title(self) -> None:
        """Display the title for the current theme."""
        presentation = self.cert.presentation
        theme_key = self.theme_manager.get_theme_key()
        theme_info = presentation.get('themes', {}).get(theme_key, {})
        game_title = theme_info.get('game_title', self.cert.name)

        title = f"""
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                           ║
    ║  {game_title:^71}  ║
    ║                                                                           ║
    ║                     A {self.cert.name} Training Experience                      ║
    ║                                                                           ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
        """
        print(title)

    def _show_introduction(self) -> None:
        """Display the game's opening narrative (theme-aware)."""
        presentation = self.cert.presentation
        theme_key = self.theme_manager.get_theme_key()
        theme_info = presentation.get('themes', {}).get(theme_key, {})

        narrator = theme_info.get('narrator', 'NARRATOR')

        if self.theme_manager.current_theme == StoryTheme.CORPORATE:
            intro = f"""
Welcome to the {self.cert.name} Training Program!

You've been selected for this comprehensive training experience.
{self.domain_count} modules await your completion.

Complete your training with flying colors, and you'll earn recognition
as a certified professional.

Good luck - and remember, the coffee in the break room is free.
            """
            print(self.display.render_narrative(intro, narrator))
        else:
            intro = f"""
The time has come to prove your worth.

Within these ancient halls, knowledge is power, and mastery is earned.
You have been summoned to face {self.domain_count} domains of trials.

Make wise choices, and you shall ascend to recognition
as a certified professional.

Let your journey begin.
            """
            print(self.display.render_narrative(intro, narrator))

        self.input.wait_for_enter("\n  Press ENTER to begin your journey...")

    def _get_player_name(self) -> Optional[str]:
        """Prompt player for their character name (theme-aware)."""
        presentation = self.cert.presentation
        theme_key = self.theme_manager.get_theme_key()
        theme_info = presentation.get('themes', {}).get(theme_key, {})
        player_term = theme_info.get('player_term', 'Seeker')

        if self.theme_manager.current_theme == StoryTheme.CORPORATE:
            print("\n  What name should we put on your desk nameplate?")
        else:
            print(f"\n  What name shall the Chronicles record for you, {player_term}?")

        name = self.input.get_text("  > ")
        if name:
            if self.theme_manager.current_theme == StoryTheme.CORPORATE:
                print(f"\n  Welcome aboard, {name}. Let's get started.\n")
            else:
                print(f"\n  Welcome, {name}. May your judgment be sound.\n")
            self.input.wait_for_enter("  Press ENTER to continue...")
        return name

    def _game_loop(self) -> None:
        """Core gameplay loop."""
        presentation = self.cert.presentation
        theme_key = self.theme_manager.get_theme_key()
        theme_info = presentation.get('themes', {}).get(theme_key, {})
        player_term = theme_info.get('player_term', 'SEEKER').upper()

        while self.player.status == GameStatus.PLAYING:
            self.display.clear_screen()

            # Show HUD
            print(self.display.render_hud(self.player, player_term))

            # Get next scenario
            scenario = self._get_next_scenario()
            if scenario is None:
                # No more scenarios in current domain, advance
                if not self._advance_domain():
                    # No more domains, game complete
                    break
                continue

            self.current_scenario = scenario

            # Run the scenario
            self._run_scenario(scenario)

            # Check for game end conditions
            if self.player.status != GameStatus.PLAYING:
                break

            # Pause before next scenario
            self.input.wait_for_enter()

        # Game over
        self._show_ending()

    def _select_scenarios_for_domain(self, domain: int) -> None:
        """Randomly select scenarios for a domain from the available pool."""
        all_domain_scenarios = self.scenarios.get(domain, [])
        count = min(self.scenarios_per_domain, len(all_domain_scenarios))
        if count > 0:
            self.selected_scenarios[domain] = random.sample(all_domain_scenarios, count)
        else:
            self.selected_scenarios[domain] = []

    def _get_next_scenario(self) -> Optional[Scenario]:
        """Get the next unplayed scenario from the randomly selected pool."""
        domain = self.player.current_domain

        # Select scenarios for this domain if not already done
        if domain not in self.selected_scenarios:
            self._select_scenarios_for_domain(domain)

        for scenario in self.selected_scenarios.get(domain, []):
            if scenario.id not in self.player.scenarios_completed:
                return scenario

        return None

    def _advance_domain(self) -> bool:
        """Move player to the next domain. Returns False if no more domains."""
        if self.player.current_domain < self.domain_count:
            self.player.current_domain += 1

            # Get domain name
            domain_names = {d['id']: d['name'] for d in self.cert.domains}
            next_domain_name = domain_names.get(self.player.current_domain, f'Domain {self.player.current_domain}')

            if self.theme_manager.current_theme == StoryTheme.CORPORATE:
                print(self.display.render_narrative(
                    f"Congratulations! You've completed that module. "
                    f"Time to move on to Level {self.player.current_domain}: {next_domain_name}.",
                    "HR NOTIFICATION"
                ))
            else:
                print(self.display.render_narrative(
                    f"You have proven yourself in this domain. "
                    f"The path to Domain {self.player.current_domain}: {next_domain_name} opens before you...",
                    "THE CITADEL"
                ))
            self.input.wait_for_enter("\n  Press ENTER to enter the next domain...")
            # Show educational introduction for the new domain
            self._show_domain_introduction(self.player.current_domain)
            return True
        return False

    def _show_domain_introduction(self, domain_num: int) -> None:
        """Display educational content when entering a new domain (theme-aware)."""
        intros = self.cert.intros
        if not intros:
            return

        domain_intro = intros.get(domain_num) or intros.get(str(domain_num))
        if not domain_intro:
            return

        self.display.clear_screen()

        # Get domain info for banner
        domain_info = None
        for d in self.cert.domains:
            if d['id'] == domain_num:
                domain_info = d
                break

        if domain_info:
            theme_key = self.theme_manager.get_theme_key()
            theme_content = domain_info.get('themes', {}).get(theme_key, {})
            domain_title = theme_content.get('title', domain_info.get('name', f'DOMAIN {domain_num}'))

            banner = f"""
    +===================================================================+
    |  [DOMAIN {domain_num}] {domain_title:<50} |
    +===================================================================+
            """
            print(banner)

        # Get theme-appropriate intro text
        theme_key = self.theme_manager.get_theme_key()
        if theme_key in domain_intro:
            intro_text = domain_intro[theme_key].get('introduction', '')
            narrator = domain_intro[theme_key].get('narrator', 'NARRATOR')
        else:
            intro_text = domain_intro.get('introduction', '')
            narrator = domain_intro.get('narrator', 'NARRATOR')

        if intro_text:
            print(self.display.render_narrative(intro_text, narrator))
            self.input.wait_for_enter("\n  Press ENTER to begin the trials of this domain...")

    def _run_scenario(self, scenario: Scenario) -> None:
        """Execute a single scenario encounter with theme support."""
        while True:
            # Get themed content for current theme
            content = scenario.get_themed_content(self.theme_manager.current_theme)
            title = content.get('title', 'SCENARIO')
            narrative = content.get('narrative', '')
            choices = content.get('choices', [])

            # Extract choice texts (handle both dict and string formats)
            choice_texts = []
            for c in choices:
                if isinstance(c, dict):
                    choice_texts.append(c.get('text', str(c)))
                else:
                    choice_texts.append(str(c))

            # Display scenario narrative
            print(self.display.render_narrative(narrative, title))

            # Show choices with theme toggle hint
            print(self.display.render_choices(choice_texts, show_theme_hint=True), end="")

            # Get player choice
            while True:
                result = self.input.get_choice(len(choices))

                if result[0] == 'quit':
                    if self.input.confirm("  Abandon your quest? [y/N] "):
                        self.player.current_domain = self.domain_count + 1  # Force game end
                        return
                    print(self.display.render_choices(choice_texts, show_theme_hint=True), end="")
                    continue

                if result[0] == 'help':
                    self._show_help()
                    print(self.display.render_choices(choice_texts, show_theme_hint=True), end="")
                    continue

                if result[0] == 'status':
                    presentation = self.cert.presentation
                    theme_key = self.theme_manager.get_theme_key()
                    theme_info = presentation.get('themes', {}).get(theme_key, {})
                    player_term = theme_info.get('player_term', 'SEEKER').upper()
                    print(self.display.render_hud(self.player, player_term))
                    print(self.display.render_choices(choice_texts, show_theme_hint=True), end="")
                    continue

                if result[0] == 'theme_toggle':
                    # Toggle theme and redisplay the scenario
                    new_theme = self.theme_manager.toggle_theme()
                    self.display.clear_screen()
                    presentation = self.cert.presentation
                    theme_key = self.theme_manager.get_theme_key()
                    theme_info = presentation.get('themes', {}).get(theme_key, {})
                    player_term = theme_info.get('player_term', 'SEEKER').upper()
                    print(self.display.render_hud(self.player, player_term))
                    theme_name = self.theme_manager.get_display_name()
                    print(f"\n  [Theme switched to: {theme_name}]\n")
                    break  # Break inner loop to redisplay with new theme

                if result[0] == 'invalid':
                    print(f"  Invalid choice. Enter 1-{len(choices)}, 0 to switch theme, or 'help'.")
                    print("  > ", end="")
                    continue

                # Valid choice - process it
                chosen = result[1] - 1  # Convert to 0-based

                # Process the choice
                if chosen == scenario.correct_index:
                    self._handle_success(scenario)
                else:
                    self._handle_failure(scenario, chosen)

                # Mark scenario complete
                self.player.complete_scenario(scenario.id)
                return  # Exit the method

            # If we get here, theme was toggled - continue outer loop to redisplay

    def _handle_success(self, scenario: Scenario) -> None:
        """Process a correct answer (theme-aware)."""
        title_changed = self.player.gain_xp(scenario.xp_reward, scenario.domain)

        # HP regeneration: restore 5 HP on correct answer if below max
        hp_healed = 0
        if self.player.hp < self.player.max_hp:
            hp_healed = self.player.heal(5)

        # Get themed success text
        content = scenario.get_themed_content(self.theme_manager.current_theme)
        success_text = content.get('success_text', 'Correct!')

        print(self.display.render_success(
            success_text,
            scenario.xp_reward,
            hp_healed
        ))

        if title_changed:
            title = self.player.get_title_for_theme(self.theme_manager.get_theme_key())
            if self.theme_manager.current_theme == StoryTheme.CORPORATE:
                print(f"\n  *** PROMOTION! New title: {title} ***\n")
            else:
                print(f"\n  *** You have earned a new title: {title} ***\n")

    def _handle_failure(self, scenario: Scenario, chosen: int) -> None:
        """Process an incorrect answer (theme-aware)."""
        self.player.take_damage(scenario.hp_penalty, scenario.domain)

        # Get the specific reasoning for this wrong choice (theme-aware)
        failure_reason = scenario.get_failure_text(self.theme_manager.current_theme, chosen)

        # Get the correct answer text for display
        content = scenario.get_themed_content(self.theme_manager.current_theme)
        choices = content.get('choices', [])
        correct_index = scenario.correct_index
        correct_text = ""
        if correct_index < len(choices):
            choice = choices[correct_index]
            if isinstance(choice, dict):
                correct_text = choice.get('text', str(choice))
            else:
                correct_text = str(choice)

        print(self.display.render_failure(
            failure_reason,
            scenario.hp_penalty,
            scenario.domain_reference,
            correct_index + 1,  # Convert to 1-based for display
            correct_text
        ))

    def _show_help(self) -> None:
        """Display help information."""
        help_text = f"""
  +------------------------------------------------------------------+
  |                         COMMANDS                                 |
  +------------------------------------------------------------------+
  |  [1-4]   - Select a numbered choice                              |
  |  [0]     - Switch story theme (Fantasy/Corporate)                |
  |  help    - Show this help message                                |
  |  status  - Show your current stats                               |
  |  quit    - End your session early                                |
  +------------------------------------------------------------------+
  |                           GOAL                                   |
  +------------------------------------------------------------------+
  |  Complete all {self.domain_count} domains to finish your training.             |
  |  Your final score reflects your mastery of {self.cert.name} concepts.     |
  |  There is no death penalty - this is training!                   |
  +------------------------------------------------------------------+
        """
        print(help_text)

    def _show_ending(self) -> None:
        """Display performance summary at the end of training (theme-aware)."""
        self.display.clear_screen()

        accuracy = self.player.accuracy
        rating = self.player.performance_rating
        is_corporate = self.theme_manager.current_theme == StoryTheme.CORPORATE

        # Get theme-specific info
        presentation = self.cert.presentation
        theme_key = self.theme_manager.get_theme_key()
        theme_info = presentation.get('themes', {}).get(theme_key, {})
        victory_message = theme_info.get('victory_message', f'Congratulations on completing {self.cert.name}!')

        # Choose ending based on performance and theme
        if accuracy >= 80:
            if is_corporate:
                print(self.display.render_narrative(
                    f"Outstanding work, {self.player.name}! "
                    f"The board is impressed. You've demonstrated mastery across all modules. "
                    f"{victory_message}",
                    "EXECUTIVE ANNOUNCEMENT"
                ))
            else:
                print(self.display.render_narrative(
                    f"Congratulations, {self.player.name}! "
                    f"You have demonstrated mastery of all domains. "
                    f"{victory_message}",
                    "THE HIGH COUNCIL"
                ))
        elif accuracy >= 60:
            if is_corporate:
                print(self.display.render_narrative(
                    f"Good effort, {self.player.name}. You've completed the training program. "
                    f"Your performance review mentions 'shows potential'. "
                    f"Consider reviewing the modules you struggled with.",
                    "HR PERFORMANCE REVIEW"
                ))
            else:
                print(self.display.render_narrative(
                    f"Well done, {self.player.name}. You have completed your training. "
                    f"Your understanding shows promise, though some areas "
                    f"would benefit from further study.",
                    "THE COUNCIL OF REVIEW"
                ))
        else:
            if is_corporate:
                print(self.display.render_narrative(
                    f"{self.player.name}, we need to talk. "
                    f"Your training scores suggest some gaps. "
                    f"Review the material and consider retaking the training.",
                    "YOUR MANAGER"
                ))
            else:
                print(self.display.render_narrative(
                    f"{self.player.name}, you have walked the halls "
                    f"and faced the trials. While your journey is complete, "
                    f"the knowledge has not yet taken root. "
                    f"Return to your studies and attempt the trials again.",
                    "THE MENTORS"
                ))

        # Performance Summary
        print("\n  " + "=" * 60)
        print("  TRAINING PERFORMANCE SUMMARY")
        print("  " + "=" * 60)
        print(f"\n  Name: {self.player.name}")
        print(f"  Certification: {self.cert.name}")
        theme_key = self.theme_manager.get_theme_key()
        title = self.player.get_title_for_theme(theme_key)
        print(f"  Final Title: {title}")
        print(f"\n  Total XP Earned: {self.player.xp}")
        print(f"  Correct Answers: {self.player.correct_answers}")
        print(f"  Incorrect Answers: {self.player.wrong_answers}")
        print(f"  Overall Accuracy: {accuracy:.1f}%")
        print(f"  Performance Rating: {rating}")

        # Per-domain breakdown
        print("\n  " + "-" * 60)
        print("  DOMAIN BREAKDOWN")
        print("  " + "-" * 60)

        domain_names = {d['id']: d.get('short_name', d['name']) for d in self.cert.domains}

        weak_domains = []
        for domain in range(1, self.domain_count + 1):
            if domain not in self.player.domain_stats:
                continue
            stats = self.player.domain_stats[domain]
            total = stats["correct"] + stats["wrong"]
            if total > 0:
                dom_accuracy = (stats["correct"] / total) * 100
                status = "✓" if dom_accuracy >= 75 else "✗"
                dom_name = domain_names.get(domain, f'Domain {domain}')[:22]
                print(f"  {status} Domain {domain}: {dom_name:<22} "
                      f"{stats['correct']:>2}/{total:<2} ({dom_accuracy:>5.1f}%)")
                if dom_accuracy < 75:
                    weak_domains.append((domain, domain_names.get(domain, f'Domain {domain}'), dom_accuracy))

        print("\n  " + "=" * 60)

        # Exam Readiness Guidance
        print(f"\n  {self.cert.name} EXAM READINESS")
        print("  " + "-" * 60)

        if accuracy >= 90:
            print("  ★ STRONG CANDIDATE")
            print("  You've demonstrated excellent mastery across all domains.")
            print("  Consider scheduling your exam soon while the material is fresh.")
        elif accuracy >= 80:
            print("  ◆ GOOD FOUNDATION")
            print("  You have a solid understanding of the concepts.")
            if weak_domains:
                print("  Focus additional study on these domains:")
                for d_num, d_name, d_acc in weak_domains:
                    print(f"    - Domain {d_num}: {d_name} ({d_acc:.1f}%)")
        elif accuracy >= 70:
            print("  ◇ MORE STUDY NEEDED")
            print("  You're building a foundation, but need more preparation.")
            if weak_domains:
                print("  Prioritize these domains in your study plan:")
                for d_num, d_name, d_acc in weak_domains:
                    print(f"    - Domain {d_num}: {d_name} ({d_acc:.1f}%)")
        else:
            print("  ○ ADDITIONAL PREPARATION RECOMMENDED")
            print("  Consider additional study resources and retake this training.")

        print("\n  " + "=" * 60)
        print()
