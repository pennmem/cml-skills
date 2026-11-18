# cml-skills

Claude Code skills for the Computational Memory Lab. Each top-level directory is one skill. Users clone this repo once and install whichever skills they want into their own `~/.claude/skills/`.

## Skills

| Skill | Purpose |
|---|---|
| [`neurorad-pipeline/`](neurorad-pipeline/) | Navigate, interpret, walk through, and debug the Neurorad iEEG localization pipeline on rhino2. |
| [`grading-assignments/`](grading-assignments/) | Auto-grade COGS 4290 student notebooks against the DataSolutions-BIDS reference answers and explain how the approaches differed. |
| [`peers/`](peers/) | Load, check and analyze the behavioral data of the five PEERS experiments (ltpFR, ltpFR2, VFFR) from the public release, with each experiment's methods and the lab's analysis and figure conventions. |

*(Add new skills as sibling directories. Each one needs a `SKILL.md` at its root — see `skill-creator` if you're writing one.)*

## Installing

Two prerequisites:

- You're on rhino2 (or somewhere Claude Code runs).
- You have Claude Code installed and working.

### Recommended: clone + symlink

```bash
# Clone once anywhere (your home directory works)
git clone https://github.com/pennmem/cml-skills.git ~/cml-skills

# Install every skill
~/cml-skills/install.sh

# Or install just the ones you want
~/cml-skills/install.sh neurorad-pipeline
```

Each skill ends up as a symlink under `~/.claude/skills/`, so a later `git -C ~/cml-skills pull` automatically updates the skills everyone has installed.

### Alternative: copy instead of symlink

```bash
~/cml-skills/install.sh --copy
```

Copies each skill. Changes to the repo after install won't propagate — you'd need to rerun `install.sh --copy` to update. Use this if symlinks cause trouble in your setup.

### What's available

```bash
~/cml-skills/install.sh --list
```

### Dry run

```bash
~/cml-skills/install.sh --dry-run
```

## Canonical checkout on rhino

The lab's blessed copy lives at:

```
/home2/RAM_maint/cml-skills/
```

Shared accounts (`RAM_maint`, `sudas`) can symlink from there into their own `~/.claude/skills/`. For users on their own accounts, cloning from GitHub into `~/cml-skills/` is usually simpler.

## Verifying a skill is loaded

Start a new Claude Code session and ask:

> *what skills do you have available?*

Claude should list `neurorad-pipeline` (and any others you installed). If it doesn't, check:

```bash
ls -la ~/.claude/skills/
```

Each entry should point at a directory containing a `SKILL.md` file.

## Contributing a new skill

1. Create a new top-level directory with a kebab-case name (e.g., `event-creation/`).
2. Put a `SKILL.md` at its root with YAML frontmatter (`name:` + `description:`).
3. Put reference docs under `references/`, assets under `assets/`, executable helpers under `scripts/`.
4. Open a PR. Include a few test prompts in `<skill>/evals/evals.json` so reviewers know what the skill is supposed to handle.

The `skill-creator` skill (in `/mnt/skills/examples/skill-creator/` inside Claude Code) has more guidance on the anatomy of a skill and how to test it.

## Repo conventions

- Skill directory name == `name:` in SKILL.md frontmatter.
- Paths in skill docs that refer to rhino (e.g. `/data10/RAM/subjects/`) are real on-server paths, not placeholders.
- Wiki content preserved from legacy sources is converted to clean Markdown in each skill's `references/`.
