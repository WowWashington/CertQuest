#!/usr/bin/env python3
"""
Convert CISSP-EightDomains Python scenarios to CertQuest YAML format.

Run this script from the CertQuest directory with the path to the CISSP project:
    python tools/convert_from_cissp.py /path/to/CISSP-EightDomains
"""

import sys
import os
import yaml

# Add the CISSP project to path for imports
def convert_scenarios(cissp_path: str, output_path: str):
    """Convert all CISSP scenarios to YAML format."""

    sys.path.insert(0, cissp_path)

    # Import scenario data
    from scenarios.domain1_security_risk import DOMAIN_1_SCENARIOS
    from scenarios.domain2_asset_security import DOMAIN_2_SCENARIOS
    from scenarios.domain3_security_architecture import DOMAIN_3_SCENARIOS
    from scenarios.domain4_communication_network import DOMAIN_4_SCENARIOS
    from scenarios.domain5_identity_access import DOMAIN_5_SCENARIOS
    from scenarios.domain6_assessment_testing import DOMAIN_6_SCENARIOS
    from scenarios.domain7_security_operations import DOMAIN_7_SCENARIOS
    from scenarios.domain8_software_development import DOMAIN_8_SCENARIOS

    all_domains = [
        (1, DOMAIN_1_SCENARIOS),
        (2, DOMAIN_2_SCENARIOS),
        (3, DOMAIN_3_SCENARIOS),
        (4, DOMAIN_4_SCENARIOS),
        (5, DOMAIN_5_SCENARIOS),
        (6, DOMAIN_6_SCENARIOS),
        (7, DOMAIN_7_SCENARIOS),
        (8, DOMAIN_8_SCENARIOS),
    ]

    domain_names = {
        1: "Security and Risk Management",
        2: "Asset Security",
        3: "Security Architecture and Engineering",
        4: "Communication and Network Security",
        5: "Identity and Access Management",
        6: "Security Assessment and Testing",
        7: "Security Operations",
        8: "Software Development Security"
    }

    os.makedirs(output_path, exist_ok=True)

    for domain_num, scenarios in all_domains:
        yaml_scenarios = []

        for scenario in scenarios:
            yaml_scenario = {
                'id': scenario.get('id', f'd{domain_num}_unknown'),
                'domain': domain_num,
                'correct_index': scenario.get('correct_index', 0),
                'xp_reward': scenario.get('xp_reward', 50),
                'hp_penalty': scenario.get('hp_penalty', 20),
                'domain_reference': scenario.get('domain_reference', f'Domain {domain_num}'),
                'failure_text': scenario.get('failure_text', ''),
                'themes': {}
            }

            # Convert themes
            themes = scenario.get('themes', {})
            for theme_name, theme_content in themes.items():
                yaml_theme = {
                    'title': theme_content.get('title', 'SCENARIO'),
                    'narrative': theme_content.get('narrative', ''),
                    'choices': [],
                    'success_text': theme_content.get('success_text', ''),
                    'failure_texts': {}
                }

                # Convert choices
                for choice in theme_content.get('choices', []):
                    if isinstance(choice, dict):
                        yaml_theme['choices'].append({
                            'text': choice.get('text', '')
                        })
                    else:
                        yaml_theme['choices'].append({'text': str(choice)})

                # Convert failure texts
                failure_texts = theme_content.get('failure_texts', {})
                for idx, text in failure_texts.items():
                    yaml_theme['failure_texts'][int(idx)] = text

                yaml_scenario['themes'][theme_name] = yaml_theme

            yaml_scenarios.append(yaml_scenario)

        # Write domain file
        output_file = os.path.join(output_path, f'domain_{domain_num}.yaml')

        yaml_data = {
            'domain': domain_num,
            'domain_name': domain_names[domain_num],
            'scenarios': yaml_scenarios
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=100)

        print(f"Created {output_file} with {len(yaml_scenarios)} scenarios")

    print(f"\nConversion complete! {sum(len(s) for _, s in all_domains)} total scenarios converted.")


def convert_intros(cissp_path: str, output_file: str):
    """Convert domain introductions to YAML."""

    sys.path.insert(0, cissp_path)

    from data.domain_intros import DOMAIN_INTRODUCTIONS

    # Convert to YAML-friendly format
    yaml_intros = {}
    for domain_num, intro_data in DOMAIN_INTRODUCTIONS.items():
        yaml_intros[domain_num] = intro_data

    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_intros, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=100)

    print(f"Created {output_file} with {len(yaml_intros)} domain introductions")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_from_cissp.py /path/to/CISSP-EightDomains")
        sys.exit(1)

    cissp_path = sys.argv[1]

    if not os.path.exists(cissp_path):
        print(f"Error: Path not found: {cissp_path}")
        sys.exit(1)

    # Get the CertQuest directory (parent of tools/)
    certquest_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_scenarios = os.path.join(certquest_dir, "certifications", "cissp", "scenarios")
    output_intros = os.path.join(certquest_dir, "certifications", "cissp", "intros.yaml")

    print("Converting CISSP scenarios to CertQuest YAML format...")
    print(f"Source: {cissp_path}")
    print(f"Output: {output_scenarios}")
    print()

    convert_scenarios(cissp_path, output_scenarios)
    print()
    convert_intros(cissp_path, output_intros)
