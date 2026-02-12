# How To Create More Quiz Topics for CertQuest

This guide explains how to use AI (Claude, ChatGPT, Gemini, Copilot, etc.) to generate new certification quiz packs for CertQuest.

## Overview

CertQuest uses a simple folder structure with YAML files. To add a new certification:

1. Create a folder in `/certifications/your-cert-name/`
2. Add `config.yaml` (certification metadata and domains)
3. Add `scenarios/domain_N.yaml` files (the actual questions)
4. Optionally add `intros.yaml` (educational introductions per domain)

You can generate all of these using the AI prompt below.

---

## 📁 USE THE TEMPLATE FOLDER

**Before using an AI to generate content, look at the `_template` folder!**

The `certifications/_template/` folder contains working, commented example files:

```
certifications/_template/
├── README.md              # Quick start instructions
├── config.yaml            # ✅ Complete config with ALL required sections
├── intros.yaml            # Optional domain introductions
└── scenarios/
    └── domain_1.yaml      # ✅ Example scenarios with correct format
```

### How to Use the Templates

**Option 1: Copy and Edit Manually**
1. Copy the `_template` folder
2. Rename it to your certification ID (e.g., `az-900`)
3. Edit the files with your content

**Option 2: Give Templates to Your AI**
When asking an AI to generate content, **paste the template files into your prompt**:

```
I need you to generate a CertQuest certification pack.

CRITICAL: You MUST follow this EXACT format. Do NOT invent custom fields.
Copy the structure exactly - only change the values.

Here is the required config.yaml format:
[Paste contents of _template/config.yaml]

Here is the required scenario format:
[Paste contents of _template/scenarios/domain_1.yaml]

Now generate content for: [Your certification topic]
- Certification ID: [your-cert-id]
- Number of domains: [N]
- Questions per domain: [X]
- Theme: standard
```

**Why this matters:** AI models often invent their own YAML schemas instead of following yours. By providing the exact templates, you ensure the AI produces compatible output.

---

## ⚠️ REQUIRED SCHEMA - READ THIS FIRST ⚠️

**CertQuest will NOT recognize your certification unless `config.yaml` follows this EXACT structure.**

The loader specifically looks for these required sections. Do NOT use custom field names like `question_file`, `theme_file`, `settings`, or `metadata` - they will be ignored.

### Minimum Required config.yaml Structure

```yaml
# REQUIRED: certification section
certification:
  id: your-cert-id          # lowercase, no spaces (used as folder name)
  name: "Display Name"      # Short name shown in menus
  full_name: "Full Certification Name"
  organization: "Issuing Organization"

# REQUIRED: domains section
domains:
  count: 1                  # Number of domains (must be >= 1)
  list:
    - id: 1
      name: "Domain Name"
      short_name: "Short Name"
      themes:
        standard:           # Must match a key in presentation.themes
          title: "DOMAIN TITLE"
          subtitle: "Optional subtitle"

# REQUIRED: presentation section with at least one theme
presentation:
  themes:
    standard:               # Theme key (use any name: standard, fantasy, corporate, etc.)
      display_name: "Standard"
      game_title: "Your Quiz Title"
      player_term: "Player"
      narrator: "NARRATOR"

# REQUIRED: scoring section
scoring:
  scenarios_per_domain: 10
  xp_per_correct: 50
  hp_penalty_wrong: 20
  max_hp: 100
  starting_hp: 100
  titles:
    - threshold: 0
      standard: "Beginner"  # Must match theme keys
    - threshold: 250
      standard: "Intermediate"
    - threshold: 500
      standard: "Expert"
```

### Required Folder Structure

```
certifications/
└── your-cert-id/           # Folder name should match certification.id
    ├── config.yaml         # REQUIRED - must follow schema above
    ├── intros.yaml         # Optional - domain introductions
    └── scenarios/          # REQUIRED folder
        ├── domain_1.yaml   # Questions for domain 1
        ├── domain_2.yaml   # Questions for domain 2 (if count >= 2)
        └── ...
```

