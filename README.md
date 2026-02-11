# CertQuest

**A modular multi-certification training framework with scenario-based challenges.**

## What It Is

CertQuest is a text-based adventure game framework that transforms dry certification study material into engaging, narrative-driven scenarios. Add new certifications by simply dropping a folder into `/certifications/` - no code changes required.

## Features

- **Modular Design**: Add new certifications without modifying the engine
- **Dual Themes**: Each scenario available in Medieval Fantasy or Corporate Office style
- **Dynamic Loading**: Certifications discovered automatically at startup
- **Detailed Feedback**: Explanations for both correct and incorrect answers
- **Progress Tracking**: XP, HP, and per-domain statistics
- **Exam Readiness**: Performance summary with study recommendations

## Quick Start

```bash
git clone https://github.com/WowWashington/CertQuest.git
cd CertQuest
pip install -r requirements.txt
python main.py
```

**Windows users:** Just double-click `play.bat`

## Requirements

- Python 3.6 or higher
- PyYAML (`pip install pyyaml`)
- Optional: colorama for colored output (`pip install colorama`)

## Included Certifications

### CISSP (Certified Information Systems Security Professional)
- **144 scenarios** across 8 domains
- Aligned with (ISC)² CISSP CBK
- Dual theme support (Fantasy/Corporate)

## Adding New Certifications

Create a folder in `/certifications/` with:

```
certifications/
└── your-cert/
    ├── config.yaml      # Certification metadata + domains
    ├── scenarios/       # Question files
    │   ├── domain_1.yaml
    │   ├── domain_2.yaml
    │   └── ...
    └── intros.yaml      # Optional: domain introductions
```

### config.yaml Structure

```yaml
certification:
  id: your-cert
  name: "Your Certification"
  full_name: "Full Certification Name"
  organization: "Certifying Body"

domains:
  count: 6
  list:
    - id: 1
      name: "Domain One"
      short_name: "Domain 1"
      themes:
        fantasy:
          title: "THE FANTASY TITLE"
        corporate:
          title: "THE CORPORATE TITLE"
    # ... more domains

scoring:
  scenarios_per_domain: 10
  xp_per_correct: 50
  hp_penalty_wrong: 20
  titles:
    - threshold: 0
      fantasy: "Novice"
      corporate: "New Hire"
    # ... more titles
```

### Scenario File Structure (domain_N.yaml)

```yaml
domain: 1
scenarios:
  - id: unique_scenario_id
    correct_index: 0  # 0-based
    xp_reward: 50
    hp_penalty: 20
    domain_reference: "Domain 1 - Topic"
    themes:
      fantasy:
        title: "SCENARIO TITLE"
        narrative: |
          The scenario description...
        choices:
          - text: "First choice (correct)"
          - text: "Second choice"
          - text: "Third choice"
          - text: "Fourth choice"
        success_text: |
          Explanation of why this was correct...
        failure_texts:
          1: "Why choice 2 was wrong..."
          2: "Why choice 3 was wrong..."
          3: "Why choice 4 was wrong..."
      corporate:
        title: "CORPORATE SCENARIO TITLE"
        # ... same structure
```

## Commands During Gameplay

| Command | Action |
|---------|--------|
| `1-4` | Select a numbered choice |
| `0` or `C` | Switch story theme |
| `help` | Show help message |
| `status` | Show your current stats |
| `quit` | End your session |

## Project Structure

```
CertQuest/
├── main.py                 # Entry point
├── engine/                 # Certification-agnostic game engine
│   ├── certification_loader.py
│   ├── game.py
│   ├── player.py
│   ├── display.py
│   ├── input_handler.py
│   └── theme_manager.py
├── certifications/         # Drop-in certification packs
│   └── cissp/
└── tools/                  # Utility scripts
```

## License

MIT License - Feel free to use, modify, and share.

---

**Learn certifications. Have fun. Pass the exam.**
