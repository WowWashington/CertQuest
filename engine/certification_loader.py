"""
Dynamic certification loader for the CertQuest framework.

Discovers and loads certification packs from the certifications/ folder.
Each certification is self-contained with config, scenarios, and optional assets.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class CertificationConfig:
    """Holds all configuration for a single certification."""
    id: str
    name: str
    full_name: str
    organization: str
    domain_count: int
    domains: List[Dict]                    # List of domain definitions
    scenarios: Dict[int, List[Dict]]       # domain_id -> list of scenario dicts
    presentation: Dict                     # Theme-specific titles, terms
    scoring: Dict                          # XP, HP, titles configuration
    intros: Optional[Dict] = None          # Domain introductions (if provided)
    art: Optional[Dict] = None             # Custom ASCII art (if provided)

    def get_domain_name(self, domain_id: int) -> str:
        """Get the name of a domain by ID."""
        for domain in self.domains:
            if domain['id'] == domain_id:
                return domain.get('name', f'Domain {domain_id}')
        return f'Domain {domain_id}'

    def get_domain_short_name(self, domain_id: int) -> str:
        """Get the short name of a domain by ID."""
        for domain in self.domains:
            if domain['id'] == domain_id:
                return domain.get('short_name', domain.get('name', f'Domain {domain_id}'))
        return f'Domain {domain_id}'

    def get_domain_theme_content(self, domain_id: int, theme: str) -> Dict:
        """Get theme-specific content for a domain."""
        for domain in self.domains:
            if domain['id'] == domain_id:
                themes = domain.get('themes', {})
                return themes.get(theme, themes.get('fantasy', {}))
        return {}

    def get_title_for_xp(self, xp: int, theme: str = 'fantasy') -> str:
        """Get the appropriate title for a given XP amount."""
        titles = self.scoring.get('titles', [])
        current_title = "Novice"

        for title_def in sorted(titles, key=lambda t: t.get('threshold', 0)):
            if xp >= title_def.get('threshold', 0):
                current_title = title_def.get(theme, title_def.get('fantasy', 'Unknown'))

        return current_title

    def get_scenarios_for_domain(self, domain_id: int) -> List[Dict]:
        """Get all scenarios for a specific domain."""
        return self.scenarios.get(domain_id, [])


class CertificationLoader:
    """Discovers and loads certification packs."""

    CERTIFICATIONS_DIR = "certifications"

    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent
        self.base_path = Path(base_path)
        self.certs_path = self.base_path / self.CERTIFICATIONS_DIR

    def discover_certifications(self) -> List[Dict[str, str]]:
        """
        Find all available certifications.
        Returns list of {id, name, full_name, organization, path} dicts.
        """
        certifications = []

        if not self.certs_path.exists():
            return certifications

        for item in self.certs_path.iterdir():
            if item.is_dir():
                config_file = item / "config.yaml"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)

                        cert_info = config.get('certification', {})
                        domains_info = config.get('domains', {})

                        certifications.append({
                            'id': cert_info.get('id', item.name),
                            'name': cert_info.get('name', item.name.upper()),
                            'full_name': cert_info.get('full_name', ''),
                            'organization': cert_info.get('organization', ''),
                            'domain_count': domains_info.get('count', 0),
                            'path': str(item)
                        })
                    except Exception as e:
                        print(f"Warning: Could not load {config_file}: {e}")

        return sorted(certifications, key=lambda x: x['name'])

    def load_certification(self, cert_id: str) -> CertificationConfig:
        """
        Fully load a certification by ID.
        Raises FileNotFoundError if not found.
        """
        cert_path = self.certs_path / cert_id
        config_file = cert_path / "config.yaml"

        if not config_file.exists():
            raise FileNotFoundError(f"Certification '{cert_id}' not found at {config_file}")

        # Load main config
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        cert_info = config.get('certification', {})
        domains_config = config.get('domains', {})

        # Load all scenarios
        scenarios = self._load_scenarios(cert_path, domains_config.get('count', 0))

        # Load optional intros
        intros = self._load_optional_yaml(cert_path / "intros.yaml")

        # Load optional custom art
        art = self._load_optional_yaml(cert_path / "art.yaml")

        return CertificationConfig(
            id=cert_info.get('id', cert_id),
            name=cert_info.get('name', cert_id.upper()),
            full_name=cert_info.get('full_name', cert_info.get('name', '')),
            organization=cert_info.get('organization', ''),
            domain_count=domains_config.get('count', 0),
            domains=domains_config.get('list', []),
            scenarios=scenarios,
            presentation=config.get('presentation', {}),
            scoring=config.get('scoring', {}),
            intros=intros,
            art=art
        )

    def _load_scenarios(self, cert_path: Path, domain_count: int) -> Dict[int, List[Dict]]:
        """Load all scenario files for a certification."""
        scenarios: Dict[int, List[Dict]] = {}
        scenarios_path = cert_path / "scenarios"

        if not scenarios_path.exists():
            return scenarios

        # Initialize empty lists for each domain
        for domain_num in range(1, domain_count + 1):
            scenarios[domain_num] = []

        # Try numbered files first (domain_1.yaml, domain_2.yaml, etc.)
        for domain_num in range(1, domain_count + 1):
            domain_file = scenarios_path / f"domain_{domain_num}.yaml"
            if domain_file.exists():
                try:
                    with open(domain_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                    if data and 'scenarios' in data:
                        scenarios[domain_num] = data['scenarios']
                except Exception as e:
                    print(f"Warning: Could not load {domain_file}: {e}")

        # Also check for all.yaml or scenarios.yaml (single file with all scenarios)
        for single_name in ['all.yaml', 'scenarios.yaml']:
            single_file = scenarios_path / single_name
            if single_file.exists():
                try:
                    with open(single_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                    if data and 'scenarios' in data:
                        for scenario in data['scenarios']:
                            domain = scenario.get('domain', 1)
                            if domain not in scenarios:
                                scenarios[domain] = []
                            scenarios[domain].append(scenario)
                except Exception as e:
                    print(f"Warning: Could not load {single_file}: {e}")

        return scenarios

    def _load_optional_yaml(self, filepath: Path) -> Optional[Dict]:
        """Load a YAML file if it exists."""
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Warning: Could not load {filepath}: {e}")
        return None