### What Will NOT Work

```yaml
# ❌ WRONG - These fields are NOT recognized:
certification:
  question_file: "questions.yaml"    # NOT SUPPORTED
  theme_file: "themes.yaml"          # NOT SUPPORTED
  settings:                          # NOT SUPPORTED
    total_questions: 5
  metadata:                          # NOT SUPPORTED
    difficulty: "Hard"

# ❌ WRONG - Missing required sections:
certification:
  id: my-cert
  name: "My Cert"
# Missing: domains, presentation, scoring sections!

# ❌ WRONG - domains.count is 0 or missing:
domains:
  list:
    - id: 1
      name: "Domain 1"
# Missing: count field!
```

---

## Flexible Theme System

CertQuest supports **one or more themes** per certification. You're not limited to "fantasy" and "corporate" - you can create any themes you want!

### Single Theme Example
For a straightforward training experience:
```yaml
presentation:
  themes:
    standard:
      display_name: "Standard Training"
      game_title: "AWS Cloud Practitioner Training"
      player_term: "Learner"
      narrator: "INSTRUCTOR"
```

### Multiple Themes Example
For variety and engagement:
```yaml
presentation:
  themes:
    fantasy:
      display_name: "Medieval Fantasy"
      game_title: "The Cloud Kingdom"
      player_term: "Apprentice"
      narrator: "THE ARCHMAGE"

    corporate:
      display_name: "Corporate Office"
      game_title: "Cloud Corp Training"
      player_term: "Employee"
      narrator: "HR DEPARTMENT"

    military:
      display_name: "Military Operations"
      game_title: "Cyber Command Academy"
      player_term: "Recruit"
      narrator: "COMMANDING OFFICER"

    scifi:
      display_name: "Science Fiction"
      game_title: "Starship Systems Training"
      player_term: "Cadet"
      narrator: "SHIP AI"
```

### Theme Behavior
- **One theme**: Auto-selected, no menu shown
- **Multiple themes**: User chooses at startup, can switch with `0` during play
- **Scenarios**: Must include content for each theme defined in config

---

## Step-by-Step Instructions

### Step 1: Copy the Prompt

