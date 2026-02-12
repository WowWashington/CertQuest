# CertQuest Certification Template

This folder contains templates for creating new certification quiz packs.

## Quick Start

1. **Copy this folder** - Rename the copy to your certification ID (lowercase, no spaces)
   ```
   certifications/
   ├── _template/     ← This folder
   └── my-cert/       ← Your new certification
   ```

2. **Edit `config.yaml`** - Update certification details, domains, themes, and scoring

3. **Edit `scenarios/domain_1.yaml`** - Add your questions

4. **Test** - Run `python main.py` and select your certification

## Required Files

| File | Required | Purpose |
|------|----------|---------|
| `config.yaml` | ✅ YES | Certification metadata, domains, themes, scoring |
| `scenarios/domain_N.yaml` | ✅ YES | Questions for each domain (N = 1, 2, 3...) |
| `intros.yaml` | ❌ Optional | Educational introductions for each domain |

## Using AI to Generate Content

Copy the contents of these template files into your AI prompt:

```
I need you to generate quiz content for CertQuest. Here is the EXACT format required:

[Paste config.yaml template]

[Paste domain_1.yaml template]

Now generate content for: [Your certification topic]
- Number of domains: [N]
- Questions per domain: [X]
- Themes: [standard / fantasy / corporate / etc.]
```

**Important:** Tell the AI to follow the template EXACTLY. Do not let it invent its own format.

## Common Mistakes

❌ **Wrong:** Custom fields like `question_file`, `settings`, `metadata`, `logic`
✅ **Right:** Use only `certification`, `domains`, `presentation`, `scoring`

❌ **Wrong:** Missing `domains.count` or setting it to 0
✅ **Right:** `domains.count` must be >= 1

❌ **Wrong:** Theme key mismatch between config and scenarios
✅ **Right:** If config has `themes.standard`, scenarios need `themes.standard`

❌ **Wrong:** Putting questions in root folder as `questions.yaml`
✅ **Right:** Put questions in `scenarios/domain_1.yaml`

## File Structure Reference

```
your-cert/
├── config.yaml              # Required: metadata + domains + themes + scoring
├── intros.yaml              # Optional: domain introductions
└── scenarios/
    ├── domain_1.yaml        # Required: questions for domain 1
    ├── domain_2.yaml        # Required if domains.count >= 2
    └── domain_N.yaml        # One file per domain
```
