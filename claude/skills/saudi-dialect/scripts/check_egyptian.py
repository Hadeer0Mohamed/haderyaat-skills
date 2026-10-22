#!/usr/bin/env python3
"""Scan Arabic text for Egyptian dialect markers.

Usage:
    python3 check_egyptian.py file1 [file2 ...]
    echo "النص" | python3 check_egyptian.py

ERROR = almost certainly Egyptian, must be fixed.
WARN  = could be valid Saudi or MSA depending on meaning; read the context.
Exit code 1 if any ERROR is found.

Rule of thumb for adding a pattern: if the word has ANY common Modern Standard
Arabic meaning, it belongs in WARNS, not ERRORS. An ERROR fails the run, so a
false positive pushes the writer to "fix" correct Arabic.
"""
import re
import sys

AR = "ء-غف-يً-ْٰ-ۓ"  # letters + harakat, not punctuation
# Word boundary for Arabic: not preceded/followed by an Arabic letter.
def w(pattern):
    # optional و/ف conjunction prefix; optional pronoun suffix for verbs/nouns
    return re.compile(rf"(?<![{AR}])(?:و|ف)?(?:{pattern})(?:ك|ه|ها|هم|كم|ني|نا|ين)?(?![{AR}])")

ERRORS = {
    r"عايز|عايزة|عايزين|عاوز|عاوزة|عاوزين": "أبغى / أبي / تبون",
    r"إزاي|ازاي|إزاى|ازاى": "كيف",
    r"دلوقتي|دلوقت|دلوقتى": "الحين",
    r"كده|كدة|كدا": "كذا",
    r"ده|دول": "هذا / هذولا",
    r"مش": "مو / ما",
    r"أوي|اوي|أوى|اوى": "مرة / حيل",
    r"فين": "وين",
    r"إمتى|امتى|إمتي|امتي": "متى",
    r"لسه|لسة": "للحين / توه",
    r"بتاع|بتاعي|بتاعتي|بتاعك|بتاعه|بتاعها|بتاعنا|بتاعهم|بتاعة|بتوع": "حق / حقي",
    r"مفيش|مافيش|ما فيش": "ما فيه",
    r"محدش|ماحدش|محدِش|مُحدش": "محد / ما أحد",
    r"برضو|برضه|برده": "بعد",
    r"علشان": "عشان",
    r"إزيك|ازيك|إزيكم|ازيكم": "كيفك / كيفكم",
    r"النهارده|النهاردة|انهارده": "اليوم",
    r"إمبارح|امبارح": "أمس",
    r"حتة|حته": "مكان",
    r"أوضة|اوضة|أوضه|اوضه": "غرفة",
    r"زهقان|زهقت|زهقانة": "طفشان / طفشت",
    r"جدعان|يا جدع": "يا جماعة / يا رجال",
    r"بص|بصي|بصوا": "شوف / طالع",
    r"ميرسي": "مشكور",
    r"معلش": "معليش",
    r"اللي ايه|ايه ده": "وش هذا",
    r"شغلانة|شغلانه": "شغلة / وظيفة",
    r"بالظبط": "بالضبط",
}

WARNS = {
    r"إيه|ايه|إيه؟|ايه؟": "Egyptian 'what' → وش/إيش ; but إيه = 'yes' in Saudi",
    r"دي": "Egyptian 'this' → هذي",
    r"ليه": "Egyptian 'why' → ليش (له = 'to him')",
    r"حاجة|حاجات": "Egyptian 'thing' → شي/أشياء ; OK if it means 'need'",
    r"كمان": "OK in Hijazi; general Saudi prefers بعد/زيادة",
    r"راجل|الراجل": "رجال / رجّال",
    r"شوية": "شوي is more Saudi",
    r"بكره": "spell it بكرة",
    r"بقى": "Egyptian discourse filler; drop it or use ترى",
    r"أيوه|ايوه": "إيه / إي (أيوا is Hijazi)",
    # --- Valid MSA words that are only Egyptian in one specific sense. ---
    r"هما": "fine as the MSA dual 'they two'; Egyptian 3pl هما → هم",
    r"قوي": "fine as 'strong'; Egyptian intensifier 'very' → مرة / حيل",
    r"خالص": "fine as 'pure/sincere' (خالص الشكر); Egyptian 'not at all' → أبد",
    r"عربية|عربيتي|العربية": "fine as 'Arabic'; Egyptian 'car' → سيارة",
    r"طب": "fine as 'medicine'; Egyptian discourse particle طب → طيب",
    r"لأ": "used in Saudi too; the fuller spelling is لا",
    r"استنى|استني|استنوا|مستني|مستنيك|مستنيكم": "used in Hijazi; general Saudi prefers انتظر / اصبر",
}

