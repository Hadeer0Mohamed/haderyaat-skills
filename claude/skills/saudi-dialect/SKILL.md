---
name: saudi-dialect
description: Convert any Arabic content (Modern Standard Arabic, Egyptian, Levantine, or mixed) into natural everyday Saudi colloquial Arabic (اللهجة السعودية الدارجة) with zero Egyptian words or grammar. Use this skill whenever the user asks to rewrite, translate, localize, or "سعودة" text into Saudi dialect — e.g. "حوله سعودي", "اكتبه باللهجة السعودية", "خليه سعودي", "localize for KSA", "Saudi copy", UI strings/i18n files for a Saudi audience, marketing copy, social posts, scripts, or chatbot replies for Saudi users. Trigger even when the request itself is written in Egyptian Arabic — the request language never affects the output dialect.
---

# Saudi Dialect Converter (تحويل للهجة السعودية)

Turn Arabic content into the kind of Saudi Arabic people actually speak and write day to day in the Kingdom (WhatsApp, X, ads, app UI), with **no Egyptian leakage at all**.

## The core rule: the request's dialect is not the output's dialect

Users often write their instructions in Egyptian Arabic (e.g. "عايزك تحول الكلام ده"). That is just *how they talk to you*. It must never bleed into the output. Egyptian words are the single most common failure here, because the model mirrors the language of the prompt. Actively resist that mirroring: read the request, understand it, then write the result as if a Saudi native wrote it from scratch.

This applies to everything you produce while using this skill: the converted content, and any short note you add around it. Keep notes minimal, and write them in Saudi dialect or neutral MSA, never Egyptian.

## Target dialect

Default to **"white" Saudi** (سعودي أبيض): the general, widely understood Saudi register used in Saudi ads, apps and social media. It leans Najdi/central but avoids heavy Bedouin or very local words so anyone in the Kingdom reads it naturally.

- If the user explicitly asks for Hijazi (حجازي) or Najdi (نجدي) specifically, lean that way, but the no-Egyptian rule still holds. Hijazi shares a few features with Egyptian (e.g. the "بـ" present prefix); still prefer the Saudi-only forms listed in the reference file.
- Keep the meaning, intent, tone and level of formality of the source. A formal source becomes polite Saudi, not slangy Saudi. A playful source stays playful.

## Workflow

1. **Separate instructions from content.** Identify exactly which text needs converting. The instruction wrapper (in whatever dialect) is not content.
2. **Understand the meaning** of each sentence first, then re-express it the way a Saudi would say it. Do not do word-by-word substitution — rebuild the sentence with Saudi structure and rhythm.
3. **Apply the reference.** Read `references/egyptian-to-saudi.md` for the full mapping of Egyptian markers → Saudi equivalents, verb conjugation rules, and examples. Read it every time; small grammar markers (future هـ, the ـوا plural ending, ده/دي) are what give Egyptian away.
4. **Self-check before answering.** Scan your draft for every Egyptian marker in the reference list. If the content is in a file, run the checker:
   ```bash
   python3 <skill-dir>/scripts/check_egyptian.py <file>
   ```
   or pipe text in: `echo "النص" | python3 <skill-dir>/scripts/check_egyptian.py`.
   Fix every `ERROR` — those are Egyptian with no innocent reading. A `WARN` needs your judgement: the word is either valid Saudi in one sense and Egyptian in another ("إيه" = "yes" in Saudi), or plain Modern Standard Arabic that only turns Egyptian in a specific use — "هما" (MSA dual), "قوي" (strong), "خالص" (خالص الشكر), "العربية" (the language), "طب" (medicine). Never "fix" one of those into slang just because it was flagged.
5. **Deliver** only the converted content unless the user asked for more (explanations, alternatives, a glossary).

## Working with files and code (Claude Code)

When converting UI strings, i18n JSON/YAML, Vue/React templates, markdown, subtitles, etc.:

- Convert only human-readable string values. Never touch keys, variable names, code, URLs, CSS classes, or file structure.
- Preserve placeholders and interpolation exactly: `{name}`, `{{ count }}`, `%s`, `:attr`, `<b>…</b>`, `\n`, ICU plural syntax. You may move a placeholder within the sentence if Saudi word order needs it.
- Keep string length reasonable for UI (buttons, labels). Short UI labels often stay in neutral MSA ("حفظ", "إلغاء", "تسجيل الدخول") — that is fine and natural in Saudi apps; don't force slang onto a button.
- Keep numbers, brand names, and English technical terms as they are unless asked.
- After editing, run the checker on the changed file(s).

## Maintaining the checker

`tests/` is the checker's regression suite: `should_flag.txt` (Egyptian lines that must raise an `ERROR`) and `should_pass.txt` (clean Saudi/MSA lines that must not). Run it with:

```bash
python3 <skill-dir>/tests/run.py
```

When you catch a leak the checker missed, or see it reject correct Arabic, add that line to the matching file before changing any pattern — the suite is what keeps new rules from breaking old ones.

## Quick reference (the most common leaks)

| Egyptian ❌ | Saudi ✅ |
|---|---|
| عايز / عاوز | أبغى / أبي |
| إزاي | كيف |
| إيه (what) | وش / إيش |
| ده / دي / دول | هذا / هذي / هذولا |
| دلوقتي | الحين |
| كده | كذا |
| مش | مو / ما |
| أوي / قوي | مرة / حيل / واجد |
| فين | وين |
| ليه | ليش |
| إمتى | متى |
| لسه | للحين / توه |
| هعمل (future هـ) | بسوي / راح أسوي |
| بيعمل (present بـ) | يسوي / قاعد يسوي |
| بتاعي | حقي |
| حاجة | شي |
| عملوا / بيقولوا | سووا / يقولون |
| معلش | معليش / ولا يهمك |

The full list, grammar rules, and before/after examples are in `references/egyptian-to-saudi.md`.
