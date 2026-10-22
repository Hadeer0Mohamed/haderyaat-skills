# Haderyaat Skills

Skills for [Claude Code](https://claude.com/claude-code).

## Skills

| Skill | What it does |
|---|---|
| [`saudi-dialect`](claude/skills/saudi-dialect/SKILL.md) | Rewrites Arabic content into everyday Saudi colloquial Arabic, with no Egyptian words or grammar leaking in |

### saudi-dialect

Models writing colloquial Arabic tend to drift Egyptian — it dominates the colloquial Arabic in their training data — and they also mirror the dialect of the prompt they were given. Ask for Saudi copy in an Egyptian-worded request and what comes back is usually Egyptian.

The skill works in three layers:

- **`SKILL.md`** — the workflow, built around one rule: the request's dialect is never the output's dialect.
- **`references/egyptian-to-saudi.md`** — the full mapping. Grammar markers (the dropped nun in plural verbs, the `ـش` negation, the `هـ` future, demonstrative placement), vocabulary, phrases, words that are fine in both dialects, and before/after examples. The grammar markers carry the most weight, because they survive word-level substitution.
- **`scripts/check_egyptian.py`** — a checker that turns self-review into a pass/fail instead of a judgement call.

The checker reports at two levels:

- `ERROR` — Egyptian with no innocent reading (`عايز`, `دلوقتي`, `مفيش`). Exits non-zero.
- `WARN` — needs context, because the word is valid Saudi or Modern Standard Arabic in another sense: `هما` (the MSA dual), `قوي` (strong), `خالص` (as in خالص الشكر), `العربية` (the language), `طب` (medicine).

That split is the point. An `ERROR` fails the run, so a false positive there would push the writer to "fix" correct Arabic into slang.

Run it on a file, or on stdin:

```bash
python3 claude/skills/saudi-dialect/scripts/check_egyptian.py path/to/strings.json
echo "النص" | python3 claude/skills/saudi-dialect/scripts/check_egyptian.py
```

## Install

Symlink every skill into `~/.claude/skills`, so updates to this repo apply immediately:

```bash
mkdir -p ~/.claude/skills
for d in claude/skills/*/; do
  ln -sfn "$PWD/$d" ~/.claude/skills/"$(basename "$d")"
done
```

Or copy a single skill:

```bash
cp -r claude/skills/saudi-dialect ~/.claude/skills/
```

## Tests

`saudi-dialect` ships a regression suite for its checker:

```bash
python3 claude/skills/saudi-dialect/tests/run.py
```

Two fixture files drive it:

- `should_flag.txt` — Egyptian lines that must raise at least one `ERROR` (recall)
- `should_pass.txt` — clean Saudi and MSA lines that must raise none (precision)

When you catch a leak the checker missed, or see it reject correct Arabic, add that line to the matching file **before** changing any pattern. The suite is what stops a new rule from quietly breaking an old one.

## Layout

```
claude/
└── skills/
    └── <skill-name>/
        ├── SKILL.md      # instructions, always loaded (required)
        ├── references/   # detail Claude reads only when it needs it
        ├── scripts/      # helper scripts
        └── tests/        # tests for those scripts (optional)
```

## Adding a skill

1. Create `claude/skills/<skill-name>/`.
2. Add a `SKILL.md` with `name` and `description` in its frontmatter. The description is what decides when the skill triggers, so spell out the cases it covers.
3. Add it to the table above.
4. Re-run the symlink command.