# Morphological patterns (noisier): ـش negation, هـ future, بيـ/بتـ present, ـوا plural.
# Each regex keeps the optional و/ف conjunction OUTSIDE group 1, so the skip-list
# below can be checked against the bare word (وهناك -> هناك).
PFX = rf"(?<![{AR}])(?:و|ف)?"
MORPH = [
    (re.compile(rf"{PFX}(ما[{AR}]{{2,}}ش)(?![{AR}])"), "ERROR", "ـش negation → ما + verb"),
    (re.compile(rf"{PFX}((?:بي|بت|بن)[{AR}]{{2,}}وا)(?![{AR}])"), "ERROR", "Egyptian plural present (بيقولوا) → يقولون"),
    # A verb starting with يـ and ending in ـوا is always present/subjunctive, never past,
    # so the dropped nun is unambiguous: يروحوا → يروحون.
    (re.compile(rf"{PFX}(ي[{AR}]{{2,}}وا)(?![{AR}])"), "ERROR", "Egyptian plural present (يروحوا) → يروحون"),
    # تـ/نـ + ـوا is ambiguous: تكلموا/تعاونوا are perfectly good past-tense plurals.
    (re.compile(rf"{PFX}((?:ت|ن)[{AR}]{{2,}}وا)(?![{AR}])"), "WARN", "if present tense (تروحوا) → تروحون ; fine if past (تكلموا)"),
    (re.compile(rf"{PFX}((?:هن|هت|هي|ها)[{AR}]{{2,}})(?![{AR}])"), "WARN", "possible future هـ (هنعمل) → بنسوي / راح"),
    (re.compile(rf"{PFX}(بي[{AR}]{{3,}})(?![{AR}])"), "WARN", "possible present بيـ (بيعمل) → يسوي / قاعد"),
]

# Common legit words that the noisy morph patterns would hit.
MORPH_SKIP = {
    "هناك", "هنا", "هنالك", "هيئة", "هيا", "هاتف", "هاتفك", "هامة", "هام", "هادي", "هادئ",
    "هيك", "هنية", "هيبة", "هيكل", "هاي", "هتاف", "بيت", "بيتك", "بيتي", "بيتنا", "بيانات",
    "بيان", "بيئة", "بين", "بينما", "بيع", "بيضاء", "بيروت", "بيتزا", "بينهم", "بينكم", "بينا",
    "هنيئا", "هنيئاً", "ماشي", "ماش", "هالشي", "هالأشياء", "هاذي",
    # past-tense plurals that happen to start with يـ
    "يئسوا", "يبسوا", "يقظوا", "يتموا", "يسروا",
}

ERR_RX = [(w(p), s) for p, s in ERRORS.items()]
WARN_RX = [(w(p), s) for p, s in WARNS.items()]


def scan(text, label):
    found = 0
    errors = 0
    for ln, line in enumerate(text.splitlines(), 1):
        hits = []
        for rx, sug in ERR_RX:
            for m in rx.finditer(line):
                hits.append(("ERROR", m.group(0), sug))
        for rx, sug in WARN_RX:
            for m in rx.finditer(line):
                hits.append(("WARN", m.group(0), sug))
        for rx, level, sug in MORPH:
            for m in rx.finditer(line):
                if m.group(1) in MORPH_SKIP:
                    continue
                hits.append((level, m.group(0), sug))
        seen = set()
        for level, word, sug in hits:
            if (level, word) in seen:
                continue
            seen.add((level, word))
            found += 1
            errors += level == "ERROR"
            print(f"{label}:{ln}: {level}: '{word}' → {sug}")
    return found, errors


def main():
    total = errs = 0
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            with open(path, encoding="utf-8") as f:
                t, e = scan(f.read(), path)
            total += t; errs += e
    else:
        t, e = scan(sys.stdin.read(), "stdin")
        total += t; errs += e
    if total == 0:
        print("✅ No Egyptian markers found.")
    else:
        print(f"\n{errs} error(s), {total - errs} warning(s).")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
