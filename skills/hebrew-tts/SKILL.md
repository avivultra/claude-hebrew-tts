---
name: hebrew-tts
description: This skill should be used when the user asks Claude to read Hebrew text aloud — trigger phrases include "תקריא", "תקריא לי", "הקרא לי", "תגיד את זה בקול", "בקול", "read this aloud", "speak this in Hebrew". It generates natural-sounding Hebrew speech via Microsoft edge-tts neural voices (Avri male / Hila female) and plays the MP3 through the OS default audio handler. No API keys required. Works on Windows, macOS, and Linux.
version: 0.1.0
---

# Hebrew TTS Skill

Reads Hebrew (or any supported language) text aloud using Microsoft's free edge-tts neural voices.

## When to use this skill

Activate when the user requests spoken audio of text in Hebrew, including:
- **"תקריא"**, **"תקריא לי"**, **"תקריא את זה"**, **"תקריא את התשובה שלך"**
- **"בקול"**, **"תגיד את זה בקול"**, **"הקרא לי"**, **"הקרא בקול"**
- **"read this aloud"**, **"speak this"**, **"say this in Hebrew"**
- Any request to convert the most recent assistant message, or a specified piece of text, into audio

## What to do (step-by-step)

### 1. Decide *what* to read

- If the user quotes specific text ("תקריא לי: שלום עולם") — read exactly that text.
- If the user says "תקריא את זה" without specifying — read the **textual** content of the most recent substantive assistant message.
- Strip code blocks, URLs, file paths, markdown syntax (`**`, `##`, bullet markers), and technical identifiers before reading — they sound awful aloud. Convert structured lists into flowing Hebrew prose.
- Do NOT paraphrase or re-generate the text unless the user asks. Reading-aloud is a render step, not a rewrite.

### 2. Write text to a temp file (UTF-8)

**Always use a temp file with `--file`. Never pipe Hebrew via stdin on Windows** — the default cp1252 codec mangles Hebrew into surrogate errors.

```
Write tool → ${CLAUDE_PLUGIN_ROOT}/skills/hebrew-tts/scripts/_last.txt
Content: <the text to read, UTF-8>
```

### 3. Run speak.py via the plugin's venv

**Windows:**
```
"${CLAUDE_PLUGIN_ROOT}/skills/hebrew-tts/venv/Scripts/python.exe" "${CLAUDE_PLUGIN_ROOT}/skills/hebrew-tts/scripts/speak.py" --file "${CLAUDE_PLUGIN_ROOT}/skills/hebrew-tts/scripts/_last.txt"
```

**macOS / Linux:**
```
"${CLAUDE_PLUGIN_ROOT}/skills/hebrew-tts/venv/bin/python" "${CLAUDE_PLUGIN_ROOT}/skills/hebrew-tts/scripts/speak.py" --file "${CLAUDE_PLUGIN_ROOT}/skills/hebrew-tts/scripts/_last.txt"
```

`${CLAUDE_PLUGIN_ROOT}` is the installed plugin's root directory, injected by Claude Code at skill invocation.

The command returns immediately — the OS audio handler plays asynchronously.

### 4. If the venv is missing (first-time setup)

If `python.exe` (or `python`) at the venv path does not exist, the user needs to run the one-time setup:

**Windows:**
```
powershell -ExecutionPolicy Bypass -File "${CLAUDE_PLUGIN_ROOT}/skills/hebrew-tts/scripts/setup.ps1"
```

**macOS / Linux:**
```
bash "${CLAUDE_PLUGIN_ROOT}/skills/hebrew-tts/scripts/setup.sh"
```

Tell the user: *"הכלי צריך התקנה חד-פעמית (יוצר venv ומוריד edge-tts, כ-30 שניות). אריץ עכשיו?"* — and run setup only after confirmation.

## Optional flags

- `--voice hila` — female voice (he-IL-HilaNeural). Default is `avri` (male, he-IL-AvriNeural).
- `--rate "+60%"` (faster) / `--rate "+15%"` (slower than default) / `--rate "+0%"` (the raw neural-voice pace — feels slow) — speech rate override. Default is `+35%` (~1.35×), a comfortable conversational pace. Only override when the user explicitly asks ("יותר מהר" / "יותר לאט").
- `--save PATH.mp3` — save to file instead of playing.

## Style when confirming

After kicking off the command, respond briefly — one short line — acknowledging the audio is playing. Do NOT repeat the text that's being read (the user is listening to it). Example:

> מקריא עכשיו. (אם לא נשמע — תגיד ונאבחן.)

## Token-efficiency note

Reading a response costs ~80 extra tokens (one Write + one Bash). Do not hesitate to use this when asked. Do not duplicate the text into the chat — it's already in the response being read.