Copy the entire prompt from the [Generic Quiz Generation Prompt](#generic-quiz-generation-prompt) section below.

### Step 2: Customize the Prompt

Before sending to your AI, fill in these placeholders at the top:
- `[CERTIFICATION_NAME]` - e.g., "AZ-900", "CompTIA Security+", "AWS Cloud Practitioner"
- `[FULL_NAME]` - e.g., "Microsoft Azure Fundamentals"
- `[ORGANIZATION]` - e.g., "Microsoft", "CompTIA", "AWS"
- `[NUMBER_OF_DOMAINS]` - How many domains/sections the cert has
- `[DOMAIN_LIST]` - List each domain name

### Step 3: Generate in Batches

For certifications with many domains, generate in batches:
1. First, ask for `config.yaml` and `intros.yaml`
2. Then ask for scenarios domain by domain: "Now generate domain_1.yaml with 18 scenarios"
3. Continue until all domains are complete

### Step 4: Save the Files

Save the generated YAML files to:
```
CertQuest/
└── certifications/
    └── your-cert-name/
        ├── config.yaml
        ├── intros.yaml
        └── scenarios/
            ├── domain_1.yaml
            ├── domain_2.yaml
            └── ...
```

### Step 5: Test

Run CertQuest and verify your new certification appears in the menu:
```bash
python main.py
```

---

## Generic Quiz Generation Prompt

Copy everything below the line and customize the variables at the top:

---

```
# =============================================================================
# CERTQUEST QUIZ GENERATION PROMPT
# =============================================================================
#
# INSTRUCTIONS FOR THE HUMAN:
# 1. Replace the variables below with your certification details
# 2. Send this entire prompt to Claude, ChatGPT, Gemini, or any AI
# 3. The AI will generate YAML files for CertQuest
# 4. For large certifications, ask for one domain at a time
#
# VARIABLES TO CUSTOMIZE:
# =============================================================================

CERTIFICATION_ID: [SHORT_ID]           # e.g., "az-900", "security-plus", "aws-ccp"
CERTIFICATION_NAME: [CERTIFICATION_NAME]    # e.g., "AZ-900", "Security+", "AWS-CCP"
FULL_NAME: [FULL_NAME]                 # e.g., "Microsoft Azure Fundamentals"
ORGANIZATION: [ORGANIZATION]           # e.g., "Microsoft", "CompTIA", "AWS"
NUMBER_OF_DOMAINS: [NUMBER]            # e.g., 6
SCENARIOS_PER_DOMAIN: [NUMBER]         # Recommended: 15-20

DOMAIN_LIST:
1. [Domain 1 Name]
2. [Domain 2 Name]
3. [Domain 3 Name]
# ... add more as needed

# THEMES (customize as desired - you can have 1, 2, or more themes)
# Each theme needs a key (lowercase, no spaces) and display settings
THEMES:
- key: fantasy
  display_name: "Medieval Fantasy"
  description: "Ancient scrolls and magical wards"
- key: corporate
  display_name: "Corporate Office"
  description: "Office life and IT departments"
# Add more themes if desired:
# - key: military
#   display_name: "Military Operations"
#   description: "Cyber command training"
# - key: scifi
#   display_name: "Science Fiction"
#   description: "Starship systems and AI"

# =============================================================================
# PROMPT STARTS HERE - DO NOT MODIFY BELOW THIS LINE
# =============================================================================

You are an expert certification exam content creator. Generate quiz content for the CertQuest training framework in YAML format.

## Your Task

Create training scenarios for the certification specified above. Each scenario should:
1. Test a real concept from the official exam objectives
2. Present a realistic situation requiring applied knowledge
3. Have exactly 4 answer choices with only ONE correct answer
4. Include detailed explanations for why the correct answer is right
5. Include explanations for why each wrong answer is incorrect
6. Be available in ALL themes listed above (each scenario needs content for every theme)

## Output Format

### File 1: config.yaml

```yaml
certification:
  id: [CERTIFICATION_ID from above]
  name: "[CERTIFICATION_NAME]"
  full_name: "[FULL_NAME]"
  organization: "[ORGANIZATION]"
  version: "2024"

presentation:
  themes:
    fantasy:
      game_title: "[Creative fantasy title for this cert]"
      subtitle: "A [CERTIFICATION_NAME] Training Adventure"
      player_term: "Seeker"
      domain_term: "Domain"
      narrator: "THE ANCIENT ARCHIVE"
      victory_message: "[Fantasy-themed victory message mentioning the cert]"

    corporate:
      game_title: "[Creative corporate title for this cert]"
      subtitle: "A [CERTIFICATION_NAME] Training Experience"
      player_term: "Employee"
      domain_term: "Module"
      narrator: "TRAINING DEPARTMENT"
      victory_message: "[Corporate-themed victory message mentioning the cert]"

domains:
  count: [NUMBER_OF_DOMAINS]

  list:
    - id: 1
      name: "[Domain 1 full name]"
      short_name: "[Domain 1 abbreviated]"
      themes:
        fantasy:
          title: "[CREATIVE FANTASY DOMAIN TITLE IN CAPS]"
          subtitle: "[Thematic subtitle]"
        corporate:
          title: "[CREATIVE CORPORATE DOMAIN TITLE IN CAPS]"
          subtitle: "[Business-appropriate subtitle]"
    # Repeat for each domain...

scoring:
  scenarios_per_domain: [SCENARIOS_PER_DOMAIN]
  xp_per_correct: 50
  hp_penalty_wrong: 20
  max_hp: 100
  starting_hp: 100

  titles:
    - threshold: 0
      fantasy: "Novice Apprentice"
      corporate: "New Hire"
    - threshold: [Calculate: total_scenarios * 50 * 0.1]
      fantasy: "[Progressive fantasy title]"
      corporate: "[Progressive corporate title]"
    # Add 6-8 progressive titles up to max XP

performance:
  excellent: 80
  passing: 60
```

### File 2: intros.yaml

```yaml
1:
  fantasy:
    narrator: "THE ANCIENT ARCHIVE"
    introduction: |
      [2-3 paragraphs introducing Domain 1 concepts in fantasy theme]
      [Mention key topics that will be covered]
      [Set the scene for the trials ahead]
  corporate:
    narrator: "TRAINING COORDINATOR"
    introduction: |
      [2-3 paragraphs introducing Domain 1 concepts in corporate theme]
      [Mention key topics in business context]
      [Prepare for the training modules]

# Repeat for each domain...
```

### File 3+: scenarios/domain_N.yaml (one per domain)

```yaml
domain: [N]
domain_name: "[Domain N Name]"

scenarios:
  - id: "d[N]_[short_descriptive_id]"
    domain: [N]
    correct_index: [0-3]  # 0-based index of correct answer
    xp_reward: 50
    hp_penalty: 20
    domain_reference: "Domain [N]: [Domain Name] - [Specific Topic]"
    failure_text: |
      [Generic explanation if specific failure text not available]

    themes:
      fantasy:
        title: "[SCENARIO TITLE IN CAPS - FANTASY THEMED]"
        narrative: |
          [3-5 paragraphs setting up the scenario in fantasy theme]
          [Present a situation requiring the certification knowledge]
          [End with a clear question or decision point]

          What do you do?

        choices:
          - text: "[Choice 1 - fantasy themed]"
          - text: "[Choice 2 - fantasy themed]"
          - text: "[Choice 3 - fantasy themed]"
          - text: "[Choice 4 - fantasy themed]"

        success_text: |
          [2-3 paragraphs explaining why this was correct]
          [Reinforce the certification concept]
          [Fantasy-themed positive outcome]

        failure_texts:
          0: |
            [If choice 0 is wrong: explanation why, in fantasy theme]
          1: |
            [If choice 1 is wrong: explanation why, in fantasy theme]
          2: |
            [If choice 2 is wrong: explanation why, in fantasy theme]
          3: |
            [If choice 3 is wrong: explanation why, in fantasy theme]
          # Only include entries for WRONG answers (not the correct one)

      corporate:
        title: "[SCENARIO TITLE IN CAPS - CORPORATE THEMED]"
        narrative: |
          [Same concept as fantasy, but in corporate/office setting]
          [Use business terminology and situations]

          What's your recommendation?

        choices:
          - text: "[Choice 1 - corporate themed]"
          - text: "[Choice 2 - corporate themed]"
          - text: "[Choice 3 - corporate themed]"
          - text: "[Choice 4 - corporate themed]"

        success_text: |
          [Corporate-themed success explanation]

        failure_texts:
          # Same structure as fantasy, corporate themed

  # Continue with more scenarios...
  # Aim for [SCENARIOS_PER_DOMAIN] scenarios per domain
```

## Important Guidelines

1. **Accuracy**: All questions must be based on real certification exam objectives
2. **Difficulty Mix**: Include easy (30%), medium (50%), and hard (20%) questions
3. **Topic Coverage**: Cover all major topics within each domain
4. **Explanations**: Every wrong answer needs a clear explanation of why it's wrong
5. **Theme Consistency**: Fantasy theme uses medieval/magical language; Corporate uses business/office language
6. **Same Correct Answer**: The correct_index must point to the same concept in both themes
7. **No Trick Questions**: Questions should test knowledge, not reading comprehension
8. **Practical Focus**: Prefer scenario-based questions over pure memorization

## Generation Request

Please generate the following files for the certification specified above:

1. First, generate the complete `config.yaml`
2. Then generate `intros.yaml` with introductions for all domains
3. Then I will ask you to generate each `domain_N.yaml` file one at a time

Start with config.yaml now.
```

---

## Example: Generating AZ-900 Content

Here's how you would customize the prompt for Azure Fundamentals:

```
CERTIFICATION_ID: az-900
CERTIFICATION_NAME: AZ-900
FULL_NAME: Microsoft Azure Fundamentals
ORGANIZATION: Microsoft
NUMBER_OF_DOMAINS: 6
SCENARIOS_PER_DOMAIN: 15

DOMAIN_LIST:
1. Describe Cloud Concepts (20-25%)
2. Describe Azure Architecture and Services (35-40%)
3. Describe Azure Management and Governance (30-35%)
```

Then send the complete prompt to your AI of choice.

---

## Tips for Best Results

### Breaking Up Large Requests

For better quality, generate content in smaller chunks:

1. **First message**: "Generate config.yaml and intros.yaml"
2. **Second message**: "Now generate domain_1.yaml with 15 scenarios covering [list key topics]"
3. **Continue**: One domain at a time until complete

### Reviewing Generated Content

Before using generated content:

1. **Verify accuracy**: Check that answers align with official exam objectives
2. **Test the YAML**: Run `python -c "import yaml; yaml.safe_load(open('file.yaml'))"` to validate syntax
3. **Play test**: Run through scenarios to ensure they make sense
4. **Adjust difficulty**: Modify if too easy or too hard

### Common Issues

| Issue | Solution |
|-------|----------|
| YAML syntax error | Check for proper indentation (2 spaces), quote strings with colons |
| correct_index wrong | Remember it's 0-based (0, 1, 2, or 3) |
| Missing failure_texts | Add explanations for all wrong answers |
| Theme mismatch | Ensure both themes test the same concept |

---

## Contributing Back

If you create a high-quality certification pack, consider contributing it back to the CertQuest repository! Submit a pull request with your certification folder.

---

---

## Troubleshooting

### Certification Not Appearing in Menu

If your certification doesn't show up when you run `python main.py`:

1. **Check for `config.yaml`** - Must exist at `certifications/your-cert/config.yaml`
2. **Verify required sections** - Must have: `certification`, `domains`, `presentation`, `scoring`
3. **Check `domains.count`** - Must be >= 1, not 0 or missing
4. **Check theme consistency** - Theme keys in `presentation.themes` must match keys used in `domains.list[].themes`

**Debug command:**
```bash
python -c "import yaml; print(yaml.safe_load(open('certifications/your-cert/config.yaml')))"
```

### "1-0" in Domain Selection Prompt

This means `domains.count` is 0 or missing. Add:
```yaml
domains:
  count: 1   # Must be >= 1
```

### LLM Generated Wrong Format

If an AI (Gemini, ChatGPT, etc.) generates a config that doesn't work:

1. The AI likely invented its own schema instead of following CertQuest's
2. **Use the `_template` folder** - Copy `certifications/_template/config.yaml` and paste it into your AI prompt
3. Tell the AI: "Use this EXACT format. Do NOT add custom fields. Only change the values."
4. Or manually copy `_template` folder and edit the files directly

**Common AI mistakes to watch for:**
- Adding `question_file`, `theme_file`, `settings`, `metadata`, `logic`, `files` fields (NOT SUPPORTED)
- Missing the `domains` section entirely
- Missing `domains.count` field
- Putting scenarios in wrong location (should be in `scenarios/domain_1.yaml`)

### YAML Syntax Errors

```bash
# Validate YAML syntax:
python -c "import yaml; yaml.safe_load(open('your-file.yaml'))"
```

Common issues:
- Missing spaces after colons: `name:"value"` → `name: "value"`
- Inconsistent indentation: Use 2 spaces, not tabs
- Unquoted special characters: Quote strings containing `: # [ ] { }`

---

## Questions?

Open an issue on the [CertQuest GitHub repository](https://github.com/WowWashington/CertQuest) if you need help.
